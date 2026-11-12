#!/usr/bin/env python3
"""Evaluate a release instance set with a common repair-output source."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Any

from evaluate_repair_output import evaluate, load_json, write_json


DEFAULT_INSTANCES = [Path("instances/seed")]
DEFAULT_WORK_DIR = Path(".tmp/release_set_evaluation")
ROW_FIELDS = [
    "instance_id",
    "instance_path",
    "parameter",
    "repair_output_json",
    "report_path",
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
    "target_value",
    "target_min",
    "target_direction",
    "target_threshold",
    "criteria_converged",
    "criteria_no_fatal_error",
    "criteria_target_metric",
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
    "selected_action_pair_key",
    "gold_action_pair_key",
    "error_stage",
]


def collect_instance_paths(paths: list[Path]) -> list[Path]:
    instances: list[Path] = []
    for path in paths:
        if path.is_dir():
            instances.extend(sorted(path.rglob("instance.json")))
        else:
            instances.append(path)
    return sorted(dict.fromkeys(instances))


def instance_id(instance_path: Path, instance: Any | None = None) -> str:
    if isinstance(instance, dict) and isinstance(instance.get("id"), str) and instance["id"]:
        return instance["id"]
    return instance_path.parent.name


def parameter_name(instance: Any) -> str | None:
    if not isinstance(instance, dict):
        return None
    actions = instance.get("gold_repair_actions")
    if not isinstance(actions, list) or not actions or not isinstance(actions[0], dict):
        return None
    parameter = actions[0].get("parameter")
    if not isinstance(parameter, dict):
        return None
    namespace = parameter.get("namespace")
    name = parameter.get("name")
    if isinstance(namespace, str) and isinstance(name, str):
        return f"{namespace}/{name}"
    return None


def parameter_key(parameter: Any) -> str | None:
    if not isinstance(parameter, dict):
        return None
    namespace = parameter.get("namespace")
    name = parameter.get("name")
    if isinstance(namespace, str) and isinstance(name, str):
        return f"{namespace}/{name}"
    return None


def first_action_from_payload(path: Path | None) -> dict[str, Any] | None:
    if path is None or not path.exists():
        return None
    try:
        payload = load_json(path)
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


def action_pair_key(action: dict[str, Any] | None) -> str | None:
    if not isinstance(action, dict):
        return None
    target = action.get("target") if isinstance(action.get("target"), dict) else {}
    parameter = parameter_key(action.get("parameter"))
    guid = target.get("guid")
    if isinstance(guid, str) and parameter:
        return f"{guid}|{parameter}"
    return None


def instance_ref(instance_path: Path, ref: str) -> Path:
    return instance_path.parent / ref


def repair_output_for_mode(instance_path: Path, instance: dict[str, Any], mode: str) -> Path:
    if mode != "hidden-mock":
        raise ValueError(f"unsupported mode: {mode}")
    mock_ref = instance.get("mock_llm_output")
    if not isinstance(mock_ref, str) or not mock_ref:
        raise ValueError("instance.mock_llm_output is required for mode=hidden-mock")
    return instance_ref(instance_path, mock_ref)


def bool_field(value: Any) -> bool:
    return bool(value is True)


def row_from_report(instance_path: Path, instance: Any, repair_output_json: Path | None, report_path: Path, report: dict[str, Any]) -> dict[str, Any]:
    target_metric = report.get("target_metric") if isinstance(report.get("target_metric"), dict) else {}
    proximity = report.get("gold_proximity") if isinstance(report.get("gold_proximity"), dict) else {}
    executor = report.get("executor") if isinstance(report.get("executor"), dict) else {}
    dwsim = report.get("dwsim") if isinstance(report.get("dwsim"), dict) else {}
    timeouts = report.get("timeouts") if isinstance(report.get("timeouts"), dict) else {}
    schema = report.get("schema") if isinstance(report.get("schema"), dict) else {}
    action_schema = report.get("action_schema") if isinstance(report.get("action_schema"), dict) else {}
    criteria = report.get("success_criteria") if isinstance(report.get("success_criteria"), dict) else {}
    selected_action = first_action_from_payload(repair_output_json)
    expected_action = gold_action(instance)
    return {
        "instance_id": instance_id(instance_path, instance),
        "instance_path": str(instance_path),
        "parameter": parameter_name(instance),
        "repair_output_json": str(repair_output_json) if repair_output_json is not None else None,
        "report_path": str(report_path),
        "schema_valid": bool_field(schema.get("valid")),
        "action_schema_valid": bool_field(action_schema.get("valid")),
        "executor_success": bool_field(executor.get("success")),
        "dwsim_success": bool_field(dwsim.get("success")),
        "executor_timed_out": bool_field(executor.get("timed_out")),
        "dwsim_timed_out": bool_field(dwsim.get("timed_out")),
        "executor_timeout_sec": timeouts.get("executor_timeout_sec"),
        "dwsim_timeout_sec": timeouts.get("dwsim_timeout_sec"),
        "pipeline_success": bool_field(report.get("pipeline_success")),
        "executable_success": bool_field(report.get("executable_success")),
        "target_value": target_metric.get("value"),
        "target_min": target_metric.get("minimum"),
        "target_direction": target_metric.get("direction"),
        "target_threshold": target_metric.get("threshold"),
        "criteria_converged": criteria.get("converged"),
        "criteria_no_fatal_error": criteria.get("no_fatal_error"),
        "criteria_target_metric": criteria.get("target_metric"),
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
        "selected_action_pair_key": action_pair_key(selected_action),
        "gold_action_pair_key": action_pair_key(expected_action),
        "error_stage": report.get("error_stage"),
    }


def failure_report(args: argparse.Namespace, instance_path: Path, instance: Any | None, repair_output_json: Path | None, report_path: Path, message: str) -> dict[str, Any]:
    return {
        "pipeline_success": False,
        "executable_success": False,
        "error_stage": "batch_setup",
        "error": message,
        "instance": str(instance_path),
        "repair_output_json": str(repair_output_json) if repair_output_json is not None else None,
        "work_dir": str(args.work_dir / instance_id(instance_path, instance)),
        "report_output": str(report_path),
        "schema": {"valid": False, "errors": []},
        "action_schema": {"valid": False, "errors": []},
        "executor": None,
        "dwsim": None,
        "target_metric": None,
        "success_criteria": None,
        "gold_proximity": None,
    }


def evaluate_instance(args: argparse.Namespace, instance_path: Path) -> tuple[dict[str, Any], int]:
    instance: Any | None = None
    repair_output_json: Path | None = None
    report_path = args.work_dir / instance_path.parent.name / "evaluation_report.json"
    try:
        instance = load_json(instance_path)
        if not isinstance(instance, dict):
            raise ValueError("instance file must contain a JSON object")
        report_path = args.work_dir / instance_id(instance_path, instance) / "evaluation_report.json"
        repair_output_json = repair_output_for_mode(instance_path, instance, args.mode)
        if not repair_output_json.exists():
            raise ValueError(f"repair output JSON does not exist: {repair_output_json}")

        single_args = argparse.Namespace(
            instance=instance_path,
            repair_output_json=repair_output_json,
            work_dir=report_path.parent,
            require_success=args.require_success,
            executor_timeout_sec=args.executor_timeout_sec,
            dwsim_timeout_sec=args.dwsim_timeout_sec,
        )
        report, exit_code = evaluate(single_args, report_path)
        write_json(report_path, report)
        return row_from_report(instance_path, instance, repair_output_json, report_path, report), exit_code
    except Exception as exc:  # noqa: BLE001
        report = failure_report(args, instance_path, instance, repair_output_json, report_path, str(exc))
        write_json(report_path, report)
        return row_from_report(instance_path, instance, repair_output_json, report_path, report), 1


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=ROW_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in ROW_FIELDS})


def aggregate(mode: str, rows: list[dict[str, Any]]) -> dict[str, Any]:
    success_count = sum(1 for row in rows if row.get("executable_success") is True)
    return {
        "mode": mode,
        "instance_count": len(rows),
        "success_count": success_count,
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instances", nargs="+", default=DEFAULT_INSTANCES, type=Path)
    parser.add_argument("--mode", choices=["hidden-mock"], default="hidden-mock")
    parser.add_argument("--work-dir", default=DEFAULT_WORK_DIR, type=Path)
    parser.add_argument("--aggregate-json", type=Path)
    parser.add_argument("--aggregate-csv", type=Path)
    parser.add_argument("--require-success", action="store_true")
    parser.add_argument("--executor-timeout-sec", default=60, type=int)
    parser.add_argument("--dwsim-timeout-sec", default=180, type=int)
    args = parser.parse_args()

    args.aggregate_json = args.aggregate_json or args.work_dir / "aggregate.json"
    args.aggregate_csv = args.aggregate_csv or args.work_dir / "aggregate.csv"

    instance_paths = collect_instance_paths(args.instances)
    rows: list[dict[str, Any]] = []
    exit_codes: list[int] = []
    for instance_path in instance_paths:
        row, exit_code = evaluate_instance(args, instance_path)
        rows.append(row)
        exit_codes.append(exit_code)
        print(
            f"{row['instance_id']}: "
            f"executable_success={row['executable_success']} "
            f"target_value={row['target_value']} target_threshold={row['target_threshold']} "
            f"error_stage={row['error_stage']}"
        )

    summary = aggregate(args.mode, rows)
    write_json(args.aggregate_json, summary)
    write_csv(args.aggregate_csv, rows)
    print(f"Wrote aggregate JSON to {args.aggregate_json}")
    print(f"Wrote aggregate CSV to {args.aggregate_csv}")

    if args.require_success:
        for row, exit_code in zip(rows, exit_codes, strict=True):
            if exit_code != 0 or row.get("pipeline_success") is not True or row.get("executable_success") is not True:
                return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
