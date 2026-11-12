#!/usr/bin/env python3
"""Generate structured repair actions from an LLM input packet."""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
sys.path.insert(0, str(Path(__file__).resolve().parent))

from jsonschema import Draft202012Validator

from llm_provider import (  # noqa: E402
    PROVIDERS,
    ProviderCallError,
    ProviderConfigError,
    ProviderResponseError,
    call_provider_with_metadata,
    load_api_key,
    run_config,
)
from repair_registry import (  # noqa: E402
    PROMPT_MODES,
    action_schema_for_pair,
    entries_for_profile,
    normalize_allowed_action_pair,
    pair_from_target_and_entry,
    value_schema_for_entry,
    unit_schema_for_entry,
    entry_for_parameter,
)


DEFAULT_INSTANCE_DIR = Path("instances/seed/distillation_002_reflux_ratio_single")
DEFAULT_LLM_INPUT = DEFAULT_INSTANCE_DIR / "public/llm_input.md"
DEFAULT_PARAMETERS = DEFAULT_INSTANCE_DIR / "public/parameters.json"
DEFAULT_OUTPUT = Path(".tmp/distillation_002_gemini_live/gemini_llm_output.json")
DEFAULT_PROMPT_OUTPUT = Path(".tmp/distillation_002_gemini_live/gemini_prompt.md")
DEFAULT_PROVIDER = "gemini"
DEFAULT_MODEL = "gemini-2.5-flash"
DEFAULT_ENV_FILE = Path(".env")
DEFAULT_REPAIR_ACTION_SCHEMA = Path("schemas/repair_action.schema.json")
COMMON_FORBIDDEN_PROMPT_PATTERNS = (
    "gold",
    "mock_llm_output",
    "metrics_report",
    "hidden/",
)
PARAMETER_FORBIDDEN_PROMPT_PATTERNS = {
    ("column_specification", "reflux_ratio"): (
        "7.501999",
        "change_reflux_ratio",
        "fault_reflux_ratio",
        "column_reflux_ratio_error",
    ),
    ("column_configuration", "feed_stage"): (
        "change_feed_stage",
        "fault_feed_stage",
        "column_feed_stage_error",
    ),
}
FORBIDDEN_PROMPT_PATTERNS = (
    *COMMON_FORBIDDEN_PROMPT_PATTERNS,
    "change_reflux_ratio",
    "change_feed_stage",
    "fault_reflux_ratio",
    "fault_feed_stage",
    "column_reflux_ratio_error",
    "column_feed_stage_error",
)
PARAMETER_SELECTION_FORBIDDEN_PROMPT_PATTERNS = (
    *COMMON_FORBIDDEN_PROMPT_PATTERNS,
    "target_parameter",
    "faulty target unit parameters",
    "adjust only reflux ratio",
    "adjust only the reflux ratio",
    "adjust only feed stage",
    "adjust only the feed stage",
    "distillation reflux-ratio repair",
    "distillation feed-stage repair",
    '"namespace": "column_specification"',
    '"name": "reflux_ratio"',
    '"namespace": "column_configuration"',
    '"name": "feed_stage"',
    '"namespace": "pressure_specification"',
    '"name": "outlet_pressure"',
    '"namespace": "thermal_specification"',
    '"name": "outlet_temperature"',
    '"namespace": "separator_specification"',
    '"name": "pressure"',
    '"name": "temperature"',
)


class LLMOutputValidationError(ValueError):
    """Provider returned JSON, but it failed the benchmark response schema."""


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig")


def sha256_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def sha256_json(data: Any) -> str:
    return sha256_text(json.dumps(data, sort_keys=True, separators=(",", ":")))


