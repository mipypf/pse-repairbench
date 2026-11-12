#!/usr/bin/env python3
"""Discover v0.1 fault specs by perturbing supported column parameters."""

from __future__ import annotations

import argparse
import math
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_from_fault_spec import build_instance, collect_allowed_repair_actions, parameter_run_value  # noqa: E402
from builder_common import (  # noqa: E402
    graphic_tags,
    is_successful_run,
    parse_stage_number,
    read_dwxmz_xml,
    read_inner_dwsim_from_curated_zip,
    run_metrics,
    text_of,
    write_json,
)
from build_from_fault_spec import apply_fault_parameter  # noqa: E402
from repair_registry import (  # noqa: E402
    REGISTRY,
    entry_for_parameter,
    entry_supports_unit_type,
    pair_from_target_and_entry,
    required_state_mismatches,
)


DEFAULT_OUTPUT_DIR = Path(".tmp/fault_discovery")
REFLUX_MULTIPLIERS = (0.1, 0.3, 0.5, 0.7, 0.9, 1.2, 1.5)
FEED_STAGE_DELTAS = (-4, -3, -2, -1, 1, 2, 3, 4)
FEED_STAGE_POSITIONS = (0.2, 0.35, 0.5, 0.65, 0.8)
THRESHOLD_ALPHA = 0.7
COMPOSITION_ABS_MIN_DELTA = 0.01
FLOW_REL_MIN_DELTA = 0.05
PRESSURE_REL_MIN_DELTA = 0.05
TEMPERATURE_ABS_MIN_DELTA = 1.0
TEMPERATURE_REL_MIN_DELTA = 0.01
COMPONENT_FLOW_EPS = 1e-8
STREAM_FLOW_EPS = 1e-8


def repo_root() -> Path:
    return Path.cwd()


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else repo_root() / path


def ensure_output_dir(path: Path, overwrite: bool) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return
    tmp_root = (repo_root() / ".tmp").resolve()
    try:
        inside_tmp = path.resolve().is_relative_to(tmp_root)
    except ValueError:
        inside_tmp = False
    if not overwrite and not inside_tmp:
        raise ValueError(f"output directory already exists outside .tmp; pass --overwrite to replace it: {path}")
    shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def prepare_base_flowsheet(source_flowsheet: Path, target: Path) -> tuple[Path, str]:
    source = resolve_repo_path(source_flowsheet)
    if not source.exists():
        raise FileNotFoundError(f"source_flowsheet not found: {source}")
    target.parent.mkdir(parents=True, exist_ok=True)
    if source.suffix.lower() == ".zip":
        source_entry = read_inner_dwsim_from_curated_zip(source, target)
    elif source.suffix.lower() in {".dwxmz", ".dwxml"}:
        shutil.copyfile(source, target)
        source_entry = source.name
    else:
        raise ValueError("source_flowsheet must be .zip, .dwxmz, or .dwxml")
    return source, source_entry


def slug(value: str) -> str:
    clean = []
    for char in value.lower():
        if char.isalnum():
            clean.append(char)
        elif clean and clean[-1] != "_":
            clean.append("_")
    return "".join(clean).strip("_") or "source"


def numeric_close(left: Any, right: Any, tolerance: float = 1e-9) -> bool:
    if isinstance(left, (int, float)) and isinstance(right, (int, float)):
        return math.isclose(float(left), float(right), rel_tol=tolerance, abs_tol=tolerance)
    return left == right


def distillation_columns(flowsheet: Path) -> list[dict[str, Any]]:
    tree, _xml_entry, _entries = read_dwxmz_xml(flowsheet)
    tags = graphic_tags(tree.getroot())
    simulation_objects = tree.getroot().find("SimulationObjects")
    if simulation_objects is None:
        return []
    columns: list[dict[str, Any]] = []
    for obj in simulation_objects:
        if text_of(obj, "Type") != "DWSIM.UnitOperations.UnitOperations.DistillationColumn":
            continue
        guid = text_of(obj, "Name")
        if not guid:
            continue
        stage_numbers: list[int] = []
        stages = obj.find("Stages")
        if stages is not None:
            for stage in stages:
                number = parse_stage_number(text_of(stage, "Name"))
                if isinstance(number, int) and number > 0:
                    stage_numbers.append(number)
        columns.append(
            {
                "kind": "unit_operation",
                "guid": guid,
                "tag": tags.get(guid, ""),
                "stage_numbers": sorted(set(stage_numbers)),
            }
        )
    return columns


