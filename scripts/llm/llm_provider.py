#!/usr/bin/env python3
"""Small provider interface for live structured LLM repair outputs."""

from __future__ import annotations

import copy
import json
import os
import time
import urllib.error
import urllib.request
from pathlib import Path
from typing import Any


PROVIDERS = {"gemini", "openai", "anthropic"}
ENV_VAR_BY_PROVIDER = {
    "gemini": "GEMINI_API_KEY",
    "openai": "OPENAI_API_KEY",
    "anthropic": "CLAUDE_API_KEY",
}
OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"
ANTHROPIC_MESSAGES_URL = "https://api.anthropic.com/v1/messages"
ANTHROPIC_VERSION = "2023-06-01"
API_RETRY_MAX = 0
TEMPERATURE = 0.0
ANTHROPIC_MAX_TOKENS = 4096
PROVIDER_SCHEMA_VARIANT = {
    "gemini": "canonical",
    "openai": "openai_strict_required_properties",
    "anthropic": "anthropic_relaxed_no_maxItems_no_oneOf",
}


class ProviderCallError(RuntimeError):
    """Provider API/network call failed before a model output could be parsed."""


class ProviderConfigError(RuntimeError):
    """Provider configuration is missing or invalid before an API call starts."""


class ProviderResponseError(ValueError):
    """Provider returned a response, but no usable structured payload was parsed."""

    def __init__(self, message: str, metadata: dict[str, Any] | None = None) -> None:
        super().__init__(message)
        self.metadata = metadata or {}


def setting_record(
    *,
    configurable: bool,
    requested: Any = None,
    effective: Any = None,
    availability: str,
    provider_default: bool = False,
) -> dict[str, Any]:
    return {
        "configurable": configurable,
        "requested": requested,
        "effective": effective,
        "availability": availability,
        "provider_default": provider_default,
    }


def provider_capabilities(provider: str) -> dict[str, Any]:
    provider = normalize_provider(provider)
    common = {
        "api_retry": {
            "support": "benchmark_controlled",
            "configured_max": API_RETRY_MAX,
            "notes": "The v0.1.5 runner does not retry provider calls.",
        },
        "raw_metadata": {
            "support": "partial",
            "notes": "The adapter preserves documented response fields and selected transport headers when exposed.",
        },
    }
    if provider == "gemini":
        return {
            **common,
            "temperature": {"support": "supported", "effective_value": "not_exposed"},
            "top_p": {"support": "supported", "effective_value": "not_exposed"},
            "max_output_tokens": {"support": "supported", "effective_value": "not_exposed"},
            "reasoning_or_thinking": {
                "support": "supported",
                "field": "thinkingConfig",
                "effective_value": "not_exposed_when_not_requested",
            },
            "structured_output_mode": {
                "support": "supported",
                "mode": "response_mime_type=application/json + response_json_schema",
            },
            "response_schema_strictness": {
                "support": "schema_subset",
                "notes": "Gemini structured outputs use a supported subset of JSON Schema; no separate strict flag is set.",
            },
            "request_id": {"support": "not_exposed_by_current_adapter"},
            "response_id": {"support": "best_effort"},
            "finish_reason": {"support": "supported"},
            "token_usage": {"support": "supported", "field": "usage_metadata"},
            "latency": {"support": "benchmark_measured"},
        }
    if provider == "openai":
        return {
            **common,
            "temperature": {"support": "supported", "effective_value": "not_exposed_when_not_requested"},
            "top_p": {"support": "supported", "effective_value": "not_exposed_when_not_requested"},
            "max_output_tokens": {"support": "supported", "effective_value": "exposed_on_response"},
            "reasoning_or_thinking": {
                "support": "supported",
                "field": "reasoning",
                "effective_value": "partially_exposed_on_response",
            },
            "structured_output_mode": {
                "support": "supported",
                "mode": "Responses API text.format=json_schema strict=true",
            },
            "response_schema_strictness": {
                "support": "supported",
                "requested": "strict=true",
            },
            "request_id": {"support": "best_effort_header"},
            "response_id": {"support": "supported", "field": "id"},
            "finish_reason": {
                "support": "status_and_incomplete_details",
                "notes": "Responses API exposes response status/incomplete_details rather than a Chat Completions finish_reason.",
            },
            "token_usage": {"support": "supported", "field": "usage"},
            "latency": {"support": "benchmark_measured"},
        }
    if provider == "anthropic":
        return {
            **common,
            "temperature": {
                "support": "model_dependent",
                "notes": "Requested as 0.0 only for Claude models that support temperature; newer models that reject temperature run provider default and are marked unsupported_by_model.",
            },
            "top_p": {
                "support": "model_dependent",
                "notes": "v0.1.5 does not request top_p; newer Claude models may reject non-default top_p.",
            },
            "max_output_tokens": {
                "support": "required",
                "requested": ANTHROPIC_MAX_TOKENS,
                "field": "max_tokens",
            },
            "reasoning_or_thinking": {
                "support": "supported",
                "field": "effort",
                "effective_value": "provider_default",
                "notes": "Claude effort is not requested. Opus 4.8 provider default is documented as high.",
            },
            "structured_output_mode": {
                "support": "supported",
                "mode": "Messages API output_config.format=json_schema",
            },
            "response_schema_strictness": {
                "support": "structured_output",
                "notes": "JSON schema is compiled into a constrained grammar; local canonical validation still runs after provider output.",
            },
            "request_id": {"support": "best_effort_header"},
            "response_id": {"support": "supported", "field": "id"},
            "finish_reason": {"support": "supported", "field": "stop_reason"},
            "token_usage": {"support": "supported", "field": "usage"},
            "latency": {"support": "benchmark_measured"},
        }
    raise AssertionError(f"unreachable provider capability dispatch: {provider}")