def metadata_record(
    *,
    dry_run: bool,
    provider: str,
    model: str,
    prompt_mode: str,
    prompt_hash: str,
    schema_hash: str,
    config: dict[str, Any],
    provider_metadata: dict[str, Any] | None = None,
    provider_error: dict[str, Any] | None = None,
    validation_error: str | None = None,
    validation_status: str | None = None,
) -> dict[str, Any]:
    return {
        "dry_run": dry_run,
        "provider": provider,
        "model": model,
        "prompt_mode": prompt_mode,
        "prompt_hash": prompt_hash,
        "schema_hash": schema_hash,
        "llm_run_config": config,
        "provider_metadata": provider_metadata,
        "provider_error": provider_error,
        "validation_error": validation_error,
        "validation_status": validation_status,
    }


def load_gemini_api_key(env_file: Path = DEFAULT_ENV_FILE) -> str:
    return load_api_key("gemini", env_file)


def strip_required_output_section(llm_input: str) -> str:
    lines = llm_input.splitlines()
    kept: list[str] = []
    for line in lines:
        if line.strip().lower() == "## required output":
            break
        kept.append(line)
    prompt = "\n".join(kept).strip()
    return (
        f"{prompt}\n\n"
        "Return only the structured repair action object requested by the API response schema. "
        "Do not include Markdown fences or explanatory prose outside the JSON object.\n"
    )


def forbidden_prompt_patterns(target_parameter: dict[str, str]) -> tuple[str, ...]:
    parameter_key = (target_parameter.get("namespace"), target_parameter.get("name"))
    return (
        *COMMON_FORBIDDEN_PROMPT_PATTERNS,
        *PARAMETER_FORBIDDEN_PROMPT_PATTERNS.get(parameter_key, ()),
    )


def assert_no_known_prompt_leaks(prompt: str, patterns: tuple[str, ...]) -> None:
    lowered = prompt.lower()
    found = [pattern for pattern in patterns if pattern.lower() in lowered]
    if found:
        raise ValueError(f"sanitized LLM prompt contains forbidden pattern(s): {', '.join(found)}")


def target_guid_from_parameters(parameters_path: Path) -> str:
    parameters = load_json(parameters_path)
    unit = parameters.get("target_unit") if isinstance(parameters, dict) else None
    guid = unit.get("guid") if isinstance(unit, dict) else None
    if isinstance(guid, str) and guid:
        return guid
    column = parameters.get("target_column") if isinstance(parameters, dict) else None
    guid = column.get("guid") if isinstance(column, dict) else None
    if not isinstance(guid, str) or not guid:
        raise ValueError(f"could not find target_column.guid in {parameters_path}")
    return guid


def target_parameter_from_parameters(parameters_path: Path) -> dict[str, str]:
    parameters = load_json(parameters_path)
    parameter = parameters.get("target_parameter") if isinstance(parameters, dict) else None
    if isinstance(parameter, dict):
        namespace = parameter.get("namespace")
        name = parameter.get("name")
        if isinstance(namespace, str) and isinstance(name, str):
            return {"namespace": namespace, "name": name}
    return {"namespace": "column_specification", "name": "reflux_ratio"}


def allowed_repair_actions_from_parameters(parameters_path: Path) -> list[dict[str, Any]]:
    parameters = load_json(parameters_path)
    raw_allowed = parameters.get("allowed_repair_actions") if isinstance(parameters, dict) else None
    if isinstance(raw_allowed, list) and raw_allowed:
        return [normalize_allowed_action_pair(pair) for pair in raw_allowed if isinstance(pair, dict)]

    target = None
    unit = parameters.get("target_unit") if isinstance(parameters, dict) else None
    column = parameters.get("target_column") if isinstance(parameters, dict) else None
    if isinstance(unit, dict) and isinstance(unit.get("guid"), str):
        target = unit
    elif isinstance(column, dict) and isinstance(column.get("guid"), str):
        target = column
    if not isinstance(target, dict) or not isinstance(target.get("guid"), str):
        raise ValueError(f"could not find allowed repair action target in {parameters_path}")
    return [pair_from_target_and_entry(target, entry) for entry in entries_for_profile("release")]


