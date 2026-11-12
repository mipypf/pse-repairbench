#!/usr/bin/env python3
"""Evaluate a repair-output JSON against one benchmark instance."""

from __future__ import annotations

import argparse
import json
import math
import os
import subprocess
import sys
import warnings
from pathlib import Path
from typing import Any

warnings.filterwarnings("ignore", category=DeprecationWarning)
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dwsim_run_contract import is_successful_dwsim_run  # noqa: E402

try:
    from jsonschema import Draft202012Validator, RefResolver
except ImportError:  # pragma: no cover - exercised only before dependencies exist.
    print(
        "ERROR: missing dependency 'jsonschema'. Install with: pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(2)


DEFAULT_INSTANCE = Path("instances/seed/distillation_002_reflux_ratio_single/instance.json")
DEFAULT_WORK_DIR = Path(".tmp/repair_output_evaluation")
APPLY_REPAIR_ACTIONS = Path("scripts/dwsim/apply_repair_actions.py")
METRIC_WORKER = Path("scripts/dwsim/dwsim_metrics_worker.ps1")
DEFAULT_EXECUTOR_TIMEOUT_SEC = 60
DEFAULT_DWSIM_TIMEOUT_SEC = 180


def repo_root() -> Path:
    return Path.cwd()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def instance_ref(instance_path: Path, ref: str) -> Path:
    return instance_path.parent / ref


def compact_completed_process(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "returncode": completed.returncode,
        "timed_out": False,
        "stdout_tail": completed.stdout[-2000:] if completed.stdout else "",
        "stderr_tail": completed.stderr[-2000:] if completed.stderr else "",
    }


def stream_tail(value: Any) -> str:
    if isinstance(value, bytes):
        value = value.decode("utf-8", errors="replace")
    if not isinstance(value, str):
        return ""
    return value[-2000:]


def compact_timeout(error: subprocess.TimeoutExpired) -> dict[str, Any]:
    return {
        "returncode": None,
        "timed_out": True,
        "timeout_seconds": error.timeout,
        "stdout_tail": stream_tail(getattr(error, "stdout", None) or getattr(error, "output", None)),
        "stderr_tail": stream_tail(getattr(error, "stderr", None)),
        "error": f"timeout after {error.timeout}s",
    }


def terminate_process_tree(process: subprocess.Popen[str]) -> None:
    if os.name == "nt":
        subprocess.run(
            ["taskkill.exe", "/PID", str(process.pid), "/T", "/F"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            check=False,
        )
    else:
        process.kill()


def run_command(command: list[str | Path], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    command_text = [str(part) for part in command]
    process = subprocess.Popen(
        command_text,
        cwd=repo_root(),
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        encoding="utf-8",
        errors="replace",
        text=True,
    )
    try:
        stdout, stderr = process.communicate(timeout=timeout)
    except subprocess.TimeoutExpired as original:
        terminate_process_tree(process)
        try:
            stdout, stderr = process.communicate(timeout=5)
        except subprocess.TimeoutExpired:
            process.kill()
            stdout, stderr = process.communicate()
        raise subprocess.TimeoutExpired(command_text, timeout, output=stdout, stderr=stderr) from original
    return subprocess.CompletedProcess(command_text, process.returncode, stdout, stderr)


def schema_store(schema_dir: Path) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    repair_action_schema = load_json(schema_dir / "repair_action.schema.json")
    repair_output_schema = load_json(schema_dir / "repair_output.schema.json")
    store = {
        repair_action_schema["$id"]: repair_action_schema,
        repair_output_schema["$id"]: repair_output_schema,
        (schema_dir / "repair_action.schema.json").resolve().as_uri(): repair_action_schema,
        (schema_dir / "repair_output.schema.json").resolve().as_uri(): repair_output_schema,
    }
    return repair_action_schema, repair_output_schema, store


def repair_output_validator(repo_root_path: Path) -> Draft202012Validator:
    schema_dir = repo_root_path / "schemas"
    _action_schema, output_schema, store = schema_store(schema_dir)
    resolver = RefResolver(
        base_uri=(schema_dir / "repair_output.schema.json").resolve().as_uri(),
        referrer=output_schema,
        store=store,
    )
    return Draft202012Validator(output_schema, resolver=resolver)


def repair_action_validator(repo_root_path: Path) -> Draft202012Validator:
    schema_dir = repo_root_path / "schemas"
    action_schema, _output_schema, _store = schema_store(schema_dir)
    return Draft202012Validator(action_schema)


def validation_errors(validator: Draft202012Validator, data: Any, prefix: str) -> list[str]:
    errors: list[str] = []
    for error in sorted(validator.iter_errors(data), key=lambda item: list(item.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path)
        name = f"{prefix}.{location}" if location else prefix
        errors.append(f"{name}: {error.message}")
    return errors


def action_validation_errors(payload: Any) -> list[str]:
    if not isinstance(payload, dict):
        return ["repair_output: must be a JSON object"]
    actions = payload.get("repair_actions")
    if not isinstance(actions, list):
        return ["repair_output.repair_actions: must be an array"]
    validator = repair_action_validator(repo_root())
    errors: list[str] = []
    for index, action in enumerate(actions):
        errors.extend(validation_errors(validator, action, f"repair_actions[{index}]"))
    return errors


def instance_target(instance: dict[str, Any]) -> dict[str, Any]:
    success = instance.get("success_criteria")
    if not isinstance(success, dict):
        success = {}
    target_metric = success.get("target_metric")
    if isinstance(target_metric, dict):
        threshold = target_metric.get("threshold")
        if threshold is None:
            threshold = target_metric.get("min") if target_metric.get("direction") != "max" else target_metric.get("max")
        return {
            "family": target_metric.get("family"),
            "stream_tag": target_metric.get("stream_tag") or target_metric.get("stream"),
            "stream_id": target_metric.get("stream_id"),
            "stream_role": target_metric.get("stream_role"),
            "component": target_metric.get("component"),
            "metric": target_metric.get("metric") or "mole_fraction",
            "direction": target_metric.get("direction") or "min",
            "threshold": threshold,
        }
    target = {
        "stream_tag": success.get("target_stream_tag"),
        "component": success.get("target_component"),
        "metric": "mole_fraction",
        "direction": "min",
        "minimum": success.get("product_mole_fraction_min"),
        "threshold": success.get("product_mole_fraction_min"),
    }
    return target


def target_column_guid(instance_path: Path, instance: dict[str, Any]) -> str | None:
    observations = instance.get("observations")
    if isinstance(observations, dict) and isinstance(observations.get("parameters"), str):
        parameters = load_json(instance_ref(instance_path, observations["parameters"]))
        unit = parameters.get("target_unit") if isinstance(parameters, dict) else None
        guid = unit.get("guid") if isinstance(unit, dict) else None
        if isinstance(guid, str) and guid:
            return guid
        column = parameters.get("target_column") if isinstance(parameters, dict) else None
        guid = column.get("guid") if isinstance(column, dict) else None
        if isinstance(guid, str) and guid:
            return guid
    gold_actions = instance.get("gold_repair_actions")
    if isinstance(gold_actions, list) and gold_actions and isinstance(gold_actions[0], dict):
        target = gold_actions[0].get("target")
        guid = target.get("guid") if isinstance(target, dict) else None
        if isinstance(guid, str) and guid:
            return guid
    return None


def target_mole_fraction(run: dict[str, Any], stream_tag: str, component: str) -> float | None:
    for stream in run.get("streams", []):
        if not isinstance(stream, dict) or (stream.get("tag") != stream_tag and stream.get("id") != stream_tag):
            continue
        compounds = stream.get("compounds")
        if not isinstance(compounds, dict):
            return None
        metrics = compounds.get(component)
        if not isinstance(metrics, dict):
            return None
        value = metrics.get("mole_fraction")
        return float(value) if isinstance(value, (int, float)) else None
    return None


def target_metric_value(run: dict[str, Any], target: dict[str, Any]) -> float | None:
    stream_tag = target.get("stream_tag")
    metric = target.get("metric")
    component = target.get("component")
    if not isinstance(stream_tag, str) or not isinstance(metric, str):
        return None
    for stream in run.get("streams", []):
        if not isinstance(stream, dict) or (stream.get("tag") != stream_tag and stream.get("id") != stream_tag):
            continue
        if isinstance(component, str) and component:
            compounds = stream.get("compounds")
            if not isinstance(compounds, dict):
                return None
            metrics = compounds.get(component)
            if not isinstance(metrics, dict):
                return None
            value = metrics.get(metric)
        else:
            value = stream.get(metric)
        return float(value) if isinstance(value, (int, float)) else None
    return None


def numeric_error(actual: Any, expected: Any) -> tuple[float | None, float | None]:
    if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
        return None, None
    absolute = abs(float(actual) - float(expected))
    relative = absolute / max(abs(float(expected)), 1e-12)
    return absolute, relative


def object_ref_match(actual: Any, expected: Any) -> bool:
    if not isinstance(actual, dict) or not isinstance(expected, dict):
        return False
    if expected.get("kind") is not None and actual.get("kind") != expected.get("kind"):
        return False
    for key in ("guid", "name", "tag"):
        if expected.get(key) is not None and actual.get(key) is not None:
            return actual.get(key) == expected.get(key)
    return actual == expected and bool(actual)


def parameter_match(actual: Any, expected: Any) -> bool:
    if not isinstance(actual, dict) or not isinstance(expected, dict):
        return False
    return actual.get("namespace") == expected.get("namespace") and actual.get("name") == expected.get("name")


def gold_proximity(payload: Any, instance: dict[str, Any]) -> dict[str, Any]:
    actual_actions = payload.get("repair_actions") if isinstance(payload, dict) else None
    gold_actions = instance.get("gold_repair_actions")
    actual = actual_actions[0] if isinstance(actual_actions, list) and actual_actions and isinstance(actual_actions[0], dict) else {}
    expected = gold_actions[0] if isinstance(gold_actions, list) and gold_actions and isinstance(gold_actions[0], dict) else {}
    value_abs_error, value_rel_error = numeric_error(actual.get("value"), expected.get("value"))
    return {
        "target_match": object_ref_match(actual.get("target"), expected.get("target")),
        "parameter_match": parameter_match(actual.get("parameter"), expected.get("parameter")),
        "unit_match": actual.get("unit") == expected.get("unit"),
        "value_abs_error": value_abs_error,
        "value_rel_error": value_rel_error,
    }


def apply_repair_action(
    faulty_flowsheet: Path,
    repaired_flowsheet: Path,
    repair_output_json: Path,
    timeout_sec: int,
) -> dict[str, Any]:
    if repaired_flowsheet.exists():
        repaired_flowsheet.unlink()
    command = [
        sys.executable,
        APPLY_REPAIR_ACTIONS,
        "--input-flowsheet",
        faulty_flowsheet,
        "--repair-output",
        repaired_flowsheet,
        "--repair-actions-json",
        repair_output_json,
    ]
    try:
        completed = run_command(command, timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        result = compact_timeout(exc)
        result["success"] = False
        return result
    result = compact_completed_process(completed)
    result["success"] = completed.returncode == 0 and repaired_flowsheet.exists()
    return result


def run_repaired_metrics(
    repaired_flowsheet: Path,
    repaired_run: Path,
    calculated_flowsheet: Path,
    column_guid: str,
    timeout_sec: int,
) -> dict[str, Any]:
    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        METRIC_WORKER,
        "-SimPath",
        repaired_flowsheet,
        "-ResultJsonPath",
        repaired_run,
        "-SavePath",
        calculated_flowsheet,
        "-ColumnGuid",
        column_guid,
    ]
    for stale_path in (repaired_run, calculated_flowsheet):
        if stale_path.exists():
            stale_path.unlink()
    try:
        completed = run_command(command, timeout=timeout_sec)
    except subprocess.TimeoutExpired as exc:
        result = compact_timeout(exc)
        result["worker_returncode"] = None
        result["success"] = False
        return result
    result = compact_completed_process(completed)
    result["worker_returncode"] = completed.returncode
    run_success = False
    if repaired_run.exists():
        try:
            run_data = load_json(repaired_run)
            run_success = is_successful_dwsim_run(run_data)
            if isinstance(run_data, dict):
                result["run_status"] = run_data.get("status")
                result["run_success"] = run_data.get("success")
                result["run_solved_after"] = run_data.get("solved_after")
                result["run_exception_count"] = run_data.get("exception_count")
        except Exception:  # noqa: BLE001
            run_success = False
    result["success"] = repaired_run.exists() and run_success
    return result


def evaluate_success_criteria(run: dict[str, Any], target: dict[str, Any]) -> tuple[dict[str, Any], dict[str, Any], bool]:
    threshold = target.get("threshold", target.get("minimum"))
    direction = target.get("direction") or "min"
    value = target_metric_value(run, target)
    if direction == "max":
        meets = bool(isinstance(value, (int, float)) and isinstance(threshold, (int, float)) and value <= threshold)
    else:
        meets = bool(isinstance(value, (int, float)) and isinstance(threshold, (int, float)) and value >= threshold)
    target_metric = {
        "family": target.get("family"),
        "stream_tag": target.get("stream_tag"),
        "stream_id": target.get("stream_id"),
        "stream_role": target.get("stream_role"),
        "component": target.get("component"),
        "metric": target.get("metric"),
        "direction": direction,
        "value": value,
        "threshold": threshold,
        "minimum": threshold if direction == "min" else None,
        "maximum": threshold if direction == "max" else None,
        "meets": meets,
    }
    criteria = {
        "converged": run.get("solved_after") is True,
        "no_fatal_error": run.get("success") is True and run.get("exception_count") == 0,
        "target_metric": target_metric["meets"],
    }
    return target_metric, criteria, all(criteria.values())


def base_report(args: argparse.Namespace, report_output: Path) -> dict[str, Any]:
    executor_timeout_sec = getattr(args, "executor_timeout_sec", DEFAULT_EXECUTOR_TIMEOUT_SEC)
    dwsim_timeout_sec = getattr(args, "dwsim_timeout_sec", DEFAULT_DWSIM_TIMEOUT_SEC)
    return {
        "pipeline_success": False,
        "executable_success": False,
        "error_stage": None,
        "instance": str(args.instance),
        "repair_output_json": str(args.repair_output_json),
        "work_dir": str(args.work_dir),
        "report_output": str(report_output),
        "schema": {"valid": False, "errors": []},
        "action_schema": {"valid": False, "errors": []},
        "executor": None,
        "dwsim": None,
        "target_metric": None,
        "success_criteria": None,
        "gold_proximity": None,
        "timeouts": {
            "executor_timeout_sec": executor_timeout_sec,
            "dwsim_timeout_sec": dwsim_timeout_sec,
        },
    }


def evaluate(args: argparse.Namespace, report_output: Path) -> tuple[dict[str, Any], int]:
    report = base_report(args, report_output)
    args.work_dir.mkdir(parents=True, exist_ok=True)
    try:
        instance = load_json(args.instance)
        payload = load_json(args.repair_output_json)
        if not isinstance(instance, dict):
            raise ValueError("instance must be a JSON object")

        output_errors = validation_errors(repair_output_validator(repo_root()), payload, "repair_output")
        action_errors = action_validation_errors(payload)
        report["schema"] = {"valid": not output_errors, "errors": output_errors}
        report["action_schema"] = {"valid": not action_errors, "errors": action_errors}
        report["gold_proximity"] = gold_proximity(payload, instance)
        if output_errors or action_errors:
            report["error_stage"] = "schema_validation"
            return report, 1

        faulty_ref = instance.get("faulty_flowsheet")
        if not isinstance(faulty_ref, str):
            raise ValueError("instance.faulty_flowsheet is required")
        column_guid = target_column_guid(args.instance, instance)
        if column_guid is None:
            raise ValueError("could not determine target column GUID")

        repaired_flowsheet = args.work_dir / "repaired.dwxmz"
        repaired_run = args.work_dir / "repaired_run.json"
        calculated_flowsheet = args.work_dir / "repaired_calculated.dwxmz"

        executor_timeout_sec = getattr(args, "executor_timeout_sec", DEFAULT_EXECUTOR_TIMEOUT_SEC)
        dwsim_timeout_sec = getattr(args, "dwsim_timeout_sec", DEFAULT_DWSIM_TIMEOUT_SEC)

        report["executor"] = {
            **apply_repair_action(
                instance_ref(args.instance, faulty_ref),
                repaired_flowsheet,
                args.repair_output_json,
                executor_timeout_sec,
            ),
            "repaired_flowsheet": str(repaired_flowsheet),
        }
        if not report["executor"]["success"]:
            report["error_stage"] = "executor_timeout" if report["executor"].get("timed_out") else "executor"
            return report, 1

        report["dwsim"] = {
            **run_repaired_metrics(repaired_flowsheet, repaired_run, calculated_flowsheet, column_guid, dwsim_timeout_sec),
            "repaired_run": str(repaired_run),
            "calculated_flowsheet": str(calculated_flowsheet),
        }
        if not report["dwsim"]["success"]:
            report["error_stage"] = "dwsim_timeout" if report["dwsim"].get("timed_out") else "dwsim_metrics"
            return report, 1

        run = load_json(repaired_run)
        target_metric, criteria, executable_success = evaluate_success_criteria(run, instance_target(instance))
        report["target_metric"] = target_metric
        report["success_criteria"] = criteria
        report["pipeline_success"] = True
        report["executable_success"] = executable_success
        report["error_stage"] = None
        if args.require_success and not executable_success:
            return report, 1
        return report, 0
    except Exception as exc:  # noqa: BLE001
        report["error_stage"] = report.get("error_stage") or "evaluation"
        report["error"] = str(exc)
        return report, 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", default=DEFAULT_INSTANCE, type=Path)
    parser.add_argument("--repair-output-json", required=True, type=Path)
    parser.add_argument("--work-dir", default=DEFAULT_WORK_DIR, type=Path)
    parser.add_argument("--report-output", type=Path)
    parser.add_argument("--executor-timeout-sec", default=DEFAULT_EXECUTOR_TIMEOUT_SEC, type=int)
    parser.add_argument("--dwsim-timeout-sec", default=DEFAULT_DWSIM_TIMEOUT_SEC, type=int)
    parser.add_argument("--require-success", action="store_true")
    args = parser.parse_args()

    report_output = args.report_output or args.work_dir / "evaluation_report.json"
    report, exit_code = evaluate(args, report_output)
    write_json(report_output, report)
    print(f"Wrote repair evaluation report to {report_output}")
    if report.get("pipeline_success"):
        metric = report.get("target_metric") or {}
        print(
            "Repair evaluation completed; "
            f"executable_success={report.get('executable_success')} "
            f"target_value={metric.get('value')} target_min={metric.get('minimum')}"
        )
    else:
        print(f"Repair evaluation failed at {report.get('error_stage')}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