def pressure_units(flowsheet: Path) -> list[dict[str, Any]]:
    entry = entry_for_parameter(("pressure_specification", "outlet_pressure"))
    tree, _xml_entry, _entries = read_dwxmz_xml(flowsheet)
    root = tree.getroot()
    tags = graphic_tags(root)
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        return []
    units: list[dict[str, Any]] = []
    for obj in simulation_objects:
        unit_type = text_of(obj, "Type")
        if not entry_supports_unit_type(entry, unit_type):
            continue
        if required_state_mismatches(entry, lambda name: text_of(obj, name)):
            continue
        guid = text_of(obj, "Name")
        if not guid:
            continue
        units.append(
            {
                "kind": "unit_operation",
                "guid": guid,
                "tag": tags.get(guid, ""),
                "type": unit_type,
            }
        )
    return units


def thermal_units(flowsheet: Path) -> list[dict[str, Any]]:
    entry = entry_for_parameter(("thermal_specification", "outlet_temperature"))
    tree, _xml_entry, _entries = read_dwxmz_xml(flowsheet)
    root = tree.getroot()
    tags = graphic_tags(root)
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        return []
    units: list[dict[str, Any]] = []
    for obj in simulation_objects:
        unit_type = text_of(obj, "Type")
        if not entry_supports_unit_type(entry, unit_type):
            continue
        if required_state_mismatches(entry, lambda name: text_of(obj, name)):
            continue
        guid = text_of(obj, "Name")
        if not guid:
            continue
        units.append(
            {
                "kind": "unit_operation",
                "guid": guid,
                "tag": tags.get(guid, ""),
                "type": unit_type,
            }
        )
    return units


def separator_units(flowsheet: Path, key: tuple[str, str]) -> list[dict[str, Any]]:
    entry = entry_for_parameter(key)
    tree, _xml_entry, _entries = read_dwxmz_xml(flowsheet)
    root = tree.getroot()
    tags = graphic_tags(root)
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        return []
    units: list[dict[str, Any]] = []
    for obj in simulation_objects:
        unit_type = text_of(obj, "Type")
        if not entry_supports_unit_type(entry, unit_type):
            continue
        if required_state_mismatches(entry, lambda name: text_of(obj, name)):
            continue
        guid = text_of(obj, "Name")
        if not guid:
            continue
        units.append(
            {
                "kind": "unit_operation",
                "guid": guid,
                "tag": tags.get(guid, ""),
                "type": unit_type,
            }
        )
    return units


def column_candidate_values(base_run: dict[str, Any], column: dict[str, Any]) -> list[dict[str, Any]]:
    candidate_values: list[dict[str, Any]] = []
    column_data = base_run.get("column") if isinstance(base_run.get("column"), dict) else {}

    reflux_ratio = column_data.get("reflux_ratio")
    if isinstance(reflux_ratio, (int, float)) and reflux_ratio > 0:
        seen_reflux: set[float] = set()
        for multiplier in REFLUX_MULTIPLIERS:
            value = float(reflux_ratio) * multiplier
            rounded = round(value, 12)
            if numeric_close(value, reflux_ratio) or rounded in seen_reflux:
                continue
            seen_reflux.add(rounded)
            candidate_values.append(
                {
                    "parameter": {"namespace": "column_specification", "name": "reflux_ratio"},
                    "fault_value": value,
                    "gold_value": float(reflux_ratio),
                    "candidate_label": f"reflux_x{multiplier:g}",
                }
            )

    feed_stage = column_data.get("feed_stage")
    valid_stages = column.get("stage_numbers") if isinstance(column.get("stage_numbers"), list) else []
    valid_stages = [stage for stage in valid_stages if isinstance(stage, int) and stage > 0]
    if isinstance(feed_stage, int) and valid_stages:
        seen_stages: set[int] = set()
        for delta in FEED_STAGE_DELTAS:
            stage = feed_stage + delta
            if stage in valid_stages and stage != feed_stage:
                seen_stages.add(stage)
        for position in FEED_STAGE_POSITIONS:
            index = round((len(valid_stages) - 1) * position)
            stage = valid_stages[max(0, min(index, len(valid_stages) - 1))]
            if stage != feed_stage:
                seen_stages.add(stage)
        for stage in sorted(seen_stages):
            candidate_values.append(
                {
                    "parameter": {"namespace": "column_configuration", "name": "feed_stage"},
                    "fault_value": stage,
                    "gold_value": feed_stage,
                    "candidate_label": f"feed_stage_{stage}",
                }
            )

    return candidate_values