def normalize_provider(provider: str) -> str:
    normalized = provider.strip().lower()
    if normalized not in PROVIDERS:
        raise ValueError(f"unsupported LLM provider: {provider!r}")
    return normalized


def parse_env_value(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        return value[1:-1]
    return value


def read_api_key_from_env_file(env_file: Path, env_var: str) -> str | None:
    if not env_file.exists():
        return None
    for line in env_file.read_text(encoding="utf-8-sig").splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        key, value = stripped.split("=", 1)
        if key.strip() == env_var:
            parsed = parse_env_value(value)
            return parsed or None
    return None


def load_api_key(provider: str, env_file: Path) -> str:
    provider = normalize_provider(provider)
    env_var = ENV_VAR_BY_PROVIDER[provider]
    existing = os.environ.get(env_var)
    if existing:
        return existing
    from_file = read_api_key_from_env_file(env_file, env_var)
    if from_file:
        return from_file
    raise ProviderConfigError(f"{env_var} is not set in the environment or the configured .env file")


def supports_temperature(provider: str, model: str) -> bool:
    provider = normalize_provider(provider)
    model = model.strip().lower()
    if provider == "openai":
        unsupported_prefixes = (
            "gpt-5.5",
        )
        return not model.startswith(unsupported_prefixes)
    if provider != "anthropic":
        return True
    unsupported_prefixes = (
        "claude-opus-4-8",
        "claude-sonnet-4-6",
        "claude-mythos",
    )
    return not model.startswith(unsupported_prefixes)


def temperature_setting(provider: str, model: str) -> dict[str, Any]:
    if supports_temperature(provider, model):
        return setting_record(
            configurable=True,
            requested=TEMPERATURE,
            effective=TEMPERATURE,
            availability="configured",
            provider_default=False,
        )
    return setting_record(
        configurable=False,
        requested=None,
        effective=None,
        availability="unsupported_by_model",
        provider_default=True,
    )


def requested_temperature(provider: str, model: str) -> float | None:
    return TEMPERATURE if supports_temperature(provider, model) else None


def structured_output_mode(provider: str) -> str:
    provider = normalize_provider(provider)
    if provider == "gemini":
        return "response_mime_type=application/json + response_json_schema"
    if provider == "openai":
        return "Responses API text.format=json_schema strict=true"
    if provider == "anthropic":
        return "Messages API output_config.format=json_schema"
    raise AssertionError(f"unreachable structured output mode dispatch: {provider}")


def provider_schema_variant(provider: str) -> str:
    return PROVIDER_SCHEMA_VARIANT[normalize_provider(provider)]


def run_config(provider: str, model: str, prompt_mode: str) -> dict[str, Any]:
    provider = normalize_provider(provider)
    strictness = "strict=true" if provider == "openai" else "schema_subset"
    if provider == "anthropic":
        strictness = "compiled_json_schema"
    generation_settings = {
        "temperature": temperature_setting(provider, model),
        "top_p": setting_record(
            configurable=True,
            requested=None,
            effective=None,
            availability="provider_default",
            provider_default=True,
        ),
        "max_output_tokens": setting_record(
            configurable=True,
            requested=ANTHROPIC_MAX_TOKENS if provider == "anthropic" else None,
            effective=ANTHROPIC_MAX_TOKENS if provider == "anthropic" else None,
            availability="configured" if provider == "anthropic" else "provider_default",
            provider_default=provider != "anthropic",
        ),
        "reasoning_or_thinking": setting_record(
            configurable=True,
            requested=None,
            effective=None,
            availability="provider_default",
            provider_default=True,
        ),
        "structured_output": setting_record(
            configurable=True,
            requested=True,
            effective=True,
            availability="configured",
            provider_default=False,
        ),
        "response_schema_strictness": setting_record(
            configurable=provider in {"openai", "anthropic"},
            requested=strictness,
            effective=strictness,
            availability="configured",
            provider_default=False,
        ),
    }
    return {
        "provider": provider,
        "model": model,
        "prompt_mode": prompt_mode,
        "generation_settings": generation_settings,
        "provider_capabilities": provider_capabilities(provider),
        "structured_output_mode": structured_output_mode(provider),
        "provider_schema_variant": provider_schema_variant(provider),
        "api_retry_max": API_RETRY_MAX,
        "model_output_retry": False,
        "simulator_retry": False,
        # Backward-compatible flat fields used by earlier result notes.
        "temperature": requested_temperature(provider, model),
        "thinking": "provider_default",
        "structured_output": True,
    }


def openai_strict_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Convert benchmark JSON Schema into OpenAI strict Structured Outputs shape."""
    return _openai_schema_node(copy.deepcopy(schema))


def anthropic_schema(schema: dict[str, Any]) -> dict[str, Any]:
    """Convert benchmark JSON Schema into Anthropic structured-output shape."""
    return _anthropic_schema_node(copy.deepcopy(schema))


def _openai_schema_node(node: Any) -> Any:
    if isinstance(node, list):
        return [_openai_schema_node(item) for item in node]
    if not isinstance(node, dict):
        return node

    converted: dict[str, Any] = {}
    for key, value in node.items():
        if key == "oneOf":
            converted["anyOf"] = _openai_schema_node(value)
        else:
            converted[key] = _openai_schema_node(value)

    if converted.get("type") == "object" or isinstance(converted.get("properties"), dict):
        properties = converted.get("properties")
        if isinstance(properties, dict):
            converted["required"] = list(properties.keys())
        converted["additionalProperties"] = False

    return converted


def _anthropic_schema_node(node: Any) -> Any:
    if isinstance(node, list):
        return [_anthropic_schema_node(item) for item in node]
    if not isinstance(node, dict):
        return node
    if isinstance(node.get("oneOf"), list):
        return anthropic_loose_action_schema(node["oneOf"])
    converted: dict[str, Any] = {}
    for key, value in node.items():
        if key == "maxItems":
            continue
        converted[key] = _anthropic_schema_node(value)
    return converted


def nested_enum_values(node: Any, path: tuple[str, ...]) -> list[Any]:
    current = node
    for key in path:
        if not isinstance(current, dict):
            return []
        current = current.get(key)
    if not isinstance(current, dict):
        return []
    if "const" in current:
        return [current["const"]]
    values = current.get("enum")
    return values if isinstance(values, list) else []


def unique_values(values: list[Any]) -> list[Any]:
    result: list[Any] = []
    for value in values:
        if value not in result:
            result.append(value)
    return result


def anthropic_loose_action_schema(options: list[Any]) -> dict[str, Any]:
    targets: list[Any] = []
    namespaces: list[Any] = []
    names: list[Any] = []
    units: list[Any] = []
    for option in options:
        if not isinstance(option, dict):
            continue
        properties = option.get("properties") if isinstance(option.get("properties"), dict) else {}
        targets.extend(nested_enum_values(properties, ("target", "properties", "guid")))
        namespaces.extend(nested_enum_values(properties, ("parameter", "properties", "namespace")))
        names.extend(nested_enum_values(properties, ("parameter", "properties", "name")))
        units.extend(nested_enum_values(properties, ("unit",)))
    unit_values = unique_values(units)
    unit_schema: dict[str, Any]
    if unit_values:
        unit_schema = {"enum": unit_values}
    else:
        unit_schema = {"type": ["string", "null"]}
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["type", "target", "parameter", "value", "unit"],
        "properties": {
            "type": {"enum": ["set_unit_parameter"]},
            "target": {
                "type": "object",
                "additionalProperties": False,
                "required": ["kind", "guid"],
                "properties": {
                    "kind": {"enum": ["unit_operation"]},
                    "guid": {"enum": unique_values(targets)} if targets else {"type": "string"},
                    "tag": {"type": "string"},
                },
            },
            "parameter": {
                "type": "object",
                "additionalProperties": False,
                "required": ["namespace", "name"],
                "properties": {
                    "namespace": {"enum": unique_values(namespaces)} if namespaces else {"type": "string"},
                    "name": {"enum": unique_values(names)} if names else {"type": "string"},
                },
            },
            "value": {"type": "number"},
            "unit": unit_schema,
            "rationale": {"type": "string"},
        },
    }


def call_provider(provider: str, prompt: str, schema: dict[str, Any], model: str, api_key: str) -> dict[str, Any]:
    return call_provider_with_metadata(provider, prompt, schema, model, api_key)["payload"]


def call_provider_with_metadata(
    provider: str,
    prompt: str,
    schema: dict[str, Any],
    model: str,
    api_key: str,
) -> dict[str, Any]:
    provider = normalize_provider(provider)
    if provider == "gemini":
        return call_gemini_with_metadata(prompt, schema, model, api_key)
    if provider == "openai":
        return call_openai_responses_with_metadata(prompt, schema, model, api_key)
    if provider == "anthropic":
        return call_anthropic_messages_with_metadata(prompt, schema, model, api_key)
    raise AssertionError(f"unreachable provider dispatch: {provider}")


def parse_gemini_response(response: Any) -> Any:
    parsed = getattr(response, "parsed", None)
    if isinstance(parsed, dict):
        return parsed
    text = getattr(response, "text", None)
    if not isinstance(text, str) or not text.strip():
        raise ValueError("Gemini response did not contain text JSON")
    return json.loads(text)


def call_gemini(prompt: str, schema: dict[str, Any], model: str, api_key: str) -> dict[str, Any]:
    return call_gemini_with_metadata(prompt, schema, model, api_key)["payload"]


def safe_json_value(value: Any) -> Any:
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, dict):
        return {str(key): safe_json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [safe_json_value(item) for item in value]
    to_dict = getattr(value, "to_dict", None)
    if callable(to_dict):
        try:
            return safe_json_value(to_dict())
        except Exception:  # noqa: BLE001
            pass
    model_dump = getattr(value, "model_dump", None)
    if callable(model_dump):
        try:
            return safe_json_value(model_dump())
        except Exception:  # noqa: BLE001
            pass
    return str(value)


def first_gemini_candidate(response: Any) -> Any | None:
    candidates = getattr(response, "candidates", None)
    if isinstance(candidates, list) and candidates:
        return candidates[0]
    return None


def gemini_response_metadata(response: Any, model: str, latency_sec: float) -> dict[str, Any]:
    candidate = first_gemini_candidate(response)
    finish_reason = getattr(candidate, "finish_reason", None) if candidate is not None else None
    usage = getattr(response, "usage_metadata", None)
    return {
        "provider": "gemini",
        "model": model,
        "request_id": None,
        "response_id": safe_json_value(getattr(response, "response_id", None)),
        "model_version": safe_json_value(getattr(response, "model_version", None)),
        "status": None,
        "finish_reason": safe_json_value(finish_reason),
        "usage": safe_json_value(usage),
        "latency_sec": latency_sec,
        "api_retry_count": 0,
        "structured_output_mode": "response_mime_type=application/json + response_json_schema",
        "raw_metadata_availability": {
            "request_id": "not_exposed",
            "response_id": "best_effort",
            "finish_reason": "available_if_candidates_exposed",
            "usage": "available_if_usage_metadata_exposed",
        },
    }


def call_gemini_with_metadata(prompt: str, schema: dict[str, Any], model: str, api_key: str) -> dict[str, Any]:
    try:
        from google import genai
    except ImportError as exc:  # pragma: no cover - depends on optional live dependency.
        raise RuntimeError("missing dependency 'google-genai'. Install with: pip install -r requirements.txt") from exc

    client = genai.Client(api_key=api_key)
    try:
        started = time.perf_counter()
        try:
            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_json_schema": schema,
                    "temperature": TEMPERATURE,
                },
            )
        except Exception as exc:  # noqa: BLE001
            raise ProviderCallError(f"Gemini API request failed: {exc}") from exc
        latency_sec = time.perf_counter() - started
        metadata = gemini_response_metadata(response, model, latency_sec)
        try:
            payload = parse_gemini_response(response)
        except Exception as exc:  # noqa: BLE001
            raise ProviderResponseError(f"Gemini response did not contain valid JSON: {exc}", metadata) from exc
    finally:
        close = getattr(client, "close", None)
        if callable(close):
            close()

    if not isinstance(payload, dict):
        raise ProviderResponseError("Gemini structured response was not a JSON object", metadata)
    return {"payload": payload, "metadata": metadata}


def call_openai_responses(prompt: str, schema: dict[str, Any], model: str, api_key: str) -> dict[str, Any]:
    return call_openai_responses_with_metadata(prompt, schema, model, api_key)["payload"]


def call_openai_responses_with_metadata(prompt: str, schema: dict[str, Any], model: str, api_key: str) -> dict[str, Any]:
    body = {
        "model": model,
        "input": [{"role": "user", "content": prompt}],
        "text": {
            "format": {
                "type": "json_schema",
                "name": "repair_output",
                "schema": openai_strict_schema(schema),
                "strict": True,
            }
        },
    }
    temperature = requested_temperature("openai", model)
    if temperature is not None:
        body["temperature"] = temperature
    request = urllib.request.Request(
        OPENAI_RESPONSES_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        started = time.perf_counter()
        with urllib.request.urlopen(request, timeout=180) as response:
            headers = dict(response.headers.items())
            response_data = json.loads(response.read().decode("utf-8"))
            latency_sec = time.perf_counter() - started
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProviderCallError(f"OpenAI Responses API error {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ProviderCallError(f"OpenAI Responses API request failed: {exc}") from exc

    metadata = openai_response_metadata(response_data, headers, model, latency_sec)
    try:
        text = first_response_text(response_data)
    except Exception as exc:  # noqa: BLE001
        raise ProviderResponseError(f"OpenAI response did not contain output text: {exc}", metadata) from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderResponseError(f"OpenAI response did not contain JSON text: {text[:500]}", metadata) from exc
    if not isinstance(payload, dict):
        raise ProviderResponseError("OpenAI structured response was not a JSON object", metadata)
    return {
        "payload": payload,
        "metadata": metadata,
    }


def call_anthropic_messages(prompt: str, schema: dict[str, Any], model: str, api_key: str) -> dict[str, Any]:
    return call_anthropic_messages_with_metadata(prompt, schema, model, api_key)["payload"]


def call_anthropic_messages_with_metadata(prompt: str, schema: dict[str, Any], model: str, api_key: str) -> dict[str, Any]:
    body: dict[str, Any] = {
        "model": model,
        "max_tokens": ANTHROPIC_MAX_TOKENS,
        "messages": [{"role": "user", "content": prompt}],
        "output_config": {
            "format": {
                "type": "json_schema",
                "schema": anthropic_schema(schema),
            }
        },
    }
    temperature = requested_temperature("anthropic", model)
    if temperature is not None:
        body["temperature"] = temperature
    request = urllib.request.Request(
        ANTHROPIC_MESSAGES_URL,
        data=json.dumps(body).encode("utf-8"),
        headers={
            "x-api-key": api_key,
            "anthropic-version": ANTHROPIC_VERSION,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        started = time.perf_counter()
        with urllib.request.urlopen(request, timeout=180) as response:
            headers = dict(response.headers.items())
            response_data = json.loads(response.read().decode("utf-8"))
            latency_sec = time.perf_counter() - started
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise ProviderCallError(f"Anthropic Messages API error {exc.code}: {detail}") from exc
    except urllib.error.URLError as exc:
        raise ProviderCallError(f"Anthropic Messages API request failed: {exc}") from exc

    metadata = anthropic_response_metadata(response_data, headers, model, latency_sec)
    try:
        text = first_anthropic_response_text(response_data)
    except Exception as exc:  # noqa: BLE001
        raise ProviderResponseError(f"Anthropic response did not contain output text: {exc}", metadata) from exc
    try:
        payload = json.loads(text)
    except json.JSONDecodeError as exc:
        raise ProviderResponseError(f"Anthropic response did not contain JSON text: {text[:500]}", metadata) from exc
    if not isinstance(payload, dict):
        raise ProviderResponseError("Anthropic structured response was not a JSON object", metadata)
    return {"payload": payload, "metadata": metadata}


def header_value(headers: dict[str, Any], *names: str) -> str | None:
    lowered = {str(key).lower(): str(value) for key, value in headers.items()}
    for name in names:
        value = lowered.get(name.lower())
        if value:
            return value
    return None


def openai_response_metadata(
    response_data: dict[str, Any],
    headers: dict[str, Any],
    model: str,
    latency_sec: float,
) -> dict[str, Any]:
    return {
        "provider": "openai",
        "model": response_data.get("model") or model,
        "request_id": header_value(headers, "x-request-id", "request-id", "openai-request-id"),
        "response_id": response_data.get("id"),
        "model_version": response_data.get("model") or model,
        "status": response_data.get("status"),
        "finish_reason": None,
        "incomplete_details": safe_json_value(response_data.get("incomplete_details")),
        "usage": safe_json_value(response_data.get("usage")),
        "latency_sec": latency_sec,
        "api_retry_count": 0,
        "structured_output_mode": "Responses API text.format=json_schema strict=true",
        "raw_metadata_availability": {
            "request_id": "best_effort_header",
            "response_id": "available",
            "finish_reason": "not_exposed",
            "status": "available",
            "usage": "available",
        },
    }


def anthropic_response_metadata(
    response_data: dict[str, Any],
    headers: dict[str, Any],
    model: str,
    latency_sec: float,
) -> dict[str, Any]:
    return {
        "provider": "anthropic",
        "model": response_data.get("model") or model,
        "request_id": header_value(headers, "request-id", "x-request-id", "anthropic-request-id"),
        "response_id": response_data.get("id"),
        "model_version": response_data.get("model") or model,
        "status": response_data.get("type"),
        "finish_reason": response_data.get("stop_reason"),
        "stop_sequence": response_data.get("stop_sequence"),
        "usage": safe_json_value(response_data.get("usage")),
        "latency_sec": latency_sec,
        "api_retry_count": 0,
        "structured_output_mode": "Messages API output_config.format=json_schema",
        "raw_metadata_availability": {
            "request_id": "best_effort_header",
            "response_id": "available",
            "finish_reason": "available_as_stop_reason",
            "usage": "available",
        },
    }


def first_response_text(response_data: Any) -> str:
    if isinstance(response_data, dict):
        output_text = response_data.get("output_text")
        if isinstance(output_text, str) and output_text.strip():
            return output_text
    for text in iter_response_text(response_data):
        if text.strip():
            return text
    raise ValueError("OpenAI response did not contain output text")


def first_anthropic_response_text(response_data: Any) -> str:
    if isinstance(response_data, dict):
        content = response_data.get("content")
        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                text = block.get("text")
                if isinstance(text, str) and text.strip():
                    return text
    raise ValueError("Anthropic response did not contain content text")


def iter_response_text(value: Any) -> Any:
    if isinstance(value, list):
        for item in value:
            yield from iter_response_text(item)
        return
    if not isinstance(value, dict):
        return

    item_type = value.get("type")
    text = value.get("text")
    if item_type in {"output_text", "text"} and isinstance(text, str):
        yield text
    for key in ("output", "content"):
        nested = value.get(key)
        if isinstance(nested, (list, dict)):
            yield from iter_response_text(nested)
