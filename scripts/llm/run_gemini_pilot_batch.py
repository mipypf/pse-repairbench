#!/usr/bin/env python3
"""Run live LLM repair generation and evaluation across a pilot instance set."""

from __future__ import annotations

import argparse
import csv
import hashlib
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluate"))

from evaluate_repair_output import evaluate, write_json  # noqa: E402
from generate_llm_input import generate as generate_llm_input_packet  # noqa: E402
from generate_llm_output import (  # noqa: E402
    DEFAULT_ENV_FILE,
    DEFAULT_MODEL,
    DEFAULT_PROVIDER,
    PROMPT_MODES,
    LLMOutputValidationError,
    generate_llm_output,
    load_json,
)
from llm_provider import PROVIDERS, ProviderCallError, ProviderConfigError, ProviderResponseError, run_config  # noqa: E402


DEFAULT_WORK_DIR = Path(".tmp/live_runs/llm_pilot")
ROW_FIELDS = [
    "instance_id",
    "instance_path",
    "source_category",
    "target_family",
    "provider",
    "model",
    "prompt_mode",
    "omit_simulator_log",
    "llm_output",
    "llm_metadata",
    "sanitized_prompt",
    "evaluation_report",
    "dataset_split_id",
    "git_commit",
    "prompt_hash",
    "schema_hash",
    "api_retry_max",
    "provider_call_delay_sec",
    "model_output_retry",
    "simulator_retry",
    "structured_output_mode",
    "provider_schema_variant",
    "provider_request_id",
    "provider_response_id",
    "provider_model_version",
    "provider_status",
    "provider_finish_reason",
    "provider_latency_sec",
    "provider_api_retry_count",
    "provider_usage_input_tokens",
    "provider_usage_output_tokens",
    "provider_usage_total_tokens",
    "provider_error_type",
    "provider_error_message",
    "validation_status",
    "validation_error",
    "schema_valid",
    "action_schema_valid",
    "executor_success",
    "dwsim_success",
    "executor_timed_out",
    "dwsim_timed_out",
    "executor_timeout_sec",
    "dwsim_timeout_sec",
    "pipeline_success",
    "executable_success",
    "criteria_converged",
    "criteria_no_fatal_error",
    "criteria_target_metric",
    "target_value",
    "target_direction",
    "target_threshold",
    "target_stream_tag",
    "target_stream_id",
    "target_stream_role",
    "target_metric_name",
    "target_component",
    "target_match",
    "parameter_match",
    "unit_match",
    "value_abs_error",
    "value_rel_error",
    "selected_value",
    "selected_unit",
    "gold_value",
    "gold_unit",
    "selected_parameter",
    "gold_parameter",
    "selected_target",
    "gold_target",
    "selected_target_guid",
    "selected_target_tag",
    "gold_target_guid",
    "gold_target_tag",
    "selected_action_pair",
    "gold_action_pair",
    "selected_action_pair_key",
    "gold_action_pair_key",
    "gold_proximity_type",
    "gold_mismatch_success_type",
    "failure_type",
    "error_stage",
    "error",
]


def collect_instance_paths(paths: list[Path]) -> list[Path]:
    instances: list[Path] = []
    for path in paths:
        if path.is_dir():
            instances.extend(sorted(path.rglob("instance.json")))
        else:
            instances.append(path)
    return sorted(dict.fromkeys(instances))


def instance_ref(instance_path: Path, ref: str) -> Path:
    return instance_path.parent / ref


def instance_id(instance_path: Path, instance: Any | None = None) -> str:
    if isinstance(instance, dict) and isinstance(instance.get("id"), str) and instance["id"]:
        return instance["id"]
    return instance_path.parent.name


def instance_work_dir(root: Path, instance_path: Path, instance: Any | None = None) -> Path:
    identity = f"{instance_id(instance_path, instance)}\n{instance_path}"
    digest = hashlib.sha1(identity.encode("utf-8")).hexdigest()[:12]
    return root / f"instance_{digest}"