def pressure_candidate_values(base_run: dict[str, Any]) -> list[dict[str, Any]]:
    entry = entry_for_parameter(("pressure_specification", "outlet_pressure"))
    baseline = parameter_run_value(base_run, ("pressure_specification", "outlet_pressure"))
    if not isinstance(baseline, (int, float)) or baseline <= 0:
        return []
    candidate_values: list[dict[str, Any]] = []
    seen: set[float] = set()
    for multiplier in entry["discovery_perturbation"]["values"]:
        value = float(baseline) * float(multiplier)
        if value <= 0:
            continue
        rounded = round(value, 6)
        if numeric_close(value, baseline) or rounded in seen:
            continue
        seen.add(rounded)
        candidate_values.append(
            {
                "parameter": {"namespace": "pressure_specification", "name": "outlet_pressure"},
                "fault_value": value,
                "gold_value": float(baseline),
                "unit": "Pa",
                "candidate_label": f"outlet_pressure_x{multiplier:g}",
            }
        )
    return candidate_values


def thermal_candidate_values(base_run: dict[str, Any]) -> list[dict[str, Any]]:
    entry = entry_for_parameter(("thermal_specification", "outlet_temperature"))
    baseline = parameter_run_value(base_run, ("thermal_specification", "outlet_temperature"))
    if not isinstance(baseline, (int, float)) or baseline <= 0:
        return []
    candidate_values: list[dict[str, Any]] = []
    seen: set[float] = set()
    for offset in entry["discovery_perturbation"]["values"]:
        value = float(baseline) + float(offset)
        if value <= 0:
            continue
        rounded = round(value, 6)
        if numeric_close(value, baseline) or rounded in seen:
            continue
        seen.add(rounded)
        candidate_values.append(
            {
                "parameter": {"namespace": "thermal_specification", "name": "outlet_temperature"},
                "fault_value": value,
                "gold_value": float(baseline),
                "unit": "K",
                "candidate_label": f"outlet_temperature_{offset:+g}K",
            }
        )
    return candidate_values


def separator_pressure_candidate_values(base_run: dict[str, Any]) -> list[dict[str, Any]]:
    entry = entry_for_parameter(("separator_specification", "pressure"))
    baseline = parameter_run_value(base_run, ("separator_specification", "pressure"))
    if not isinstance(baseline, (int, float)) or baseline <= 0:
        return []
    candidate_values: list[dict[str, Any]] = []
    seen: set[float] = set()
    for multiplier in entry["discovery_perturbation"]["values"]:
        value = float(baseline) * float(multiplier)
        if value <= 0:
            continue
        rounded = round(value, 6)
        if numeric_close(value, baseline) or rounded in seen:
            continue
        seen.add(rounded)
        candidate_values.append(
            {
                "parameter": {"namespace": "separator_specification", "name": "pressure"},
                "fault_value": value,
                "gold_value": float(baseline),
                "unit": "Pa",
                "candidate_label": f"separator_pressure_x{multiplier:g}",
            }
        )
    return candidate_values


def separator_temperature_candidate_values(base_run: dict[str, Any]) -> list[dict[str, Any]]:
    entry = entry_for_parameter(("separator_specification", "temperature"))
    baseline = parameter_run_value(base_run, ("separator_specification", "temperature"))
    if not isinstance(baseline, (int, float)) or baseline <= 0:
        return []
    candidate_values: list[dict[str, Any]] = []
    seen: set[float] = set()
    for offset in entry["discovery_perturbation"]["values"]:
        value = float(baseline) + float(offset)
        if value <= 0:
            continue
        rounded = round(value, 6)
        if numeric_close(value, baseline) or rounded in seen:
            continue
        seen.add(rounded)
        candidate_values.append(
            {
                "parameter": {"namespace": "separator_specification", "name": "temperature"},
                "fault_value": value,
                "gold_value": float(baseline),
                "unit": "K",
                "candidate_label": f"separator_temperature_{offset:+g}K",
            }
        )
    return candidate_values


def stream_by_key(run: dict[str, Any]) -> dict[str, dict[str, Any]]:
    streams: dict[str, dict[str, Any]] = {}
    for stream in run.get("streams", []):
        if not isinstance(stream, dict):
            continue
        for key in (stream.get("tag"), stream.get("id")):
            if isinstance(key, str) and key:
                streams[key] = stream
    return streams


def component_value(stream: dict[str, Any], component: str, metric: str) -> float | None:
    compounds = stream.get("compounds")
    if not isinstance(compounds, dict):
        return None
    metrics = compounds.get(component)
    if not isinstance(metrics, dict):
        return None
    value = metrics.get(metric)
    return float(value) if isinstance(value, (int, float)) else None


def stream_value(stream: dict[str, Any], metric: str) -> float | None:
    value = stream.get(metric)
    return float(value) if isinstance(value, (int, float)) else None


def direction_meets(value: float | None, direction: str, threshold: float) -> bool:
    if not isinstance(value, (int, float)):
        return False
    return value >= threshold if direction == "min" else value <= threshold


def direction_misses(value: float | None, direction: str, threshold: float) -> bool:
    if not isinstance(value, (int, float)):
        return False
    return value < threshold if direction == "min" else value > threshold


