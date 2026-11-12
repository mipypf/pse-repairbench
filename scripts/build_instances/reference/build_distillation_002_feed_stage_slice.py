#!/usr/bin/env python3
"""Build the distillation_002 feed-stage release slice after a fault sweep."""

from __future__ import annotations

import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from builder_common import (
    absolute_ref,
    compact_candidate_result,
    component_metric,
    extract_source_metadata,
    gold_proximity,
    is_successful_run,
    load_json,
    read_inner_dwsim_from_curated_zip,
    run_apply_repair_actions,
    run_generate_llm_input,
    run_metrics,
    set_column_feed_stage,
    sha256,
    target_candidates,
    update_dwxmz,
    write_json,
    write_log,
    write_parameters,
    write_stream_table,
    write_topology,
)


INSTANCE_ID = "distillation_002_feed_stage_single"
SOURCE_ARCHIVE = Path(
    "curated_data/dwsim_headless_successes/distillation/"
    "002_air_liquefaction_using_linde_single_column_system.zip"
)
SOURCE_NAME = "FOSSEE DWSIM Flowsheeting Project: Air Liquefaction using Linde Single Column System"
COLUMN_GUID = "DC-84eedf9c-acf3-4dfc-8675-2245dc73de75"
COLUMN_TAG = "DC-01"
BASE_FEED_STAGE = 3
FAULT_FEED_STAGES = (1, 2, 4, 5)

SCRATCH_DIR = Path(".tmp/distillation_002_feed_stage_probe")
FORMAL_TMP_DIR = SCRATCH_DIR / "formal_runs"
INSTANCE_DIR = Path("instances/seed") / INSTANCE_ID
HIDDEN_DIR = INSTANCE_DIR / "hidden"
PUBLIC_DIR = INSTANCE_DIR / "public"
INSTANCE_PATH = INSTANCE_DIR / "instance.json"
TARGET_PARAMETER = {"namespace": "column_configuration", "name": "feed_stage"}


def set_feed_stage(source: Path, target: Path, stage_number: int) -> None:
    update_dwxmz(source, target, lambda tree: set_column_feed_stage(tree, COLUMN_GUID, stage_number))


def evaluate_fault_candidate(
    stage_number: int,
    base_run: dict[str, Any],
    faulty_run: dict[str, Any],
    repaired_run: dict[str, Any],
) -> list[dict[str, Any]]:
    if not (is_successful_run(base_run) and is_successful_run(faulty_run) and is_successful_run(repaired_run)):
        return []

    valid: list[dict[str, Any]] = []
    for candidate in target_candidates(base_run):
        tag = candidate["stream_tag"]
        component = candidate["component"]
        target = candidate["product_mole_fraction_min"]
        faulty_value = component_metric(faulty_run, tag, component)
        repaired_value = component_metric(repaired_run, tag, component)
        if faulty_value is None or repaired_value is None:
            continue
        if faulty_value < target <= repaired_value:
            valid.append(
                {
                    **candidate,
                    "fault_feed_stage": stage_number,
                    "faulty_mole_fraction": faulty_value,
                    "repaired_mole_fraction": repaired_value,
                    "purity_drop": candidate["base_mole_fraction"] - faulty_value,
                }
            )
    return valid