def parameter_name(parameter: Any) -> str | None:
    if not isinstance(parameter, dict):
        return None
    namespace = parameter.get("namespace")
    name = parameter.get("name")
    if isinstance(namespace, str) and isinstance(name, str):
        return f"{namespace}/{name}"
    return None


def selected_parameter_name(llm_output: Path | None) -> str | None:
    if llm_output is None or not llm_output.exists():
        return None
    try:
        payload = load_json(llm_output)
    except Exception:  # noqa: BLE001
        return None
    actions = payload.get("repair_actions") if isinstance(payload, dict) else None
    if isinstance(actions, list) and actions and isinstance(actions[0], dict):
        return parameter_name(actions[0].get("parameter"))
    return None


def first_action_from_output(llm_output: Path | None) -> dict[str, Any] | None:
    if llm_output is None or not llm_output.exists():
        return None
    try:
        payload = load_json(llm_output)
    except Exception:  # noqa: BLE001
        return None
    actions = payload.get("repair_actions") if isinstance(payload, dict) else None
    if isinstance(actions, list) and actions and isinstance(actions[0], dict):
        return actions[0]
    return None


def gold_action(instance: Any) -> dict[str, Any] | None:
    actions = instance.get("gold_repair_actions") if isinstance(instance, dict) else None
    if isinstance(actions, list) and actions and isinstance(actions[0], dict):
        return actions[0]
    return None


def target_name(target: Any) -> str | None:
    if not isinstance(target, dict):
        return None
    tag = target.get("tag")
    guid = target.get("guid")
    if isinstance(tag, str) and tag:
        return tag
    return guid if isinstance(guid, str) else None


def target_parts(target: Any) -> tuple[str | None, str | None, str | None]:
    if not isinstance(target, dict):
        return None, None, None
    guid = target.get("guid")
    tag = target.get("tag")
    guid_text = guid if isinstance(guid, str) and guid else None
    tag_text = tag if isinstance(tag, str) and tag else None
    return target_name(target), guid_text, tag_text


def selected_action_summary(llm_output: Path | None) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    action = first_action_from_output(llm_output)
    if isinstance(action, dict):
        target, target_guid, target_tag = target_parts(action.get("target"))
        parameter = parameter_name(action.get("parameter"))
        pair = f"{target}: {parameter}" if target and parameter else None
        return target, parameter, pair, target_guid, target_tag
    return None, None, None, None, None


def gold_parameter_name(instance: Any) -> str | None:
    actions = instance.get("gold_repair_actions") if isinstance(instance, dict) else None
    if isinstance(actions, list) and actions and isinstance(actions[0], dict):
        return parameter_name(actions[0].get("parameter"))
    return None


def gold_action_summary(instance: Any) -> tuple[str | None, str | None, str | None, str | None, str | None]:
    action = gold_action(instance)
    if isinstance(action, dict):
        target, target_guid, target_tag = target_parts(action.get("target"))
        parameter = parameter_name(action.get("parameter"))
        pair = f"{target}: {parameter}" if target and parameter else None
        return target, parameter, pair, target_guid, target_tag
    return None, None, None, None, None


def action_pair_key(action: dict[str, Any] | None) -> str | None:
    if not isinstance(action, dict):
        return None
    target = action.get("target") if isinstance(action.get("target"), dict) else {}
    parameter = parameter_name(action.get("parameter"))
    guid = target.get("guid")
    if isinstance(guid, str) and parameter:
        return f"{guid}|{parameter}"
    return None


def load_metadata(path: Path | None) -> dict[str, Any]:
    if path is None or not path.exists():
        return {}
    try:
        data = load_json(path)
    except Exception:  # noqa: BLE001
        return {}
    return data if isinstance(data, dict) else {}


def nested_metadata(metadata: dict[str, Any]) -> dict[str, Any]:
    provider_metadata = metadata.get("provider_metadata")
    return provider_metadata if isinstance(provider_metadata, dict) else {}