def direction_for_delta(baseline: float, faulty: float) -> str:
    return "min" if baseline > faulty else "max"


def interpolated_threshold(baseline: float, faulty: float) -> float:
    if baseline > faulty:
        return faulty + THRESHOLD_ALPHA * (baseline - faulty)
    return faulty - THRESHOLD_ALPHA * (faulty - baseline)


def relative_delta(baseline: float, faulty: float) -> float:
    return abs(baseline - faulty) / max(abs(baseline), 1e-12)


def closer_to_baseline(repaired: float, faulty: float, baseline: float) -> bool:
    return abs(repaired - baseline) < abs(faulty - baseline)


def candidate_metric(
    family: str,
    stream_tag: str,
    stream_id: str | None,
    component: str | None,
    metric: str,
    baseline: float,
    faulty: float,
    repaired: float,
    score: float,
    minimum_checks: dict[str, bool],
) -> dict[str, Any]:
    direction = direction_for_delta(baseline, faulty)
    threshold = interpolated_threshold(baseline, faulty)
    accepted = (
        all(minimum_checks.values())
        and direction_misses(faulty, direction, threshold)
        and direction_meets(repaired, direction, threshold)
        and closer_to_baseline(repaired, faulty, baseline)
    )
    rejection_reasons: list[str] = []
    for name, passed in minimum_checks.items():
        if not passed:
            rejection_reasons.append(f"{name}_below_minimum")
    if not direction_misses(faulty, direction, threshold):
        rejection_reasons.append("faulty_does_not_miss_threshold")
    if not direction_meets(repaired, direction, threshold):
        rejection_reasons.append("repaired_does_not_meet_threshold")
    if not closer_to_baseline(repaired, faulty, baseline):
        rejection_reasons.append("repaired_not_closer_to_baseline")
    result: dict[str, Any] = {
        "family": family,
        "stream_tag": stream_tag,
        "stream_id": stream_id,
        "stream_role": "terminal_material_stream",
        "metric": metric,
        "direction": direction,
        "threshold": threshold,
        "baseline_value": baseline,
        "faulty_value": faulty,
        "repaired_value": repaired,
        "score": score,
        "abs_delta": abs(baseline - faulty),
        "rel_delta": relative_delta(baseline, faulty),
        "threshold_alpha": THRESHOLD_ALPHA,
        "accepted": accepted,
        "rejection_reasons": rejection_reasons,
    }
    if component:
        result["component"] = component
    if direction == "min":
        result["min"] = threshold
    else:
        result["max"] = threshold
    return result


def terminal_stream_keys(run: dict[str, Any]) -> list[str]:
    keys: list[str] = []
    seen: set[str] = set()
    for stream in run.get("terminal_material_streams", []):
        if not isinstance(stream, dict):
            continue
        for key in (stream.get("tag"), stream.get("id")):
            if isinstance(key, str) and key and key not in seen:
                keys.append(key)
                seen.add(key)
                break
    return keys


def stream_display_key(stream: dict[str, Any]) -> str:
    tag = stream.get("tag")
    if isinstance(tag, str) and tag:
        return tag
    stream_id = stream.get("id")
    return str(stream_id) if isinstance(stream_id, str) and stream_id else ""


def composition_component_flow(stream: dict[str, Any], component: str, metric: str) -> float | None:
    flow_metric = "mass_flow" if metric == "mass_fraction" else "molar_flow"
    value = component_value(stream, component, flow_metric)
    if isinstance(value, (int, float)):
        return value
    fallback = component_value(stream, component, "molar_flow")
    if isinstance(fallback, (int, float)):
        return fallback
    return component_value(stream, component, "mass_flow")


def add_stream_metric_candidate(
    scored: list[dict[str, Any]],
    family: str,
    base_stream: dict[str, Any],
    faulty_stream: dict[str, Any],
    repaired_stream: dict[str, Any],
    metric: str,
    score: float,
    minimum_checks: dict[str, bool],
) -> None:
    baseline = stream_value(base_stream, metric)
    faulty = stream_value(faulty_stream, metric)
    repaired = stream_value(repaired_stream, metric)
    if not all(isinstance(value, (int, float)) for value in (baseline, faulty, repaired)):
        return
    if numeric_close(baseline, faulty, tolerance=1e-9):
        return
    stream_tag = stream_display_key(base_stream)
    if not stream_tag:
        return
    scored.append(
        candidate_metric(
            family,
            stream_tag,
            base_stream.get("id") if isinstance(base_stream.get("id"), str) else None,
            None,
            metric,
            baseline,
            faulty,
            repaired,
            score,
            minimum_checks,
        )
    )


