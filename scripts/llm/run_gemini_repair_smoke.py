#!/usr/bin/env python3
"""Run a live LLM repair smoke test for the distillation_002 slice."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

from generate_llm_output import DEFAULT_ENV_FILE, DEFAULT_MODEL, DEFAULT_PROVIDER, PROMPT_MODES, generate_llm_output, load_json, write_json
from llm_provider import PROVIDERS


DEFAULT_INSTANCE = Path("instances/seed/distillation_002_reflux_ratio_single/instance.json")
DEFAULT_WORK_DIR = Path(".tmp/distillation_002_gemini_live")
DEFAULT_LLM_OUTPUT = DEFAULT_WORK_DIR / "gemini_llm_output.json"
DEFAULT_SUMMARY = DEFAULT_WORK_DIR / "gemini_repair_smoke_summary.json"
APPLY_REPAIR_ACTIONS = Path("scripts/dwsim/apply_repair_actions.py")
METRIC_WORKER = Path("scripts/dwsim/dwsim_metrics_worker.ps1")


def repo_root() -> Path:
    return Path.cwd()


def instance_ref(instance_path: Path, ref: str) -> Path:
    return instance_path.parent / ref


def compact_completed_process(completed: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    return {
        "returncode": completed.returncode,
        "stdout_tail": completed.stdout[-2000:] if completed.stdout else "",
        "stderr_tail": completed.stderr[-2000:] if completed.stderr else "",
    }


def run_command(command: list[str], timeout: int = 180) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        command,
        cwd=repo_root(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=timeout,
        check=False,
    )


def instance_target(instance: dict[str, Any]) -> dict[str, Any]:
    success = instance.get("success_criteria")
    if not isinstance(success, dict):
        raise ValueError("instance.success_criteria must be an object")
    target_metric = success.get("target_metric")
    if isinstance(target_metric, dict):
        threshold = target_metric.get("threshold")
        if threshold is None:
            threshold = target_metric.get("max") if target_metric.get("direction") == "max" else target_metric.get("min")
        target = {
            "family": target_metric.get("family"),
            "stream_tag": target_metric.get("stream_tag") or target_metric.get("stream"),
            "component": target_metric.get("component"),
            "metric": target_metric.get("metric") or "mole_fraction",
            "direction": target_metric.get("direction") or "min",
            "threshold": threshold,
        }
        missing = [key for key in ("stream_tag", "metric", "direction", "threshold") if target.get(key) is None]
        if missing:
            raise ValueError(f"missing target field(s): {', '.join(missing)}")
        return target
    target = {
        "stream_tag": success.get("target_stream_tag"),
        "component": success.get("target_component"),
        "metric": "mole_fraction",
        "direction": "min",
        "threshold": success.get("product_mole_fraction_min"),
    }
    missing = [key for key, value in target.items() if value is None]
    if missing:
        raise ValueError(f"missing target field(s): {', '.join(missing)}")
    return target


def target_column_guid(instance_path: Path, instance: dict[str, Any]) -> str:
    observations = instance.get("observations")
    if not isinstance(observations, dict) or not isinstance(observations.get("parameters"), str):
        raise ValueError("instance observations must include parameters")
    parameters = load_json(instance_ref(instance_path, observations["parameters"]))
    unit = parameters.get("target_unit") if isinstance(parameters, dict) else None
    guid = unit.get("guid") if isinstance(unit, dict) else None
    if isinstance(guid, str) and guid:
        return guid
    column = parameters.get("target_column") if isinstance(parameters, dict) else None
    guid = column.get("guid") if isinstance(column, dict) else None
    if not isinstance(guid, str) or not guid:
        raise ValueError("target_column.guid missing from parameters")
    return guid


def target_mole_fraction(run: dict[str, Any], stream_tag: str, component: str) -> float | None:
    for stream in run.get("streams", []):
        if stream.get("tag") != stream_tag:
            continue
        value = stream.get("compounds", {}).get(component, {}).get("mole_fraction")
        return float(value) if isinstance(value, (int, float)) else None
    return None


def target_metric_value(run: dict[str, Any], target: dict[str, Any]) -> float | None:
    stream_tag = target.get("stream_tag")
    metric = target.get("metric")
    component = target.get("component")
    if not isinstance(stream_tag, str) or not isinstance(metric, str):
        return None
    for stream in run.get("streams", []):
        if not isinstance(stream, dict) or stream.get("tag") != stream_tag:
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


def target_repaired(value: float | None, target: dict[str, Any]) -> bool:
    threshold = target.get("threshold")
    if not isinstance(value, (int, float)) or not isinstance(threshold, (int, float)):
        return False
    if target.get("direction") == "max":
        return value <= threshold
    return value >= threshold


def apply_repair_action(faulty_flowsheet: Path, repaired_flowsheet: Path, llm_output: Path) -> dict[str, Any]:
    command = [
        sys.executable,
        str(APPLY_REPAIR_ACTIONS),
        "--input-flowsheet",
        str(faulty_flowsheet),
        "--repair-output",
        str(repaired_flowsheet),
        "--repair-actions-json",
        str(llm_output),
    ]
    completed = run_command(command, timeout=60)
    result = compact_completed_process(completed)
    if completed.returncode != 0:
        raise RuntimeError(f"repair action executor failed: {json.dumps(result, ensure_ascii=False)}")
    return result


def run_repaired_metrics(repaired_flowsheet: Path, repaired_run: Path, calculated_flowsheet: Path, column_guid: str) -> dict[str, Any]:
    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(METRIC_WORKER),
        "-SimPath",
        str(repaired_flowsheet),
        "-ResultJsonPath",
        str(repaired_run),
        "-SavePath",
        str(calculated_flowsheet),
        "-ColumnGuid",
        column_guid,
    ]
    completed = run_command(command, timeout=180)
    result = compact_completed_process(completed)
    if completed.returncode != 0:
        raise RuntimeError(f"DWSIM metrics worker failed: {json.dumps(result, ensure_ascii=False)}")
    if not repaired_run.exists():
        raise RuntimeError(f"DWSIM metrics worker did not create {repaired_run}")
    return result


def base_summary(args: argparse.Namespace, instance: dict[str, Any] | None = None) -> dict[str, Any]:
    summary: dict[str, Any] = {
        "pipeline_success": False,
        "repair_success": False,
        "provider": args.provider,
        "model": args.model,
        "llm_output": str(args.llm_output),
        "summary_output": str(args.summary_output),
        "work_dir": str(args.work_dir),
        "error_stage": None,
        "error": None,
    }
    if instance is not None:
        summary["instance_id"] = instance.get("id")
    return summary


def run_smoke(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    instance = load_json(args.instance)
    if not isinstance(instance, dict):
        raise ValueError("instance file must contain a JSON object")
    summary = base_summary(args, instance)
    try:
        args.work_dir.mkdir(parents=True, exist_ok=True)

        observations = instance.get("observations")
        if not isinstance(observations, dict):
            raise ValueError("instance.observations must be an object")
        llm_input_ref = instance.get("llm_input")
        faulty_ref = instance.get("faulty_flowsheet")
        parameters_ref = observations.get("parameters")
        if not all(isinstance(ref, str) for ref in (llm_input_ref, faulty_ref, parameters_ref)):
            raise ValueError("instance must include llm_input, faulty_flowsheet, and observations.parameters")

        target = instance_target(instance)
        column_guid = target_column_guid(args.instance, instance)
        repaired_flowsheet = args.work_dir / "gemini_repaired.dwxmz"
        repaired_run = args.work_dir / "gemini_repaired_run.json"
        calculated_flowsheet = args.work_dir / "gemini_repaired_calculated.dwxmz"

        summary.update(
            {
                "target_stream_tag": target["stream_tag"],
                "target_component": target.get("component"),
                "target_metric": target.get("metric"),
                "target_direction": target.get("direction"),
                "target_threshold": target.get("threshold"),
                "target_min": target.get("threshold") if target.get("direction") == "min" else None,
                "target_max": target.get("threshold") if target.get("direction") == "max" else None,
                "repaired_flowsheet": str(repaired_flowsheet),
                "repaired_run": str(repaired_run),
            }
        )

        summary["error_stage"] = "llm_output"
        generate_llm_output(
            llm_input_path=instance_ref(args.instance, llm_input_ref),
            output_path=args.llm_output,
            parameters_path=instance_ref(args.instance, parameters_ref),
            model=args.model,
            env_file=args.env_file,
            prompt_mode=args.prompt_mode,
            provider=args.provider,
        )

        summary["error_stage"] = "executor"
        summary["executor"] = apply_repair_action(instance_ref(args.instance, faulty_ref), repaired_flowsheet, args.llm_output)

        summary["error_stage"] = "dwsim_metrics"
        summary["dwsim_metrics"] = run_repaired_metrics(repaired_flowsheet, repaired_run, calculated_flowsheet, column_guid)

        repaired = load_json(repaired_run)
        target_value = target_metric_value(repaired, target)
        summary["pipeline_success"] = True
        summary["target_value"] = target_value
        summary["repair_success"] = target_repaired(target_value, target)
        summary["error_stage"] = None

        if args.require_repair and not summary["repair_success"]:
            return summary, 1
        return summary, 0
    except Exception as exc:  # noqa: BLE001
        summary["error"] = str(exc)
        return summary, 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", default=DEFAULT_INSTANCE, type=Path)
    parser.add_argument("--llm-output", default=DEFAULT_LLM_OUTPUT, type=Path)
    parser.add_argument("--work-dir", default=DEFAULT_WORK_DIR, type=Path)
    parser.add_argument("--summary-output", default=DEFAULT_SUMMARY, type=Path)
    parser.add_argument("--provider", choices=sorted(PROVIDERS), default=DEFAULT_PROVIDER)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE, type=Path)
    parser.add_argument("--prompt-mode", choices=sorted(PROMPT_MODES), default="oracle-parameter")
    parser.add_argument("--require-repair", action="store_true")
    args = parser.parse_args()

    summary: dict[str, Any]
    exit_code: int
    try:
        summary, exit_code = run_smoke(args)
    except Exception as exc:  # noqa: BLE001
        summary = base_summary(args)
        summary["error"] = str(exc)
        exit_code = 1

    args.summary_output.parent.mkdir(parents=True, exist_ok=True)
    write_json(args.summary_output, summary)
    print(f"Wrote {args.provider} repair smoke summary to {args.summary_output}")
    if summary.get("pipeline_success"):
        print(
            f"{args.provider} repair smoke pipeline completed; "
            f"repair_success={summary.get('repair_success')} "
            f"target_value={summary.get('target_value')} target_threshold={summary.get('target_threshold')}"
        )
    else:
        print(f"{args.provider} repair smoke pipeline failed at {summary.get('error_stage')}", file=sys.stderr)
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