def usage_value(usage: Any, *keys: str) -> Any:
    if not isinstance(usage, dict):
        return None
    for key in keys:
        value = usage.get(key)
        if isinstance(value, (int, float)):
            return value
    return None


def usage_total_value(usage: Any) -> Any:
    total = usage_value(usage, "total_tokens", "total_token_count")
    if total is not None:
        return total
    input_tokens = usage_value(usage, "input_tokens", "prompt_token_count")
    output_tokens = usage_value(usage, "output_tokens", "candidates_token_count")
    if isinstance(input_tokens, (int, float)) and isinstance(output_tokens, (int, float)):
        return input_tokens + output_tokens
    return None


def git_commit() -> str | None:
    try:
        completed = subprocess.run(
            ["git", "rev-parse", "--short", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            check=False,
        )
    except Exception:  # noqa: BLE001
        return None
    commit = completed.stdout.strip()
    return commit or None


def numeric_positive(value: Any, tolerance: float = 1e-12) -> bool:
    return isinstance(value, (int, float)) and value > tolerance


def gold_proximity_type(report: dict[str, Any]) -> str | None:
    if report.get("pipeline_success") is not True:
        return None
    proximity = report.get("gold_proximity") if isinstance(report.get("gold_proximity"), dict) else {}
    target_match = proximity.get("target_match")
    parameter_match = proximity.get("parameter_match")
    unit_match = proximity.get("unit_match")
    value_abs_error = proximity.get("value_abs_error")
    if target_match is True and parameter_match is True and unit_match is True and not numeric_positive(value_abs_error):
        return "gold_exact"
    if target_match is False and parameter_match is False:
        return "wrong_action_pair"
    if target_match is False:
        return "wrong_target"
    if parameter_match is False:
        return "wrong_parameter"
    if unit_match is False:
        return "wrong_unit"
    if numeric_positive(value_abs_error):
        return "right_parameter_different_value"
    return "gold_mismatch_unknown"


def gold_mismatch_success_type(report: dict[str, Any]) -> str | None:
    if report.get("executable_success") is not True:
        return None
    proximity_type = gold_proximity_type(report)
    if proximity_type is None or proximity_type == "gold_exact":
        return proximity_type
    return f"{proximity_type}_success"


def failure_type(report: dict[str, Any]) -> str | None:
    stage = report.get("error_stage")
    if stage == "dry_run_sanitize":
        return "dry_run_sanitize"
    if stage == "provider_config":
        return "provider_config_failure"
    if stage == "provider_call":
        return "provider_call_failure"
    if stage == "provider_response":
        return "model_output_failure"
    if stage in {"gemini_output", "llm_output"}:
        return "model_output_failure"
    if stage == "schema_validation":
        return "schema_failure"
    if stage == "executor_timeout":
        return "executor_timeout"
    if stage == "executor":
        return "executor_failure"
    if stage == "dwsim_timeout":
        return "dwsim_timeout"
    if stage == "dwsim_metrics":
        return "dwsim_failure"
    if report.get("pipeline_success") is True:
        if report.get("executable_success") is True:
            return None
        proximity = report.get("gold_proximity") if isinstance(report.get("gold_proximity"), dict) else {}
        if proximity.get("target_match") is False and proximity.get("parameter_match") is False:
            return "wrong_action_pair"
        if proximity.get("target_match") is False:
            return "wrong_target"
        if proximity.get("parameter_match") is False:
            return "wrong_parameter"
        value_abs_error = proximity.get("value_abs_error")
        if proximity.get("parameter_match") is True and isinstance(value_abs_error, (int, float)) and value_abs_error > 1e-12:
            return "right_parameter_wrong_value"
        return "target_failure"
    return str(stage or "pipeline_failure")


def row_from_report(
    instance_path: Path,
    instance: Any,
    provider: str,
    model: str,
    prompt_mode: str,
    llm_output: Path | None,
    llm_metadata: Path | None,
    sanitized_prompt: Path | None,
    evaluation_report: Path | None,
    report: dict[str, Any],
    dataset_split_id: str | None,
    git_commit_value: str | None,
    config: dict[str, Any],
) -> dict[str, Any]:
    schema = report.get("schema") if isinstance(report.get("schema"), dict) else {}
    action_schema = report.get("action_schema") if isinstance(report.get("action_schema"), dict) else {}
    executor = report.get("executor") if isinstance(report.get("executor"), dict) else {}
    dwsim = report.get("dwsim") if isinstance(report.get("dwsim"), dict) else {}
    timeouts = report.get("timeouts") if isinstance(report.get("timeouts"), dict) else {}
    target_metric = report.get("target_metric") if isinstance(report.get("target_metric"), dict) else {}
    criteria = report.get("success_criteria") if isinstance(report.get("success_criteria"), dict) else {}
    proximity = report.get("gold_proximity") if isinstance(report.get("gold_proximity"), dict) else {}
    selected_target, selected_parameter, selected_pair, selected_target_guid, selected_target_tag = selected_action_summary(llm_output)
    gold_target, gold_parameter, gold_pair, gold_target_guid, gold_target_tag = gold_action_summary(instance)
    selected_action = first_action_from_output(llm_output)
    expected_action = gold_action(instance)
    metadata = load_metadata(llm_metadata)
    provider_metadata = nested_metadata(metadata)
    provider_error = metadata.get("provider_error") if isinstance(metadata.get("provider_error"), dict) else {}
    usage = provider_metadata.get("usage")
    source = instance.get("source") if isinstance(instance, dict) else {}
    success = instance.get("success_criteria") if isinstance(instance, dict) else {}
    manifest_target = success.get("target_metric") if isinstance(success, dict) else {}
    return {
        "instance_id": instance_id(instance_path, instance),
        "instance_path": str(instance_path),
        "source_category": source.get("source_category") if isinstance(source, dict) else None,
        "target_family": manifest_target.get("family") if isinstance(manifest_target, dict) else None,
        "provider": provider,
        "model": model,
        "prompt_mode": prompt_mode,
        "omit_simulator_log": config.get("omit_simulator_log", False),
        "llm_output": str(llm_output) if llm_output is not None else None,
        "llm_metadata": str(llm_metadata) if llm_metadata is not None else None,
        "sanitized_prompt": str(sanitized_prompt) if sanitized_prompt is not None else None,
        "evaluation_report": str(evaluation_report) if evaluation_report is not None else None,
        "dataset_split_id": dataset_split_id,
        "git_commit": git_commit_value,
        "prompt_hash": metadata.get("prompt_hash"),
        "schema_hash": metadata.get("schema_hash"),
        "api_retry_max": config.get("api_retry_max"),
        "provider_call_delay_sec": config.get("provider_call_delay_sec"),
        "model_output_retry": config.get("model_output_retry"),
        "simulator_retry": config.get("simulator_retry"),
        "structured_output_mode": config.get("structured_output_mode"),
        "provider_schema_variant": config.get("provider_schema_variant"),
        "provider_request_id": provider_metadata.get("request_id"),
        "provider_response_id": provider_metadata.get("response_id"),
        "provider_model_version": provider_metadata.get("model_version"),
        "provider_status": provider_metadata.get("status"),
        "provider_finish_reason": provider_metadata.get("finish_reason"),
        "provider_latency_sec": provider_metadata.get("latency_sec"),
        "provider_api_retry_count": provider_metadata.get("api_retry_count"),
        "provider_usage_input_tokens": usage_value(usage, "input_tokens", "prompt_token_count"),
        "provider_usage_output_tokens": usage_value(usage, "output_tokens", "candidates_token_count"),
        "provider_usage_total_tokens": usage_total_value(usage),
        "provider_error_type": provider_error.get("type"),
        "provider_error_message": provider_error.get("message"),
        "validation_status": metadata.get("validation_status"),
        "validation_error": metadata.get("validation_error"),
        "schema_valid": schema.get("valid") is True,
        "action_schema_valid": action_schema.get("valid") is True,
        "executor_success": executor.get("success") is True,
        "dwsim_success": dwsim.get("success") is True,
        "executor_timed_out": executor.get("timed_out") is True,
        "dwsim_timed_out": dwsim.get("timed_out") is True,
        "executor_timeout_sec": timeouts.get("executor_timeout_sec"),
        "dwsim_timeout_sec": timeouts.get("dwsim_timeout_sec"),
        "pipeline_success": report.get("pipeline_success") is True,
        "executable_success": report.get("executable_success") is True,
        "criteria_converged": criteria.get("converged"),
        "criteria_no_fatal_error": criteria.get("no_fatal_error"),
        "criteria_target_metric": criteria.get("target_metric"),
        "target_value": target_metric.get("value"),
        "target_direction": target_metric.get("direction"),
        "target_threshold": target_metric.get("threshold"),
        "target_stream_tag": target_metric.get("stream_tag"),
        "target_stream_id": target_metric.get("stream_id"),
        "target_stream_role": target_metric.get("stream_role"),
        "target_metric_name": target_metric.get("metric"),
        "target_component": target_metric.get("component"),
        "target_match": proximity.get("target_match"),
        "parameter_match": proximity.get("parameter_match"),
        "unit_match": proximity.get("unit_match"),
        "value_abs_error": proximity.get("value_abs_error"),
        "value_rel_error": proximity.get("value_rel_error"),
        "selected_value": selected_action.get("value") if isinstance(selected_action, dict) else None,
        "selected_unit": selected_action.get("unit") if isinstance(selected_action, dict) else None,
        "gold_value": expected_action.get("value") if isinstance(expected_action, dict) else None,
        "gold_unit": expected_action.get("unit") if isinstance(expected_action, dict) else None,
        "selected_parameter": selected_parameter,
        "gold_parameter": gold_parameter,
        "selected_target": selected_target,
        "gold_target": gold_target,
        "selected_target_guid": selected_target_guid,
        "selected_target_tag": selected_target_tag,
        "gold_target_guid": gold_target_guid,
        "gold_target_tag": gold_target_tag,
        "selected_action_pair": selected_pair,
        "gold_action_pair": gold_pair,
        "selected_action_pair_key": action_pair_key(selected_action),
        "gold_action_pair_key": action_pair_key(expected_action),
        "gold_proximity_type": gold_proximity_type(report),
        "gold_mismatch_success_type": gold_mismatch_success_type(report),
        "failure_type": failure_type(report),
        "error_stage": report.get("error_stage"),
        "error": report.get("error"),
    }


def failure_report(
    instance_path: Path,
    instance: Any,
    work_dir: Path,
    llm_output: Path | None,
    message: str,
    error_stage: str = "llm_output",
) -> dict[str, Any]:
    return {
        "pipeline_success": False,
        "executable_success": False,
        "error_stage": error_stage,
        "error": message,
        "instance": str(instance_path),
        "repair_output_json": str(llm_output) if llm_output is not None else None,
        "work_dir": str(work_dir),
        "schema": {"valid": False, "errors": []},
        "action_schema": {"valid": False, "errors": []},
        "executor": None,
        "dwsim": None,
        "target_metric": None,
        "success_criteria": None,
        "gold_proximity": None,
    }


def evaluate_generated_output(
    instance_path: Path,
    repair_output_json: Path,
    work_dir: Path,
    report_path: Path,
    require_success: bool,
    executor_timeout_sec: int,
    dwsim_timeout_sec: int,
) -> tuple[dict[str, Any], int]:
    args = argparse.Namespace(
        instance=instance_path,
        repair_output_json=repair_output_json,
        work_dir=work_dir,
        require_success=require_success,
        executor_timeout_sec=executor_timeout_sec,
        dwsim_timeout_sec=dwsim_timeout_sec,
    )
    report, exit_code = evaluate(args, report_path)
    write_json(report_path, report)
    return report, exit_code


def run_instance(args: argparse.Namespace, instance_path: Path) -> tuple[dict[str, Any], int]:
    instance: Any = None
    item_work_dir = instance_work_dir(args.work_dir, instance_path)
    llm_output = item_work_dir / f"{args.provider}_llm_output.json"
    llm_metadata = item_work_dir / "llm_metadata.json"
    sanitized_prompt = item_work_dir / f"{args.provider}_prompt.md"
    effective_llm_input = item_work_dir / "llm_input.md"
    evaluation_report = item_work_dir / "evaluation_report.json"
    config = run_config(args.provider, args.model, args.prompt_mode)
    config["provider_call_delay_sec"] = args.provider_call_delay_sec
    config["omit_simulator_log"] = getattr(args, "omit_simulator_log", False)
    try:
        # Clear stale metadata even on failures before prompt generation.
        if llm_metadata.exists():
            llm_metadata.unlink()
        if config["omit_simulator_log"] and args.prompt_mode != "parameter-selection":
            raise ValueError("--omit-simulator-log requires --prompt-mode parameter-selection")
        instance = load_json(instance_path)
        if not isinstance(instance, dict):
            raise ValueError("instance file must contain a JSON object")
        item_work_dir = instance_work_dir(args.work_dir, instance_path, instance)
        llm_output = item_work_dir / f"{args.provider}_llm_output.json"
        llm_metadata = item_work_dir / "llm_metadata.json"
        sanitized_prompt = item_work_dir / f"{args.provider}_prompt.md"
        effective_llm_input = item_work_dir / "llm_input.md"
        evaluation_report = item_work_dir / "evaluation_report.json"
        if llm_metadata.exists():
            llm_metadata.unlink()

        observations = instance.get("observations")
        if not isinstance(observations, dict):
            raise ValueError("instance.observations must be an object")
        llm_input_ref = instance.get("llm_input")
        parameters_ref = observations.get("parameters")
        if not isinstance(llm_input_ref, str) or not isinstance(parameters_ref, str):
            raise ValueError("instance must include llm_input and observations.parameters")

        if args.prompt_mode == "parameter-selection":
            generate_llm_input_packet(
                instance_path, effective_llm_input, prompt_mode=args.prompt_mode,
                omit_simulator_log=config["omit_simulator_log"],
            )
            llm_input_path = effective_llm_input
        else:
            llm_input_path = instance_ref(instance_path, llm_input_ref)

        if llm_output.exists():
            llm_output.unlink()
        generate_llm_output(
            llm_input_path=llm_input_path,
            output_path=llm_output,
            parameters_path=instance_ref(instance_path, parameters_ref),
            model=args.model,
            env_file=args.env_file,
            dry_run_sanitize=args.dry_run_sanitize,
            sanitized_prompt_output=sanitized_prompt,
            prompt_mode=args.prompt_mode,
            provider=args.provider,
            metadata_output=llm_metadata,
        )
        if args.dry_run_sanitize:
            report = {
                "pipeline_success": True,
                "executable_success": False,
                "error_stage": "dry_run_sanitize",
                "target_metric": None,
                "gold_proximity": None,
            }
            write_json(evaluation_report, report)
            return row_from_report(
                instance_path,
                instance,
                args.provider,
                args.model,
                args.prompt_mode,
                None,
                llm_metadata,
                sanitized_prompt,
                evaluation_report,
                report,
                args.dataset_split_id,
                args.git_commit,
                config,
            ), 0

        report, exit_code = evaluate_generated_output(
            instance_path,
            llm_output,
            item_work_dir / "evaluation_work",
            evaluation_report,
            args.require_success,
            args.executor_timeout_sec,
            args.dwsim_timeout_sec,
        )
        return row_from_report(
            instance_path,
            instance,
            args.provider,
            args.model,
            args.prompt_mode,
            llm_output,
            llm_metadata,
            sanitized_prompt,
            evaluation_report,
            report,
            args.dataset_split_id,
            args.git_commit,
            config,
        ), exit_code
    except Exception as exc:  # noqa: BLE001
        if isinstance(exc, ProviderConfigError):
            error_stage = "provider_config"
        elif isinstance(exc, ProviderCallError):
            error_stage = "provider_call"
        elif isinstance(exc, ProviderResponseError):
            error_stage = "provider_response"
        elif isinstance(exc, LLMOutputValidationError):
            error_stage = "schema_validation"
        else:
            error_stage = "llm_output"
        report = failure_report(instance_path, instance, item_work_dir, llm_output, str(exc), error_stage)
        write_json(evaluation_report, report)
        return row_from_report(
            instance_path,
            instance,
            args.provider,
            args.model,
            args.prompt_mode,
            llm_output,
            llm_metadata,
            sanitized_prompt,
            evaluation_report,
            report,
            args.dataset_split_id,
            args.git_commit,
            config,
        ), 1
    finally:
        # The generator retains provider details and hashes on all its error paths.
        # Add the batch condition even when input preparation fails before a call.
        metadata = load_metadata(llm_metadata)
        metadata["omit_simulator_log"] = config["omit_simulator_log"]
        write_json(llm_metadata, metadata)


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROW_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in ROW_FIELDS})