def score_target_metrics(base_run: dict[str, Any], faulty_run: dict[str, Any], repaired_run: dict[str, Any]) -> list[dict[str, Any]]:
    base_streams = stream_by_key(base_run)
    faulty_streams = stream_by_key(faulty_run)
    repaired_streams = stream_by_key(repaired_run)
    scored: list[dict[str, Any]] = []
    for key in terminal_stream_keys(base_run):
        base_stream = base_streams.get(key)
        faulty_stream = faulty_streams.get(key)
        repaired_stream = repaired_streams.get(key)
        if base_stream is None or faulty_stream is None or repaired_stream is None:
            continue

        base_pressure = stream_value(base_stream, "pressure")
        faulty_pressure = stream_value(faulty_stream, "pressure")
        repaired_pressure = stream_value(repaired_stream, "pressure")
        if (
            isinstance(base_pressure, (int, float))
            and abs(base_pressure) > 1e-9
            and isinstance(faulty_pressure, (int, float))
            and isinstance(repaired_pressure, (int, float))
            and not numeric_close(base_pressure, faulty_pressure, tolerance=1e-6)
        ):
            add_stream_metric_candidate(
                scored,
                "terminal_pressure",
                base_stream,
                faulty_stream,
                repaired_stream,
                "pressure",
                relative_delta(base_pressure, faulty_pressure),
                {"pressure_rel_delta": relative_delta(base_pressure, faulty_pressure) >= PRESSURE_REL_MIN_DELTA},
            )

        for flow_metric in ("molar_flow", "mass_flow"):
            base_flow = stream_value(base_stream, flow_metric)
            faulty_flow = stream_value(faulty_stream, flow_metric)
            repaired_flow = stream_value(repaired_stream, flow_metric)
            if not all(isinstance(value, (int, float)) for value in (base_flow, faulty_flow, repaired_flow)):
                continue
            if abs(base_flow) <= STREAM_FLOW_EPS or numeric_close(base_flow, faulty_flow, tolerance=1e-12):
                continue
            rel = relative_delta(base_flow, faulty_flow)
            add_stream_metric_candidate(
                scored,
                "terminal_flow",
                base_stream,
                faulty_stream,
                repaired_stream,
                flow_metric,
                rel,
                {"flow_rel_delta": rel >= FLOW_REL_MIN_DELTA},
            )

        base_temperature = stream_value(base_stream, "temperature")
        faulty_temperature = stream_value(faulty_stream, "temperature")
        repaired_temperature = stream_value(repaired_stream, "temperature")
        if (
            isinstance(base_temperature, (int, float))
            and abs(base_temperature) > 1e-9
            and isinstance(faulty_temperature, (int, float))
            and isinstance(repaired_temperature, (int, float))
            and not numeric_close(base_temperature, faulty_temperature, tolerance=1e-9)
        ):
            abs_delta = abs(base_temperature - faulty_temperature)
            rel = relative_delta(base_temperature, faulty_temperature)
            add_stream_metric_candidate(
                scored,
                "terminal_temperature",
                base_stream,
                faulty_stream,
                repaired_stream,
                "temperature",
                abs_delta,
                {
                    "temperature_abs_delta": abs_delta >= TEMPERATURE_ABS_MIN_DELTA,
                    "temperature_rel_delta": rel >= TEMPERATURE_REL_MIN_DELTA,
                },
            )

        compounds = base_stream.get("compounds")
        if not isinstance(compounds, dict):
            continue
        for component in compounds:
            for fraction_metric in ("mole_fraction", "mass_fraction"):
                baseline = component_value(base_stream, component, fraction_metric)
                faulty = component_value(faulty_stream, component, fraction_metric)
                repaired = component_value(repaired_stream, component, fraction_metric)
                component_flow = composition_component_flow(base_stream, component, fraction_metric)
                if not all(isinstance(value, (int, float)) for value in (baseline, faulty, repaired, component_flow)):
                    continue
                if component_flow <= COMPONENT_FLOW_EPS or numeric_close(baseline, faulty, tolerance=1e-12):
                    continue
                abs_delta = abs(baseline - faulty)
                stream_tag = stream_display_key(base_stream)
                if not stream_tag:
                    continue
                scored.append(
                    candidate_metric(
                        "terminal_composition",
                        stream_tag,
                        base_stream.get("id") if isinstance(base_stream.get("id"), str) else None,
                        component,
                        fraction_metric,
                        baseline,
                        faulty,
                        repaired,
                        abs_delta,
                        {"composition_abs_delta": abs_delta >= COMPOSITION_ABS_MIN_DELTA},
                    )
                )
    return sorted(scored, key=lambda item: item["score"], reverse=True)