def write_problem(target: dict[str, Any], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    threshold = f"{target['product_mole_fraction_min']:.2f}"
    text = f"""# Repair Task: Distillation Column Feed Stage

The DWSIM air-liquefaction flowsheet runs headlessly, but the selected product stream misses its purity target.

Adjust only the feed stage for column `{COLUMN_TAG}` / GUID `{COLUMN_GUID}`. Propose a structured repair action so that `{target['component']}` mole fraction in material stream `{target['stream_tag']}` is at least `{threshold}` after rerunning the flowsheet.

Expected repair action type: `set_unit_parameter`.
"""
    output_path.write_text(text, encoding="utf-8")


def gold_repair_action() -> dict[str, Any]:
    return {
        "type": "set_unit_parameter",
        "target": {"kind": "unit_operation", "guid": COLUMN_GUID, "tag": COLUMN_TAG},
        "parameter": TARGET_PARAMETER,
        "value": BASE_FEED_STAGE,
        "unit": None,
    }


def write_mock_llm_output(output_path: Path) -> None:
    write_json(
        output_path,
        {
            "diagnosis": "The product purity target is missed because the distillation column feed stage is misplaced.",
            "repair_actions": [gold_repair_action()],
            "rationale": "Restoring the feed to the validated base stage recovers the selected oxygen product purity target.",
        },
    )


def build_instance(
    base_path: Path,
    selected: dict[str, Any],
    source_entry: str,
    candidate_summaries: list[dict[str, Any]],
) -> None:
    HIDDEN_DIR.mkdir(parents=True, exist_ok=True)
    PUBLIC_DIR.mkdir(parents=True, exist_ok=True)
    FORMAL_TMP_DIR.mkdir(parents=True, exist_ok=True)

    formal_base = HIDDEN_DIR / "base.dwxmz"
    formal_faulty = PUBLIC_DIR / "faulty.dwxmz"
    repaired_flowsheet = HIDDEN_DIR / "repaired.dwxmz"
    mock_output_path = HIDDEN_DIR / "mock_llm_output.json"
    problem_path = PUBLIC_DIR / "problem.md"
    llm_input_path = PUBLIC_DIR / "llm_input.md"
    llm_context_path = FORMAL_TMP_DIR / "llm_input_context.json"

    shutil.copyfile(base_path, formal_base)
    set_feed_stage(formal_base, formal_faulty, int(selected["fault_feed_stage"]))

    base_run = run_metrics(formal_base, HIDDEN_DIR / "base_run.json", FORMAL_TMP_DIR / "base_calculated.dwxmz", COLUMN_GUID)
    faulty_run = run_metrics(
        formal_faulty,
        HIDDEN_DIR / "faulty_run.json",
        FORMAL_TMP_DIR / "faulty_calculated.dwxmz",
        COLUMN_GUID,
    )

    target = {
        "stream_tag": selected["stream_tag"],
        "stream_id": selected["stream_id"],
        "component": selected["component"],
        "product_mole_fraction_min": selected["product_mole_fraction_min"],
    }

    write_topology(
        formal_faulty,
        PUBLIC_DIR / "topology.json",
        {"kind": "unit_operation", "guid": COLUMN_GUID, "tag": COLUMN_TAG},
        "Topology extracted from the faulty flowsheet after feed-stage injection.",
    )
    write_parameters(faulty_run, target, PUBLIC_DIR / "parameters.json", TARGET_PARAMETER)
    write_stream_table(faulty_run, PUBLIC_DIR / "streams.csv")
    write_log(faulty_run, target, PUBLIC_DIR / "log.txt")
    write_problem(target, problem_path)

    write_json(
        llm_context_path,
        {
            "id": INSTANCE_ID,
            "process_category": "distillation",
            "reasoning_class": "P_parameter",
            "faulty_flowsheet": absolute_ref(formal_faulty),
            "problem_statement": absolute_ref(problem_path),
            "observations": {
                "topology": absolute_ref(PUBLIC_DIR / "topology.json"),
                "parameters": absolute_ref(PUBLIC_DIR / "parameters.json"),
                "simulator_log": absolute_ref(PUBLIC_DIR / "log.txt"),
                "stream_table": absolute_ref(PUBLIC_DIR / "streams.csv"),
            },
            "gold_repair_actions": [
                {
                    "type": "set_unit_parameter",
                    "target": {"kind": "unit_operation", "guid": COLUMN_GUID},
                    "parameter": TARGET_PARAMETER,
                }
            ],
            "success_criteria": {
                "converged": True,
                "no_fatal_error": True,
                "target_stream_tag": target["stream_tag"],
                "target_component": target["component"],
                "product_mole_fraction_min": target["product_mole_fraction_min"],
            },
        },
    )
    run_generate_llm_input(llm_context_path, llm_input_path)

    write_mock_llm_output(mock_output_path)
    run_apply_repair_actions(formal_faulty, repaired_flowsheet, mock_output_path)
    repaired_run = run_metrics(
        repaired_flowsheet,
        HIDDEN_DIR / "repaired_run.json",
        FORMAL_TMP_DIR / "repaired_calculated.dwxmz",
        COLUMN_GUID,
    )

    metrics_report = {
        "instance_id": INSTANCE_ID,
        "repairable": True,
        "selection_rule": "largest base-to-faulty target mole fraction drop among successful base/faulty/repaired runs",
        "source_archive": str(SOURCE_ARCHIVE),
        "target": target,
        "base": {
            "feed_stage": base_run.get("column", {}).get("feed_stage"),
            "target_mole_fraction": component_metric(base_run, target["stream_tag"], target["component"]),
        },
        "faulty": {
            "feed_stage": faulty_run.get("column", {}).get("feed_stage"),
            "target_mole_fraction": component_metric(faulty_run, target["stream_tag"], target["component"]),
        },
        "repaired": {
            "feed_stage": repaired_run.get("column", {}).get("feed_stage"),
            "target_mole_fraction": component_metric(repaired_run, target["stream_tag"], target["component"]),
        },
        "gold_repair_action": gold_repair_action(),
        "gold_proximity": gold_proximity(load_json(mock_output_path)["repair_actions"][0], gold_repair_action()),
        "candidate_results": candidate_summaries,
    }
    base_value = metrics_report["base"]["target_mole_fraction"]
    faulty_value = metrics_report["faulty"]["target_mole_fraction"]
    if isinstance(base_value, (int, float)) and isinstance(faulty_value, (int, float)):
        metrics_report["purity_drop"] = base_value - faulty_value
    write_json(HIDDEN_DIR / "metrics_report.json", metrics_report)

    if not (
        is_successful_run(base_run)
        and is_successful_run(faulty_run)
        and is_successful_run(repaired_run)
        and metrics_report["base"]["feed_stage"] == BASE_FEED_STAGE
        and metrics_report["faulty"]["feed_stage"] == selected["fault_feed_stage"]
        and metrics_report["repaired"]["feed_stage"] == BASE_FEED_STAGE
        and metrics_report["faulty"]["target_mole_fraction"] < target["product_mole_fraction_min"]
        and metrics_report["repaired"]["target_mole_fraction"] >= target["product_mole_fraction_min"]
    ):
        raise RuntimeError("formal artifact rerun did not satisfy selected repairability criteria")

    source = extract_source_metadata(formal_base, SOURCE_ARCHIVE, source_entry, SOURCE_NAME, base_run)
    instance = {
        "id": INSTANCE_ID,
        "process_category": "distillation",
        "reasoning_class": "P_parameter",
        "base_flowsheet": "hidden/base.dwxmz",
        "faulty_flowsheet": "public/faulty.dwxmz",
        "problem_statement": "public/problem.md",
        "llm_input": "public/llm_input.md",
        "mock_llm_output": "hidden/mock_llm_output.json",
        "fault_type": "column_feed_stage_error",
        "fault_severity": "medium",
        "fault_count": 1,
        "leakage_flags": [],
        "observations": {
            "topology": "public/topology.json",
            "parameters": "public/parameters.json",
            "simulator_log": "public/log.txt",
            "stream_table": "public/streams.csv",
        },
        "run_artifacts": {
            "base_run": "hidden/base_run.json",
            "faulty_run": "hidden/faulty_run.json",
            "repaired_run": "hidden/repaired_run.json",
            "metrics_report": "hidden/metrics_report.json",
        },
        "gold_repair_actions": [
            {
                **gold_repair_action(),
                "rationale": "Restore the distillation column feed to the base stage that satisfies the selected product purity target.",
            }
        ],
        "hints": [
            {
                "level": 1,
                "type": "subsystem",
                "message": "The abnormal behavior is localized in the distillation column.",
            },
            {
                "level": 3,
                "type": "target_object",
                "target": COLUMN_GUID,
                "message": "Check whether the column feed location is consistent with the requested product purity.",
            },
            {
                "level": 5,
                "type": "direct_repair",
                "target": COLUMN_GUID,
                "message": f"Set the feed stage of {COLUMN_TAG} to {BASE_FEED_STAGE}.",
            },
        ],
        "source": source,
        "reproducibility": {
            "base_flowsheet_sha256": sha256(formal_base),
            "faulty_flowsheet_sha256": sha256(formal_faulty),
            "fault_injector_version": "build_distillation_002_feed_stage_slice.py:1",
            "observation_extractor_version": "builder_common.py:1;generate_llm_input.py:1",
            "executor_version": "apply_repair_actions.py:2",
            "dwsim_runner_version": "dwsim_metrics_worker.ps1:2",
            "evaluator_version": "builder_common.py:1",
        },
        "success_criteria": {
            "converged": True,
            "no_fatal_error": True,
            "target_stream_tag": target["stream_tag"],
            "target_component": target["component"],
            "product_mole_fraction_min": target["product_mole_fraction_min"],
        },
    }
    write_json(INSTANCE_PATH, instance)


def main() -> int:
    if SCRATCH_DIR.exists():
        shutil.rmtree(SCRATCH_DIR)
    SCRATCH_DIR.mkdir(parents=True, exist_ok=True)

    base_path = SCRATCH_DIR / "base.dwxmz"
    source_entry = read_inner_dwsim_from_curated_zip(SOURCE_ARCHIVE, base_path)

    base_run = run_metrics(base_path, SCRATCH_DIR / "base_run.json", SCRATCH_DIR / "base_calculated.dwxmz", COLUMN_GUID)
    candidate_summaries: list[dict[str, Any]] = []
    valid_candidates: list[dict[str, Any]] = []

    for stage_number in FAULT_FEED_STAGES:
        faulty_path = SCRATCH_DIR / f"fault_feed_stage_{stage_number}.dwxmz"
        repaired_path = SCRATCH_DIR / f"repaired_feed_stage_{stage_number}.dwxmz"
        set_feed_stage(base_path, faulty_path, stage_number)
        set_feed_stage(faulty_path, repaired_path, BASE_FEED_STAGE)

        faulty_run = run_metrics(
            faulty_path,
            SCRATCH_DIR / f"fault_feed_stage_{stage_number}_run.json",
            SCRATCH_DIR / f"fault_feed_stage_{stage_number}_calculated.dwxmz",
            COLUMN_GUID,
        )
        repaired_run = run_metrics(
            repaired_path,
            SCRATCH_DIR / f"repaired_feed_stage_{stage_number}_run.json",
            SCRATCH_DIR / f"repaired_feed_stage_{stage_number}_calculated.dwxmz",
            COLUMN_GUID,
        )
        candidate_summaries.append(compact_candidate_result("fault_feed_stage", stage_number, faulty_run, repaired_run))
        valid_candidates.extend(evaluate_fault_candidate(stage_number, base_run, faulty_run, repaired_run))

    sweep_summary = {
        "source_archive": str(SOURCE_ARCHIVE),
        "source_entry": source_entry,
        "column_guid": COLUMN_GUID,
        "base_feed_stage": BASE_FEED_STAGE,
        "fault_feed_stages": list(FAULT_FEED_STAGES),
        "base_success": is_successful_run(base_run),
        "candidate_results": candidate_summaries,
        "valid_candidates": valid_candidates,
    }

    if not valid_candidates:
        write_json(SCRATCH_DIR / "sweep_summary.json", sweep_summary)
        print(f"No clean feed-stage degradation case found. See {SCRATCH_DIR / 'sweep_summary.json'}")
        return 1

    selected = sorted(valid_candidates, key=lambda item: item["purity_drop"], reverse=True)[0]
    sweep_summary["selected"] = selected
    write_json(SCRATCH_DIR / "sweep_summary.json", sweep_summary)
    build_instance(base_path, selected, source_entry, candidate_summaries)

    print(f"Built {INSTANCE_ID}")
    print(f"Selected fault feed stage: {selected['fault_feed_stage']}")
    print(f"Target: {selected['component']} in {selected['stream_tag']} >= {selected['product_mole_fraction_min']:.2f}")
    print(f"Sweep summary: {SCRATCH_DIR / 'sweep_summary.json'}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