def value_schema_for_parameter(target_parameter: dict[str, str]) -> dict[str, Any]:
    return value_schema_for_entry(entry_for_parameter(target_parameter))


def unit_schema_for_parameter(target_parameter: dict[str, str]) -> dict[str, Any]:
    return unit_schema_for_entry(entry_for_parameter(target_parameter))


def action_schema_for_parameter(target_guid: str, parameter: dict[str, str]) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["type", "target", "parameter", "value", "unit"],
        "properties": {
            "type": {"type": "string", "enum": ["set_unit_parameter"]},
            "target": {
                "type": "object",
                "additionalProperties": False,
                "required": ["kind", "guid"],
                "properties": {
                    "kind": {"type": "string", "enum": ["unit_operation"]},
                    "guid": {"type": "string", "enum": [target_guid]},
                },
            },
            "parameter": {
                "type": "object",
                "additionalProperties": False,
                "required": ["namespace", "name"],
                "properties": {
                    "namespace": {"type": "string", "enum": [parameter["namespace"]]},
                    "name": {"type": "string", "enum": [parameter["name"]]},
                },
            },
            "value": value_schema_for_parameter(parameter),
            "unit": unit_schema_for_parameter(parameter),
            "rationale": {"type": "string"},
        },
    }


def gemini_action_item_schema(
    target_guid: str | None,
    prompt_mode: str,
    target_parameter: dict[str, str] | None,
    allowed_pairs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if prompt_mode == "oracle-parameter":
        if target_parameter is None:
            raise ValueError("target parameter is required for oracle-parameter mode")
        return action_schema_for_parameter(target_guid, target_parameter)
    if prompt_mode == "parameter-selection":
        pairs = allowed_pairs or []
        if len(pairs) < 2:
            raise ValueError("parameter-selection mode requires at least two allowed target-parameter pairs")
        return {"oneOf": [action_schema_for_pair(pair) for pair in pairs]}
    raise ValueError(f"unsupported prompt mode: {prompt_mode!r}")


def gemini_output_schema(
    target_guid: str | None,
    prompt_mode: str,
    target_parameter: dict[str, str] | None,
    allowed_pairs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    return {
        "type": "object",
        "additionalProperties": False,
        "required": ["diagnosis", "repair_actions", "rationale"],
        "properties": {
            "diagnosis": {"type": "string"},
            "rationale": {"type": "string"},
            "repair_actions": {
                "type": "array",
                "minItems": 1,
                "maxItems": 1,
                "items": gemini_action_item_schema(target_guid, prompt_mode, target_parameter, allowed_pairs),
            },
        },
    }


def validate_llm_payload(
    payload: Any,
    target_guid: str | None,
    prompt_mode: str,
    target_parameter: dict[str, str] | None,
    repair_action_schema_path: Path,
    allowed_pairs: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    if not isinstance(payload, dict):
        raise ValueError("LLM output must be a JSON object")

    structured_validator = Draft202012Validator(gemini_output_schema(target_guid, prompt_mode, target_parameter, allowed_pairs))
    structured_errors = sorted(structured_validator.iter_errors(payload), key=lambda error: list(error.absolute_path))
    if structured_errors:
        messages = []
        for error in structured_errors:
            location = ".".join(str(part) for part in error.absolute_path)
            prefix = location or "<root>"
            messages.append(f"{prefix}: {error.message}")
        raise ValueError("; ".join(messages))

    repair_action_schema = load_json(repair_action_schema_path)
    repair_action_validator = Draft202012Validator(repair_action_schema)
    repair_actions = payload.get("repair_actions")
    if not isinstance(repair_actions, list):
        raise ValueError("LLM output repair_actions must be an array")
    for index, action in enumerate(repair_actions):
        errors = sorted(repair_action_validator.iter_errors(action), key=lambda error: list(error.absolute_path))
        if errors:
            messages = []
            for error in errors:
                location = ".".join(str(part) for part in error.absolute_path)
                prefix = f"repair_actions[{index}]"
                if location:
                    prefix = f"{prefix}.{location}"
                messages.append(f"{prefix}: {error.message}")
            raise ValueError("; ".join(messages))

    return payload


validate_gemini_payload = validate_llm_payload


def generate_llm_output(
    llm_input_path: Path = DEFAULT_LLM_INPUT,
    output_path: Path = DEFAULT_OUTPUT,
    parameters_path: Path = DEFAULT_PARAMETERS,
    model: str = DEFAULT_MODEL,
    env_file: Path = DEFAULT_ENV_FILE,
    repair_action_schema_path: Path = DEFAULT_REPAIR_ACTION_SCHEMA,
    dry_run_sanitize: bool = False,
    sanitized_prompt_output: Path = DEFAULT_PROMPT_OUTPUT,
    prompt_mode: str = "oracle-parameter",
    provider: str = DEFAULT_PROVIDER,
    metadata_output: Path | None = None,
) -> dict[str, Any]:
    if provider not in PROVIDERS:
        raise ValueError(f"unsupported provider: {provider!r}")
    if prompt_mode not in PROMPT_MODES:
        raise ValueError(f"unsupported prompt mode: {prompt_mode!r}")
    if prompt_mode == "oracle-parameter":
        target_guid: str | None = target_guid_from_parameters(parameters_path)
        target_parameter = target_parameter_from_parameters(parameters_path)
        allowed_pairs = None
    else:
        target_guid = None
        target_parameter = None
        allowed_pairs = allowed_repair_actions_from_parameters(parameters_path)
    prompt = strip_required_output_section(read_text(llm_input_path))
    prompt_patterns = (
        forbidden_prompt_patterns(target_parameter)
        if prompt_mode == "oracle-parameter" and target_parameter is not None
        else PARAMETER_SELECTION_FORBIDDEN_PROMPT_PATTERNS
    )
    assert_no_known_prompt_leaks(prompt, prompt_patterns)
    schema = gemini_output_schema(target_guid, prompt_mode, target_parameter, allowed_pairs)
    prompt_hash = sha256_text(prompt)
    schema_hash = sha256_json(schema)
    config = run_config(provider, model, prompt_mode)

    if dry_run_sanitize:
        sanitized_prompt_output.parent.mkdir(parents=True, exist_ok=True)
        sanitized_prompt_output.write_text(prompt, encoding="utf-8")
        result = {
            "dry_run": True,
            "provider": provider,
            "model": model,
            "prompt_mode": prompt_mode,
            "llm_run_config": config,
            "sanitized_prompt_output": str(sanitized_prompt_output),
            "prompt_hash": prompt_hash,
            "schema_hash": schema_hash,
        }
        if target_parameter is not None:
            result["target_guid"] = target_guid
            result["target_parameter"] = target_parameter
        else:
            result["allowed_repair_actions"] = allowed_pairs
        if metadata_output is not None:
            write_json(
                metadata_output,
                metadata_record(
                    dry_run=True,
                    provider=provider,
                    model=model,
                    prompt_mode=prompt_mode,
                    prompt_hash=prompt_hash,
                    schema_hash=schema_hash,
                    config=config,
                    validation_status="dry_run",
                ),
            )
        return result

    try:
        api_key = load_api_key(provider, env_file)
    except ProviderConfigError as exc:
        if metadata_output is not None:
            write_json(
                metadata_output,
                metadata_record(
                    dry_run=False,
                    provider=provider,
                    model=model,
                    prompt_mode=prompt_mode,
                    prompt_hash=prompt_hash,
                    schema_hash=schema_hash,
                    config=config,
                    provider_error={"type": "provider_config", "message": str(exc)},
                    validation_status="not_reached",
                ),
            )
        raise
    try:
        provider_result = call_provider_with_metadata(provider, prompt, schema, model, api_key)
    except ProviderCallError as exc:
        if metadata_output is not None:
            write_json(
                metadata_output,
                metadata_record(
                    dry_run=False,
                    provider=provider,
                    model=model,
                    prompt_mode=prompt_mode,
                    prompt_hash=prompt_hash,
                    schema_hash=schema_hash,
                    config=config,
                    provider_error={"type": "provider_call", "message": str(exc)},
                    validation_status="not_reached",
                ),
            )
        raise
    except ProviderResponseError as exc:
        if metadata_output is not None:
            write_json(
                metadata_output,
                metadata_record(
                    dry_run=False,
                    provider=provider,
                    model=model,
                    prompt_mode=prompt_mode,
                    prompt_hash=prompt_hash,
                    schema_hash=schema_hash,
                    config=config,
                    provider_metadata=exc.metadata,
                    provider_error={"type": "provider_response", "message": str(exc)},
                    validation_status="not_reached",
                ),
            )
        raise
    payload = provider_result["payload"]
    if metadata_output is not None:
        write_json(
            metadata_output,
            metadata_record(
                dry_run=False,
                provider=provider,
                model=model,
                prompt_mode=prompt_mode,
                prompt_hash=prompt_hash,
                schema_hash=schema_hash,
                config=config,
                provider_metadata=provider_result.get("metadata"),
                validation_status="pending",
            ),
        )
    try:
        normalized = validate_llm_payload(payload, target_guid, prompt_mode, target_parameter, repair_action_schema_path, allowed_pairs)
    except Exception as exc:  # noqa: BLE001
        if metadata_output is not None:
            write_json(
                metadata_output,
                metadata_record(
                    dry_run=False,
                    provider=provider,
                    model=model,
                    prompt_mode=prompt_mode,
                    prompt_hash=prompt_hash,
                    schema_hash=schema_hash,
                    config=config,
                    provider_metadata=provider_result.get("metadata"),
                    validation_error=str(exc),
                    validation_status="schema_invalid",
                ),
            )
        raise LLMOutputValidationError(str(exc)) from exc
    write_json(output_path, normalized)
    if metadata_output is not None:
        write_json(
            metadata_output,
            metadata_record(
                dry_run=False,
                provider=provider,
                model=model,
                prompt_mode=prompt_mode,
                prompt_hash=prompt_hash,
                schema_hash=schema_hash,
                config=config,
                provider_metadata=provider_result.get("metadata"),
                validation_status="valid",
            ),
        )
    return normalized


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--llm-input", default=DEFAULT_LLM_INPUT, type=Path)
    parser.add_argument("--output", default=DEFAULT_OUTPUT, type=Path)
    parser.add_argument("--parameters", default=DEFAULT_PARAMETERS, type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default=DEFAULT_PROVIDER)
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE, type=Path)
    parser.add_argument("--repair-action-schema", default=DEFAULT_REPAIR_ACTION_SCHEMA, type=Path)
    parser.add_argument("--dry-run-sanitize", action="store_true")
    parser.add_argument("--sanitized-prompt-output", default=DEFAULT_PROMPT_OUTPUT, type=Path)
    parser.add_argument("--prompt-mode", choices=sorted(PROMPT_MODES), default="oracle-parameter")
    parser.add_argument("--metadata-output", type=Path)
    args = parser.parse_args()

    try:
        result = generate_llm_output(
            llm_input_path=args.llm_input,
            output_path=args.output,
            parameters_path=args.parameters,
            model=args.model,
            env_file=args.env_file,
            repair_action_schema_path=args.repair_action_schema,
            dry_run_sanitize=args.dry_run_sanitize,
            sanitized_prompt_output=args.sanitized_prompt_output,
            prompt_mode=args.prompt_mode,
            provider=args.provider,
            metadata_output=args.metadata_output,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    if args.dry_run_sanitize:
        print(f"Wrote sanitized {args.provider} prompt to {result['sanitized_prompt_output']}")
    else:
        print(f"Wrote {args.provider} LLM output to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