def candidate_spec(
    source_flowsheet: Path,
    source_name: str,
    source_slug: str,
    unit: dict[str, Any],
    candidate: dict[str, Any],
    target_metric: dict[str, Any],
    sequence: int,
    process_category: str,
    source_category: str | None,
    allowed_repair_actions: list[dict[str, Any]],
) -> dict[str, Any]:
    parameter = candidate["parameter"]
    name = parameter["name"]
    instance_id = f"{source_slug}_{slug(unit.get('tag') or unit['guid'])}_{name}_{sequence:03d}"
    return {
        "instance_id": instance_id,
        "source_flowsheet": str(source_flowsheet),
        "source_name": source_name,
        "source_category": source_category,
        "process_category": process_category,
        "reasoning_class": "P_parameter",
        "fault_type": f"discovered_{name}_error",
        "fault_severity": "medium",
        "allowed_repair_actions": allowed_repair_actions,
        "fault": {
            "target": {
                "kind": "unit_operation",
                "guid": unit["guid"],
                "tag": unit.get("tag"),
            },
            "parameter": parameter,
            "fault_value": candidate["fault_value"],
            "gold_value": candidate["gold_value"],
            "unit": candidate.get("repair_unit"),
        },
        "target_metric": {
            "family": target_metric["family"],
            "stream": target_metric["stream_tag"],
            "stream_tag": target_metric["stream_tag"],
            "stream_id": target_metric.get("stream_id"),
            "stream_role": target_metric.get("stream_role"),
            "component": target_metric.get("component"),
            "metric": target_metric["metric"],
            "direction": target_metric["direction"],
            "threshold": target_metric["threshold"],
        },
        "mock_output": {
            "diagnosis": f"The selected target metric is degraded by an incorrect unit {name.replace('_', ' ')} setting.",
            "rationale": "Restoring the discovered scalar unit parameter to the base value recovers the selected process target.",
        },
    }


def run_candidate(
    output_dir: Path,
    base_path: Path,
    base_run: dict[str, Any],
    unit: dict[str, Any],
    candidate: dict[str, Any],
) -> dict[str, Any]:
    parameter = candidate["parameter"]
    key = (parameter["namespace"], parameter["name"])
    safe_label = slug(f"{unit.get('tag') or unit['guid']}_{candidate['candidate_label']}")
    candidate_dir = output_dir / "candidate_runs" / safe_label
    candidate_dir.mkdir(parents=True, exist_ok=True)
    faulty_path = candidate_dir / "faulty.dwxmz"
    repaired_path = candidate_dir / "repaired.dwxmz"

    result: dict[str, Any] = {
        "unit": {key: value for key, value in unit.items() if key != "stage_numbers"},
        "column": {key: value for key, value in unit.items() if key != "stage_numbers"},
        "parameter": parameter,
        "fault_value": candidate["fault_value"],
        "gold_value": candidate["gold_value"],
        "repair_unit": candidate.get("unit"),
        "candidate_label": candidate["candidate_label"],
        "accepted": False,
        "rejection_reasons": [],
        "target_metric_candidates": [],
    }
    try:
        apply_fault_parameter(base_path, faulty_path, unit["guid"], key, candidate["fault_value"], candidate.get("unit"))
        apply_fault_parameter(faulty_path, repaired_path, unit["guid"], key, candidate["gold_value"], candidate.get("unit"))
        faulty_run = run_metrics(faulty_path, candidate_dir / "faulty_run.json", candidate_dir / "faulty_calculated.dwxmz", unit["guid"])
        repaired_run = run_metrics(
            repaired_path,
            candidate_dir / "repaired_run.json",
            candidate_dir / "repaired_calculated.dwxmz",
            unit["guid"],
        )
    except Exception as exc:  # noqa: BLE001
        result["rejection_reasons"].append("candidate_execution_failed")
        result["error"] = str(exc)
        return result

    result["faulty_success"] = is_successful_run(faulty_run)
    result["repaired_success"] = is_successful_run(repaired_run)
    if not (is_successful_run(base_run) and is_successful_run(faulty_run) and is_successful_run(repaired_run)):
        result["rejection_reasons"].append("run_not_successful")
        return result

    target_metrics = score_target_metrics(base_run, faulty_run, repaired_run)
    result["target_metric_candidates"] = target_metrics[:20]
    accepted_metrics = [metric for metric in target_metrics if metric["accepted"]]
    if not accepted_metrics:
        result["rejection_reasons"].append("no_accepted_target_metric")
        return result

    result["accepted"] = True
    result["selected_target_metric"] = accepted_metrics[0]
    result["score"] = accepted_metrics[0]["score"]
    return result


def select_diverse_top(candidates: list[dict[str, Any]], limit: int) -> list[dict[str, Any]]:
    accepted = sorted((item for item in candidates if item.get("accepted") is True), key=lambda item: item.get("score", 0), reverse=True)
    selected: list[dict[str, Any]] = []
    seen_parameters: set[str] = set()
    for item in accepted:
        parameter_key = f"{item['parameter']['namespace']}/{item['parameter']['name']}"
        if parameter_key in seen_parameters:
            continue
        selected.append(item)
        seen_parameters.add(parameter_key)
        if len(selected) >= limit:
            return selected
    for item in accepted:
        if item in selected:
            continue
        selected.append(item)
        if len(selected) >= limit:
            return selected
    return selected