def aggregate(
    rows: list[dict[str, Any]],
    provider: str,
    model: str,
    dry_run_sanitize: bool,
    dataset_split_id: str | None,
    git_commit_value: str | None,
    provider_call_delay_sec: float,
    omit_simulator_log: bool = False,
) -> dict[str, Any]:
    failure_counts: dict[str, int] = {}
    preflight_counts: dict[str, int] = {}
    for row in rows:
        failure = row.get("failure_type")
        if isinstance(failure, str) and failure:
            if dry_run_sanitize or failure == "dry_run_sanitize":
                preflight_counts[failure] = preflight_counts.get(failure, 0) + 1
            else:
                failure_counts[failure] = failure_counts.get(failure, 0) + 1
    gold_proximity_types = {
        str(key): sum(1 for row in rows if row.get("gold_proximity_type") == key)
        for key in sorted({row.get("gold_proximity_type") for row in rows if row.get("gold_proximity_type")})
    }
    gold_mismatch_success_types = {
        str(key): sum(1 for row in rows if row.get("gold_mismatch_success_type") == key)
        for key in sorted({row.get("gold_mismatch_success_type") for row in rows if row.get("gold_mismatch_success_type")})
    }
    config = run_config(provider, model, rows[0].get("prompt_mode") if rows else "unknown")
    config["provider_call_delay_sec"] = provider_call_delay_sec
    config["omit_simulator_log"] = omit_simulator_log
    return {
        "provider": provider,
        "model": model,
        "prompt_mode": rows[0].get("prompt_mode") if rows else None,
        "omit_simulator_log": omit_simulator_log,
        "llm_run_config": config,
        "dataset_split_id": dataset_split_id,
        "git_commit": git_commit_value,
        "api_retry_max": config.get("api_retry_max"),
        "provider_call_delay_sec": provider_call_delay_sec,
        "model_output_retry": False,
        "simulator_retry": False,
        "dry_run_sanitize": dry_run_sanitize,
        "instance_count": len(rows),
        "pipeline_success_count": sum(1 for row in rows if row.get("pipeline_success") is True),
        "executable_success_count": sum(1 for row in rows if row.get("executable_success") is True),
        "exec_success_with_gold_mismatch_count": sum(
            1
            for row in rows
            if row.get("executable_success") is True and row.get("gold_proximity_type") not in {None, "gold_exact"}
        ),
        "wrong_parameter_success_count": sum(
            1 for row in rows if row.get("gold_mismatch_success_type") == "wrong_parameter_success"
        ),
        "failure_counts": failure_counts,
        "preflight_counts": preflight_counts,
        "gold_proximity_type_counts": gold_proximity_types,
        "gold_mismatch_success_type_counts": gold_mismatch_success_types,
        "selected_action_pair_counts": {
            str(key): sum(1 for row in rows if row.get("selected_action_pair") == key)
            for key in sorted({row.get("selected_action_pair") for row in rows if row.get("selected_action_pair")})
        },
        "target_family_counts": {
            str(key): sum(1 for row in rows if row.get("target_family") == key)
            for key in sorted({row.get("target_family") for row in rows if row.get("target_family")})
        },
        "source_category_counts": {
            str(key): sum(1 for row in rows if row.get("source_category") == key)
            for key in sorted({row.get("source_category") for row in rows if row.get("source_category")})
        },
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instances", nargs="+", required=True, type=Path)
    parser.add_argument("--work-dir", default=DEFAULT_WORK_DIR, type=Path)
    parser.add_argument("--aggregate-json", type=Path)
    parser.add_argument("--aggregate-csv", type=Path)
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default=DEFAULT_PROVIDER)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE, type=Path)
    parser.add_argument("--prompt-mode", choices=sorted(PROMPT_MODES), default="oracle-parameter")
    parser.add_argument(
        "--omit-simulator-log", action="store_true",
        help="Omit only the Faulty Simulator Log section (parameter-selection mode only).",
    )
    parser.add_argument("--dry-run-sanitize", action="store_true")
    parser.add_argument("--require-success", action="store_true")
    parser.add_argument("--dataset-split-id")
    parser.add_argument("--executor-timeout-sec", default=60, type=int)
    parser.add_argument("--dwsim-timeout-sec", default=180, type=int)
    parser.add_argument(
        "--provider-call-delay-sec",
        default=0.0,
        type=float,
        help="Sleep this many seconds after each instance before starting the next provider call.",
    )
    args = parser.parse_args()
    if args.omit_simulator_log and args.prompt_mode != "parameter-selection":
        parser.error("--omit-simulator-log requires --prompt-mode parameter-selection")

    args.aggregate_json = args.aggregate_json or args.work_dir / "aggregate.json"
    args.aggregate_csv = args.aggregate_csv or args.work_dir / "aggregate.csv"
    if args.dataset_split_id is None:
        args.dataset_split_id = args.instances[0].name if len(args.instances) == 1 else "mixed"
    args.git_commit = git_commit()

    rows: list[dict[str, Any]] = []
    exit_codes: list[int] = []
    instance_paths = collect_instance_paths(args.instances)
    for index, instance_path in enumerate(instance_paths):
        row, exit_code = run_instance(args, instance_path)
        rows.append(row)
        exit_codes.append(exit_code)
        print(
            f"{row['instance_id']}: "
            f"pipeline_success={row['pipeline_success']} "
            f"executable_success={row['executable_success']} "
            f"failure_type={row['failure_type']}"
        )
        if args.provider_call_delay_sec > 0 and index < len(instance_paths) - 1:
            time.sleep(args.provider_call_delay_sec)

    summary = aggregate(
        rows,
        args.provider,
        args.model,
        args.dry_run_sanitize,
        args.dataset_split_id,
        args.git_commit,
        args.provider_call_delay_sec,
        omit_simulator_log=args.omit_simulator_log,
    )
    write_json(args.aggregate_json, summary)
    write_csv(args.aggregate_csv, rows)
    print(f"Wrote {args.provider} pilot aggregate JSON to {args.aggregate_json}")
    print(f"Wrote {args.provider} pilot aggregate CSV to {args.aggregate_csv}")

    if args.require_success:
        for row, exit_code in zip(rows, exit_codes, strict=True):
            if exit_code != 0 or row.get("executable_success") is not True:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