def discover(args: argparse.Namespace) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    ensure_output_dir(args.output_dir, args.overwrite)

    base_path = args.output_dir / "base.dwxmz"
    source_path, source_entry = prepare_base_flowsheet(args.source_flowsheet, base_path)
    columns = distillation_columns(base_path)
    pressure_targets = pressure_units(base_path)
    thermal_targets = thermal_units(base_path)
    separator_pressure_targets = separator_units(base_path, ("separator_specification", "pressure"))
    separator_temperature_targets = separator_units(base_path, ("separator_specification", "temperature"))
    if not columns and not pressure_targets and not thermal_targets and not separator_pressure_targets and not separator_temperature_targets:
        raise ValueError("no supported native unit targets found")

    source_slug = slug(args.source_id or source_path.stem)
    source_name = args.source_name or source_path.name
    source_category = getattr(args, "source_category", None)
    allowed_repair_actions = collect_allowed_repair_actions(base_path)
    report: dict[str, Any] = {
        "source_flowsheet": str(args.source_flowsheet),
        "source_entry": source_entry,
        "source_name": source_name,
        "source_category": source_category,
        "source_id": source_slug,
        "candidate_count": 0,
        "accepted_count": 0,
        "columns": [],
        "pressure_units": [],
        "thermal_units": [],
        "separator_pressure_units": [],
        "separator_temperature_units": [],
        "allowed_repair_action_count": len(allowed_repair_actions),
        "candidates": [],
        "built_instances": [],
    }
    accepted_candidates: list[dict[str, Any]] = []

    for column in columns:
        base_run = run_metrics(base_path, args.output_dir / f"base_run_{slug(column['guid'])}.json", args.output_dir / f"base_calculated_{slug(column['guid'])}.dwxmz", column["guid"])
        column_entry = {
            "guid": column["guid"],
            "tag": column.get("tag"),
            "base_success": is_successful_run(base_run),
            "base_column": base_run.get("column"),
        }
        report["columns"].append(column_entry)
        if not is_successful_run(base_run):
            continue
        for candidate in column_candidate_values(base_run, column):
            result = run_candidate(args.output_dir, base_path, base_run, column, candidate)
            if result.get("accepted") is True and len(allowed_repair_actions) < 2:
                result["accepted"] = False
                result["rejection_reasons"].append("insufficient_allowed_repair_actions")
            report["candidates"].append(result)
            if result.get("accepted") is True:
                accepted_candidates.append(result)

    for unit in pressure_targets:
        base_run = run_metrics(
            base_path,
            args.output_dir / f"base_run_{slug(unit['guid'])}.json",
            args.output_dir / f"base_calculated_{slug(unit['guid'])}.dwxmz",
            unit["guid"],
        )
        unit_entry = {
            "guid": unit["guid"],
            "tag": unit.get("tag"),
            "type": unit.get("type"),
            "base_success": is_successful_run(base_run),
            "base_target_unit": base_run.get("target_unit"),
        }
        report["pressure_units"].append(unit_entry)
        if not is_successful_run(base_run):
            continue
        for candidate in pressure_candidate_values(base_run):
            result = run_candidate(args.output_dir, base_path, base_run, unit, candidate)
            if result.get("accepted") is True and len(allowed_repair_actions) < 2:
                result["accepted"] = False
                result["rejection_reasons"].append("insufficient_allowed_repair_actions")
            report["candidates"].append(result)
            if result.get("accepted") is True:
                accepted_candidates.append(result)

    for unit in thermal_targets:
        base_run = run_metrics(
            base_path,
            args.output_dir / f"base_run_{slug(unit['guid'])}.json",
            args.output_dir / f"base_calculated_{slug(unit['guid'])}.dwxmz",
            unit["guid"],
        )
        unit_entry = {
            "guid": unit["guid"],
            "tag": unit.get("tag"),
            "type": unit.get("type"),
            "base_success": is_successful_run(base_run),
            "base_target_unit": base_run.get("target_unit"),
        }
        report["thermal_units"].append(unit_entry)
        if not is_successful_run(base_run):
            continue
        for candidate in thermal_candidate_values(base_run):
            result = run_candidate(args.output_dir, base_path, base_run, unit, candidate)
            if result.get("accepted") is True and len(allowed_repair_actions) < 2:
                result["accepted"] = False
                result["rejection_reasons"].append("insufficient_allowed_repair_actions")
            report["candidates"].append(result)
            if result.get("accepted") is True:
                accepted_candidates.append(result)

    for unit in separator_pressure_targets:
        base_run = run_metrics(
            base_path,
            args.output_dir / f"base_run_{slug(unit['guid'])}.json",
            args.output_dir / f"base_calculated_{slug(unit['guid'])}.dwxmz",
            unit["guid"],
        )
        unit_entry = {
            "guid": unit["guid"],
            "tag": unit.get("tag"),
            "type": unit.get("type"),
            "base_success": is_successful_run(base_run),
            "base_target_unit": base_run.get("target_unit"),
        }
        report["separator_pressure_units"].append(unit_entry)
        if not is_successful_run(base_run):
            continue
        for candidate in separator_pressure_candidate_values(base_run):
            result = run_candidate(args.output_dir, base_path, base_run, unit, candidate)
            if result.get("accepted") is True and len(allowed_repair_actions) < 2:
                result["accepted"] = False
                result["rejection_reasons"].append("insufficient_allowed_repair_actions")
            report["candidates"].append(result)
            if result.get("accepted") is True:
                accepted_candidates.append(result)

    for unit in separator_temperature_targets:
        base_run = run_metrics(
            base_path,
            args.output_dir / f"base_run_{slug(unit['guid'])}.json",
            args.output_dir / f"base_calculated_{slug(unit['guid'])}.dwxmz",
            unit["guid"],
        )
        unit_entry = {
            "guid": unit["guid"],
            "tag": unit.get("tag"),
            "type": unit.get("type"),
            "base_success": is_successful_run(base_run),
            "base_target_unit": base_run.get("target_unit"),
        }
        report["separator_temperature_units"].append(unit_entry)
        if not is_successful_run(base_run):
            continue
        for candidate in separator_temperature_candidate_values(base_run):
            result = run_candidate(args.output_dir, base_path, base_run, unit, candidate)
            if result.get("accepted") is True and len(allowed_repair_actions) < 2:
                result["accepted"] = False
                result["rejection_reasons"].append("insufficient_allowed_repair_actions")
            report["candidates"].append(result)
            if result.get("accepted") is True:
                accepted_candidates.append(result)

    report["candidate_count"] = len(report["candidates"])
    report["accepted_count"] = len(accepted_candidates)
    specs: list[dict[str, Any]] = []
    for index, candidate in enumerate(sorted(accepted_candidates, key=lambda item: item.get("score", 0), reverse=True), start=1):
        spec = candidate_spec(
            args.source_flowsheet,
            source_name,
            source_slug,
            candidate.get("unit") or candidate.get("column"),
            candidate,
            candidate["selected_target_metric"],
            index,
            "distillation" if candidate["parameter"]["namespace"].startswith("column_") else (source_category or "other_candidate"),
            source_category,
            allowed_repair_actions,
        )
        candidate["fault_spec"] = spec
        specs.append(spec)

    if args.write_specs:
        specs_dir = args.output_dir / "candidate_specs"
        specs_dir.mkdir(parents=True, exist_ok=True)
        for index, spec in enumerate(specs, start=1):
            write_json(specs_dir / f"spec_{index:04d}.json", spec)

    if args.build_top_k:
        selected = select_diverse_top(accepted_candidates, args.build_top_k)
        generated_root = args.output_dir / "generated_instances"
        for candidate in selected:
            spec = candidate.get("fault_spec")
            if not isinstance(spec, dict):
                continue
            try:
                instance_path = build_instance(spec, generated_root, overwrite=True)
                report["built_instances"].append(
                    {
                        "instance_id": spec["instance_id"],
                        "instance_path": str(instance_path),
                        "parameter": f"{candidate['parameter']['namespace']}/{candidate['parameter']['name']}",
                        "score": candidate.get("score"),
                    }
                )
            except Exception as exc:  # noqa: BLE001
                report["built_instances"].append(
                    {
                        "instance_id": spec["instance_id"],
                        "error": str(exc),
                        "parameter": f"{candidate['parameter']['namespace']}/{candidate['parameter']['name']}",
                        "score": candidate.get("score"),
                    }
                )

    write_json(args.output_dir / "sensitivity_report.json", report)
    return report, specs


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source-flowsheet", required=True, type=Path)
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, type=Path)
    parser.add_argument("--source-id")
    parser.add_argument("--source-name")
    parser.add_argument("--source-category")
    parser.add_argument("--write-specs", action="store_true")
    parser.add_argument("--build-top-k", type=int, default=0)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        report, _specs = discover(args)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        f"Discovery complete: candidates={report['candidate_count']} "
        f"accepted={report['accepted_count']} built={len(report['built_instances'])}"
    )
    print(f"Wrote sensitivity report to {args.output_dir / 'sensitivity_report.json'}")
    return 0 if report["accepted_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
