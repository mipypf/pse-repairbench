#!/usr/bin/env python3
"""Build a release-style instance from a fixed v0.1 fault spec."""

from __future__ import annotations

import argparse
import shutil
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from builder_common import (  # noqa: E402
    absolute_ref,
    component_metric,
    extract_source_metadata,
    gold_proximity,
    graphic_tags,
    is_successful_run,
    load_json,
    parse_stage_number,
    read_dwxmz_xml,
    read_inner_dwsim_from_curated_zip,
    run_apply_repair_actions,
    run_generate_llm_input,
    run_metrics,
    set_pressure_outlet_pressure,
    set_separator_pressure,
    set_separator_temperature,
    set_thermal_outlet_temperature,
    set_column_feed_stage,
    set_column_reflux_ratio,
    sha256,
    text_of,
    unit_summary,
    update_dwxmz,
    write_json,
    write_stream_table,
    write_topology,
)
from repair_registry import (  # noqa: E402
    REGISTRY,
    entry_for_parameter,
    entry_supports_unit_type,
    parameter_key_text,
    parameter_label,
    pair_from_target_and_entry,
    parameter_key as registry_parameter_key,
    normalize_value_for_entry,
    required_state_mismatches,
    validate_unit_for_entry,
    xml_field_for_unit_type,
)


DEFAULT_OUTPUT_ROOT = Path(".tmp/generated_pilot_native_units")
FAULT_TYPE_BY_PARAMETER = {
    ("column_specification", "reflux_ratio"): "column_reflux_ratio_error",
    ("column_configuration", "feed_stage"): "column_feed_stage_error",
    ("pressure_specification", "outlet_pressure"): "pressure_outlet_pressure_error",
    ("thermal_specification", "outlet_temperature"): "thermal_outlet_temperature_error",
    ("separator_specification", "pressure"): "separator_pressure_error",
    ("separator_specification", "temperature"): "separator_temperature_error",
}


def repo_root() -> Path:
    return Path.cwd()


def resolve_repo_path(path_text: str) -> Path:
    path = Path(path_text)
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


def parameter_key(parameter: dict[str, Any]) -> tuple[str, str]:
    key = registry_parameter_key(parameter)
    if key is None:
        raise ValueError("fault.parameter must include string namespace and name")
    try:
        entry_for_parameter(key)
    except KeyError as exc:
        supported = ", ".join(entry["key"] for entry in REGISTRY)
        raise ValueError(f"unsupported builder parameter {parameter_key_text(key)}; supported: {supported}") from exc
    return key


def normalize_value(key: tuple[str, str], value: Any, field_name: str) -> int | float:
    return normalize_value_for_entry(entry_for_parameter(key), value, field_name)


def normalize_component_name(raw: str) -> str:
    aliases = {
        "o2": "Oxygen",
        "oxygen": "Oxygen",
        "n2": "Nitrogen",
        "nitrogen": "Nitrogen",
    }
    return aliases.get(raw.strip().lower(), raw.strip())


def normalize_target_metric(raw: dict[str, Any]) -> dict[str, Any]:
    stream_tag = raw.get("stream_tag") or raw.get("stream")
    if not isinstance(stream_tag, str) or not stream_tag:
        raise ValueError("target_metric.stream or target_metric.stream_tag is required")

    component = raw.get("component")
    metric = raw.get("metric")
    family = raw.get("family")
    direction = raw.get("direction")
    property_name = raw.get("property")
    if isinstance(property_name, str) and property_name.endswith("_mole_fraction"):
        prefix = property_name[: -len("_mole_fraction")]
        component = component or prefix
        metric = metric or "mole_fraction"
        family = family or "product_purity"
    if isinstance(component, str):
        component = normalize_component_name(component)
    if not isinstance(metric, str) or not metric:
        metric = "mole_fraction"
    if not isinstance(family, str) or not family:
        family = "product_flow" if component is None and metric in {"molar_flow", "mass_flow"} else "product_purity"
    supported_families = {
        "product_purity",
        "impurity_max",
        "product_flow",
        "stream_pressure",
        "terminal_composition",
        "terminal_flow",
        "terminal_temperature",
        "terminal_pressure",
    }
    if family not in supported_families:
        raise ValueError(f"unsupported target_metric.family: {family!r}")
    if family in {"product_purity", "impurity_max", "terminal_composition"} and (
        not isinstance(component, str) or not component
    ):
        raise ValueError("composition target metrics require target_metric.component")
    if family in {"product_purity", "impurity_max"} and metric != "mole_fraction":
        raise ValueError("legacy purity target metrics support only mole_fraction")
    if family == "terminal_composition" and metric not in {"mole_fraction", "mass_fraction"}:
        raise ValueError("terminal_composition target metrics support mole_fraction or mass_fraction")
    if family in {"product_flow", "terminal_flow"} and metric not in {"molar_flow", "mass_flow"}:
        raise ValueError("flow target metrics support only molar_flow or mass_flow")
    if family in {"stream_pressure", "terminal_pressure"}:
        component = None
        metric = "pressure"
    if family == "terminal_temperature":
        component = None
        metric = "temperature"
    if not isinstance(direction, str) or not direction:
        direction = "max" if family == "impurity_max" else "min"
    if direction not in {"min", "max"}:
        raise ValueError("target_metric.direction must be 'min' or 'max'")

    threshold = raw.get("threshold", raw.get("min", raw.get("minimum")))
    if isinstance(threshold, bool) or not isinstance(threshold, (int, float)):
        raise ValueError("target_metric.threshold or target_metric.min must be numeric")
    target = {
        "family": family,
        "stream_tag": stream_tag,
        "component": component,
        "metric": metric,
        "direction": direction,
        "threshold": float(threshold),
    }
    if isinstance(raw.get("stream_id"), str) and raw.get("stream_id"):
        target["stream_id"] = raw["stream_id"]
    if isinstance(raw.get("stream_role"), str) and raw.get("stream_role"):
        target["stream_role"] = raw["stream_role"]
    if direction == "min":
        target["minimum"] = float(threshold)
    else:
        target["maximum"] = float(threshold)
    if family == "product_purity" and metric == "mole_fraction" and direction == "min":
        target["product_mole_fraction_min"] = float(threshold)
    return target


def prepare_base_flowsheet(source_flowsheet: str, target: Path) -> tuple[Path, str]:
    source = resolve_repo_path(source_flowsheet)
    if not source.exists():
        raise FileNotFoundError(f"source_flowsheet not found: {source}")
    if source.suffix.lower() == ".zip":
        source_entry = read_inner_dwsim_from_curated_zip(source, target)
    elif source.suffix.lower() in {".dwxmz", ".dwxml"}:
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(source, target)
        source_entry = source.name
    else:
        raise ValueError("source_flowsheet must be a .zip, .dwxmz, or .dwxml file")
    return source, source_entry


def resolve_unit_target(flowsheet: Path, target: dict[str, Any], key: tuple[str, str]) -> dict[str, Any]:
    if target.get("kind") != "unit_operation":
        raise ValueError("general builder supports only target.kind='unit_operation'")
    entry = entry_for_parameter(key)
    requested_guid = target.get("guid") or target.get("name")
    requested_tag = target.get("tag")
    tree, _xml_entry, _entries = read_dwxmz_xml(flowsheet)
    root = tree.getroot()
    tags = graphic_tags(root)
    simulation_objects = tree.getroot().find("SimulationObjects")
    if simulation_objects is None:
        raise ValueError("source flowsheet has no SimulationObjects section")

    matches: list[dict[str, Any]] = []
    for obj in simulation_objects:
        unit_type = text_of(obj, "Type")
        if not entry_supports_unit_type(entry, unit_type):
            continue
        guid = text_of(obj, "Name")
        tag = tags.get(guid or "")
        if requested_guid and guid != requested_guid:
            continue
        if requested_tag and tag != requested_tag:
            continue
        if not guid:
            continue
        summary = unit_summary(root, obj)
        if key == ("column_configuration", "feed_stage"):
            stages = obj.find("Stages")
            stage_numbers: list[int] = []
            if stages is not None:
                for stage in stages:
                    from builder_common import parse_stage_number  # local import avoids widening public API here

                    number = parse_stage_number(text_of(stage, "Name"))
                    if isinstance(number, int) and number > 0:
                        stage_numbers.append(number)
            summary["stage_numbers"] = sorted(set(stage_numbers))
        matches.append(summary)

    if len(matches) != 1:
        selector = {key: value for key, value in target.items() if key in {"guid", "name", "tag"}}
        raise ValueError(f"expected exactly one supported target for {selector}, found {len(matches)}")
    return matches[0]


def apply_fault_parameter(
    source: Path,
    target: Path,
    unit_guid: str,
    key: tuple[str, str],
    value: int | float,
    unit: str | None = None,
) -> None:
    if key == ("column_specification", "reflux_ratio"):
        update_dwxmz(source, target, lambda tree: set_column_reflux_ratio(tree, unit_guid, repr(float(value))))
    elif key == ("column_configuration", "feed_stage"):
        update_dwxmz(source, target, lambda tree: set_column_feed_stage(tree, unit_guid, int(value)))
    elif key == ("pressure_specification", "outlet_pressure"):
        update_dwxmz(source, target, lambda tree: set_pressure_outlet_pressure(tree, unit_guid, float(value), unit or "Pa"))
    elif key == ("thermal_specification", "outlet_temperature"):
        update_dwxmz(source, target, lambda tree: set_thermal_outlet_temperature(tree, unit_guid, float(value), unit or "K"))
    elif key == ("separator_specification", "pressure"):
        update_dwxmz(source, target, lambda tree: set_separator_pressure(tree, unit_guid, float(value), unit or "Pa"))
    elif key == ("separator_specification", "temperature"):
        update_dwxmz(source, target, lambda tree: set_separator_temperature(tree, unit_guid, float(value), unit or "K"))
    else:  # pragma: no cover - guarded by parameter_key.
        raise ValueError(f"unsupported parameter: {key}")


def gold_repair_action(
    resolved_target: dict[str, str],
    parameter: dict[str, str],
    gold_value: int | float,
    unit: str | None,
) -> dict[str, Any]:
    target = {
        "kind": resolved_target["kind"],
        "guid": resolved_target["guid"],
    }
    if resolved_target.get("tag"):
        target["tag"] = resolved_target["tag"]
    return {
        "type": "set_unit_parameter",
        "target": target,
        "parameter": parameter,
        "value": gold_value,
        "unit": unit,
    }


def render_problem(spec: dict[str, Any], target: dict[str, Any], resolved_target: dict[str, str]) -> str:
    problem = spec.get("public_problem")
    if not isinstance(problem, dict):
        problem = {}
    key = parameter_key(spec["fault"]["parameter"])
    title = problem.get("title") or "Repair Task: Terminal Stream Target Recovery"
    body = problem.get("body")
    if body is None:
        body = (
            "The DWSIM flowsheet runs headlessly, but a terminal material stream misses its target condition.\n\n"
            "Choose exactly one allowed existing unit-parameter repair action from the provided observations. "
            "The repaired flowsheet should make `{target_metric_label}` in material stream `{target_stream_tag}` "
            "meet `{target_direction}` threshold `{target_threshold}` after rerunning.\n\n"
            "Expected repair action type: `set_unit_parameter`."
        )
    if "{gold_value" in body or "{fault_value" in body:
        raise ValueError("public_problem.body must not expose fault_value or gold_value placeholders")

    context = {
        "target_tag": resolved_target.get("tag") or "",
        "target_guid": resolved_target["guid"],
        "target_stream_tag": target["stream_tag"],
        "target_component": target.get("component") or "",
        "target_min": f"{target['threshold']:.2f}",
        "target_threshold": f"{target['threshold']:.12g}",
        "target_direction": target["direction"],
        "target_metric_label": target_metric_label(target),
        "parameter_namespace": spec["fault"]["parameter"]["namespace"],
        "parameter_name": spec["fault"]["parameter"]["name"],
        "parameter_label": parameter_label(key),
    }
    return f"# {title}\n\n{body.format(**context).strip()}\n"


def write_mock_llm_output(path: Path, action: dict[str, Any], spec: dict[str, Any]) -> None:
    mock = spec.get("mock_output")
    if not isinstance(mock, dict):
        mock = {}
    write_json(
        path,
        {
            "diagnosis": mock.get("diagnosis") or "The selected product target is missed because the target unit parameter is misconfigured.",
            "repair_actions": [action],
            "rationale": mock.get("rationale") or "Restoring the validated scalar parameter setting recovers the selected process target.",
        },
    )


def parameter_metric_key(key: tuple[str, str]) -> str:
    if key == ("column_specification", "reflux_ratio"):
        return "reflux_ratio"
    if key == ("column_configuration", "feed_stage"):
        return "feed_stage"
    if key == ("pressure_specification", "outlet_pressure"):
        return "outlet_pressure"
    if key == ("thermal_specification", "outlet_temperature"):
        return "outlet_temperature"
    if key == ("separator_specification", "pressure"):
        return "separator_pressure"
    if key == ("separator_specification", "temperature"):
        return "separator_temperature"
    raise ValueError(f"unsupported parameter: {key}")


def parameter_run_value(run: dict[str, Any], key: tuple[str, str]) -> Any:
    metric_key = parameter_metric_key(key)
    if key in {("column_specification", "reflux_ratio"), ("column_configuration", "feed_stage")}:
        return run.get("column", {}).get(metric_key)
    target_unit = run.get("target_unit") if isinstance(run.get("target_unit"), dict) else {}
    if key == ("pressure_specification", "outlet_pressure"):
        for field in ("outlet_pressure", "pout", "p_out"):
            value = target_unit.get(field)
            if isinstance(value, (int, float)):
                return value
    if key == ("thermal_specification", "outlet_temperature"):
        value = target_unit.get("outlet_temperature")
        if isinstance(value, (int, float)):
            return value
    if key == ("separator_specification", "pressure"):
        value = target_unit.get("flash_pressure")
        if isinstance(value, (int, float)):
            return value
    if key == ("separator_specification", "temperature"):
        value = target_unit.get("flash_temperature")
        if isinstance(value, (int, float)):
            return value
    return None


def numeric_close(actual: Any, expected: Any, tolerance: float = 1e-9) -> bool:
    if isinstance(actual, bool) or isinstance(expected, bool):
        return actual == expected
    if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
        return abs(float(actual) - float(expected)) <= tolerance + tolerance * abs(float(expected))
    return actual == expected


def stream_metric(run: dict[str, Any], tag: str, metric: str) -> float | None:
    for stream in run.get("streams", []):
        if isinstance(stream, dict) and (stream.get("tag") == tag or stream.get("id") == tag):
            value = stream.get(metric)
            return float(value) if isinstance(value, (int, float)) else None
    return None


def target_value(run: dict[str, Any], target: dict[str, Any]) -> float | None:
    component = target.get("component")
    if isinstance(component, str) and component:
        return component_metric(run, target["stream_tag"], component, target["metric"])
    return stream_metric(run, target["stream_tag"], target["metric"])


def target_meets(value: float | None, target: dict[str, Any]) -> bool:
    if not isinstance(value, (int, float)):
        return False
    if target["direction"] == "min":
        return value >= target["threshold"]
    return value <= target["threshold"]


def target_misses(value: float | None, target: dict[str, Any]) -> bool:
    if not isinstance(value, (int, float)):
        return False
    if target["direction"] == "min":
        return value < target["threshold"]
    return value > target["threshold"]


def target_metric_label(target: dict[str, Any]) -> str:
    component = target.get("component")
    if isinstance(component, str) and component:
        return f"{component} {target['metric']}"
    return str(target["metric"])


def target_metric_for_manifest(target: dict[str, Any]) -> dict[str, Any]:
    manifest: dict[str, Any] = {
        "family": target["family"],
        "stream_tag": target["stream_tag"],
        "stream": target["stream_tag"],
        "metric": target["metric"],
        "direction": target["direction"],
        "threshold": target["threshold"],
    }
    if target.get("stream_id"):
        manifest["stream_id"] = target["stream_id"]
    if target.get("stream_role"):
        manifest["stream_role"] = target["stream_role"]
    if target.get("component"):
        manifest["component"] = target["component"]
    if target["direction"] == "min":
        manifest["min"] = target["threshold"]
    else:
        manifest["max"] = target["threshold"]
    return manifest


def numeric_text(value: str | None) -> int | float | None:
    if value is None:
        return None
    try:
        number = float(value)
    except ValueError:
        return None
    return int(number) if number.is_integer() else number


def compact_column_summary(unit: Any, summary: dict[str, Any]) -> None:
    summary["reflux_ratio"] = numeric_text(text_of(unit, "RefluxRatio"))
    summary["number_of_stages"] = numeric_text(text_of(unit, "NumberOfStages"))
    summary["condenser_duty"] = numeric_text(text_of(unit, "CondenserDuty"))
    summary["reboiler_duty"] = numeric_text(text_of(unit, "ReboilerDuty"))
    material_streams = unit.find("MaterialStreams")
    if material_streams is None:
        return
    feed_streams = [stream for stream in material_streams if text_of(stream, "StreamBehavior") == "Feed"]
    if len(feed_streams) != 1:
        return
    associated_stage = text_of(feed_streams[0], "AssociatedStage")
    summary["feed_stream_id"] = text_of(feed_streams[0], "ID")
    stages = unit.find("Stages")
    if stages is None or not associated_stage:
        return
    for stage in stages:
        if text_of(stage, "ID") == associated_stage:
            summary["feed_stage_name"] = text_of(stage, "Name")
            summary["feed_stage"] = parse_stage_number(text_of(stage, "Name"))
            return


def compact_observed_unit(root: Any, unit: Any, supported_parameters: list[str]) -> dict[str, Any]:
    summary = unit_summary(root, unit)
    summary["supported_parameters"] = sorted(dict.fromkeys(supported_parameters))
    unit_type = summary.get("type")
    if entry_supports_unit_type(entry_for_parameter(("column_specification", "reflux_ratio")), unit_type) or entry_supports_unit_type(
        entry_for_parameter(("column_configuration", "feed_stage")), unit_type
    ):
        compact_column_summary(unit, summary)

    for field, output_key in (
        ("OutletPressure", "outlet_pressure"),
        ("Pout", "pout"),
        ("POut", "p_out"),
        ("DeltaP", "delta_p"),
        ("OutletTemperature", "outlet_temperature"),
        ("FlashPressure", "flash_pressure"),
        ("FlashTemperature", "flash_temperature"),
    ):
        value = numeric_text(text_of(unit, field))
        if value is not None:
            summary[output_key] = value
    for field, output_key in (("OverrideP", "override_p"), ("OverrideT", "override_t")):
        value = text_of(unit, field)
        if value is not None:
            summary[output_key] = value

    for parameter_text in supported_parameters:
        try:
            entry = entry_for_parameter(tuple(parameter_text.split("/", 1)))  # type: ignore[arg-type]
            xml_field = xml_field_for_unit_type(entry, unit_type)
        except Exception:  # noqa: BLE001
            continue
        observed_value = numeric_text(text_of(unit, xml_field))
        if observed_value is not None:
            summary.setdefault("observed_values", {})[parameter_text] = observed_value
    return {key: value for key, value in summary.items() if value is not None}


def observed_candidate_units(flowsheet: Path, allowed_repair_actions: list[dict[str, Any]]) -> list[dict[str, Any]]:
    by_guid: dict[str, list[str]] = {}
    ordered_guids: list[str] = []
    for pair in allowed_repair_actions:
        target = pair.get("target") if isinstance(pair, dict) else None
        parameter = pair.get("parameter") if isinstance(pair, dict) else None
        guid = target.get("guid") if isinstance(target, dict) else None
        namespace = parameter.get("namespace") if isinstance(parameter, dict) else None
        name = parameter.get("name") if isinstance(parameter, dict) else None
        if not isinstance(guid, str) or not guid or not isinstance(namespace, str) or not isinstance(name, str):
            continue
        if guid not in by_guid:
            by_guid[guid] = []
            ordered_guids.append(guid)
        by_guid[guid].append(f"{namespace}/{name}")

    if not ordered_guids:
        return []

    tree, _xml_entry, _entries = read_dwxmz_xml(flowsheet)
    root = tree.getroot()
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        return []
    objects_by_guid = {text_of(obj, "Name"): obj for obj in simulation_objects if text_of(obj, "Name")}

    summaries: list[dict[str, Any]] = []
    for guid in ordered_guids:
        unit = objects_by_guid.get(guid)
        if unit is None:
            continue
        summaries.append(compact_observed_unit(root, unit, by_guid[guid]))
    return summaries


def write_observation_parameters(
    faulty_run: dict[str, Any],
    target: dict[str, Any],
    output_path: Path,
    target_parameter: dict[str, str],
    allowed_repair_actions: list[dict[str, Any]] | None = None,
    observed_units: list[dict[str, Any]] | None = None,
    include_target_parameter: bool = False,
    include_target_locator: bool = True,
) -> None:
    product_target = {
        "stream_tag": target["stream_tag"],
        "metric": target["metric"],
        "direction": target["direction"],
        "threshold": target["threshold"],
    }
    if target.get("component"):
        product_target["component"] = target["component"]
    if target.get("product_mole_fraction_min") is not None:
        product_target["product_mole_fraction_min"] = target["product_mole_fraction_min"]
    payload = {
        "schema_version": "draft-0",
        "extraction_note": "Parameters extracted from the calculated faulty flowsheet.",
        "allowed_repair_actions": allowed_repair_actions or [],
        "observed_candidate_units": observed_units or [],
        "terminal_material_streams": faulty_run.get("terminal_material_streams") or [],
        "product_target": product_target,
        "target_metric": target_metric_for_manifest(target),
    }
    if include_target_locator:
        payload["target_column"] = faulty_run.get("column")
        payload["target_unit"] = faulty_run.get("target_unit")
    if include_target_parameter:
        payload["target_parameter"] = target_parameter
    write_json(output_path, payload)


def write_observation_log(run: dict[str, Any], target: dict[str, Any], output_path: Path) -> None:
    observed_value = target_value(run, target)
    comparator = ">=" if target["direction"] == "min" else "<="
    lines = [
        f"DWSIM headless status: {run.get('status')}",
        f"Solved after calculation: {run.get('solved_after')}",
        f"Exception count: {run.get('exception_count')}",
        f"Messages log count: {run.get('messages_log_count')}",
        f"Target stream: {target['stream_tag']}",
        f"Target metric: {target_metric_label(target)}",
        f"Observed target value: {observed_value}",
        f"Required target value: {comparator} {target['threshold']}",
    ]
    for exception in run.get("exceptions", []):
        lines.append(f"Exception: {exception.get('type')}: {exception.get('message')}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def target_stream_id(run: dict[str, Any], target: dict[str, Any]) -> str | None:
    for stream in run.get("streams", []):
        if not isinstance(stream, dict):
            continue
        if stream.get("tag") == target["stream_tag"] or stream.get("id") == target["stream_tag"]:
            stream_id = stream.get("id")
            return stream_id if isinstance(stream_id, str) else None
    return None


def collect_allowed_repair_actions(flowsheet: Path) -> list[dict[str, Any]]:
    tree, _xml_entry, _entries = read_dwxmz_xml(flowsheet)
    root = tree.getroot()
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        return []
    allowed: list[dict[str, Any]] = []
    for obj in simulation_objects:
        summary = unit_summary(root, obj)
        unit_type = summary.get("type")
        if not isinstance(summary.get("guid"), str):
            continue
        for entry in REGISTRY:
            if not entry_supports_unit_type(entry, unit_type):
                continue
            if required_state_mismatches(entry, lambda name: text_of(obj, name)):
                continue
            if entry["key"] == "column_configuration/feed_stage":
                material_streams = obj.find("MaterialStreams")
                if material_streams is None:
                    continue
                feed_streams = [stream for stream in material_streams if text_of(stream, "StreamBehavior") == "Feed"]
                if len(feed_streams) != 1:
                    continue
            allowed.append(pair_from_target_and_entry(summary, entry))
    return allowed


def validate_generated_runs(
    key: tuple[str, str],
    fault_value: int | float,
    gold_value: int | float,
    target: dict[str, Any],
    base_run: dict[str, Any],
    faulty_run: dict[str, Any],
    repaired_run: dict[str, Any],
    proximity: dict[str, Any],
) -> None:
    faulty_metric = target_value(faulty_run, target)
    repaired_metric = target_value(repaired_run, target)
    errors: list[str] = []

    if not is_successful_run(base_run):
        errors.append("base_run did not solve successfully")
    if not is_successful_run(faulty_run):
        errors.append("faulty_run did not solve successfully")
    if not is_successful_run(repaired_run):
        errors.append("repaired_run did not solve successfully")
    metric_key = parameter_metric_key(key)
    if not numeric_close(parameter_run_value(faulty_run, key), fault_value):
        errors.append(f"faulty target {metric_key} does not match fault_value")
    if not numeric_close(parameter_run_value(repaired_run, key), gold_value):
        errors.append(f"repaired target {metric_key} does not match gold_value")
    if not target_misses(faulty_metric, target):
        errors.append("faulty target metric does not miss the selected target")
    if not target_meets(repaired_metric, target):
        errors.append("repaired target metric does not satisfy the selected target")
    if proximity != {
        "target_match": True,
        "parameter_match": True,
        "unit_match": True,
        "value_abs_error": 0.0,
        "value_rel_error": 0.0,
    }:
        errors.append("gold_proximity is not an exact match")
    if errors:
        raise RuntimeError("; ".join(errors))


def write_llm_input_context(
    path: Path,
    instance_id: str,
    process_category: str,
    formal_faulty: Path,
    problem_path: Path,
    public_dir: Path,
    action: dict[str, Any],
    target: dict[str, Any],
) -> None:
    write_json(
        path,
        {
            "id": instance_id,
            "process_category": process_category,
            "reasoning_class": "P_parameter",
            "faulty_flowsheet": absolute_ref(formal_faulty),
            "problem_statement": absolute_ref(problem_path),
            "observations": {
                "topology": absolute_ref(public_dir / "topology.json"),
                "parameters": absolute_ref(public_dir / "parameters.json"),
                "simulator_log": absolute_ref(public_dir / "log.txt"),
                "stream_table": absolute_ref(public_dir / "streams.csv"),
            },
            "gold_repair_actions": [
                {
                    "type": action["type"],
                    "target": {"kind": "unit_operation", "guid": action["target"]["guid"]},
                    "parameter": action["parameter"],
                }
            ],
            "success_criteria": {
                "converged": True,
                "no_fatal_error": True,
                "target_stream_tag": target["stream_tag"],
                "target_component": target.get("component"),
                "product_mole_fraction_min": target.get("product_mole_fraction_min"),
                "target_metric": target_metric_for_manifest(target),
            },
        },
    )


def build_instance(spec: dict[str, Any], output_root: Path, overwrite: bool) -> Path:
    instance_id = spec.get("instance_id")
    if not isinstance(instance_id, str) or not instance_id:
        raise ValueError("instance_id is required")
    fault = spec.get("fault")
    if not isinstance(fault, dict):
        raise ValueError("fault object is required")
    target_ref = fault.get("target")
    parameter = fault.get("parameter")
    if not isinstance(target_ref, dict) or not isinstance(parameter, dict):
        raise ValueError("fault.target and fault.parameter objects are required")

    key = parameter_key(parameter)
    entry = entry_for_parameter(key)
    unit = fault.get("unit")
    if unit is not None and not isinstance(unit, str):
        raise ValueError("fault.unit must be string or null")
    validate_unit_for_entry(entry, unit)
    fault_value = normalize_value(key, fault.get("fault_value"), "fault.fault_value")
    gold_value = normalize_value(key, fault.get("gold_value"), "fault.gold_value")
    target = normalize_target_metric(spec.get("target_metric") if isinstance(spec.get("target_metric"), dict) else {})

    output_dir = output_root / instance_id
    ensure_output_dir(output_dir, overwrite)
    hidden_dir = output_dir / "hidden"
    public_dir = output_dir / "public"
    work_dir = output_dir / "_builder_work"
    hidden_dir.mkdir(parents=True, exist_ok=True)
    public_dir.mkdir(parents=True, exist_ok=True)
    work_dir.mkdir(parents=True, exist_ok=True)

    formal_base = hidden_dir / "base.dwxmz"
    formal_faulty = public_dir / "faulty.dwxmz"
    repaired_flowsheet = hidden_dir / "repaired.dwxmz"
    mock_output_path = hidden_dir / "mock_llm_output.json"
    problem_path = public_dir / "problem.md"
    llm_input_path = public_dir / "llm_input.md"
    llm_context_path = work_dir / "llm_input_context.json"
    source_path, source_entry = prepare_base_flowsheet(spec["source_flowsheet"], formal_base)

    resolved_target = resolve_unit_target(formal_base, target_ref, key)
    action = gold_repair_action(resolved_target, {"namespace": key[0], "name": key[1]}, gold_value, unit)

    apply_fault_parameter(formal_base, formal_faulty, resolved_target["guid"], key, fault_value, unit)
    base_run = run_metrics(formal_base, hidden_dir / "base_run.json", work_dir / "base_calculated.dwxmz", resolved_target["guid"])
    faulty_run = run_metrics(
        formal_faulty,
        hidden_dir / "faulty_run.json",
        work_dir / "faulty_calculated.dwxmz",
        resolved_target["guid"],
    )
    stream_id = target_stream_id(base_run, target) or target_stream_id(faulty_run, target)
    if stream_id:
        target["stream_id"] = stream_id

    allowed_repair_actions = spec.get("allowed_repair_actions")
    if not isinstance(allowed_repair_actions, list):
        allowed_repair_actions = collect_allowed_repair_actions(formal_faulty)
    observed_units = observed_candidate_units(formal_faulty, allowed_repair_actions)

    problem_path.write_text(render_problem(spec, target, resolved_target), encoding="utf-8")
    write_topology(
        formal_faulty,
        public_dir / "topology.json",
        resolved_target,
        f"Topology extracted from the faulty flowsheet after {parameter_label(key)} injection.",
    )
    public_prompt_mode = spec.get("public_prompt_mode", "parameter-selection")
    include_target_parameter = bool(spec.get("public_include_target_parameter", False))
    include_target_locator = bool(spec.get("public_include_target_locator", public_prompt_mode != "parameter-selection"))
    write_observation_parameters(
        faulty_run,
        target,
        public_dir / "parameters.json",
        action["parameter"],
        allowed_repair_actions,
        observed_units,
        include_target_parameter=include_target_parameter,
        include_target_locator=include_target_locator,
    )
    write_stream_table(faulty_run, public_dir / "streams.csv")
    write_observation_log(faulty_run, target, public_dir / "log.txt")

    process_category = spec.get("process_category", "distillation")
    write_llm_input_context(llm_context_path, instance_id, process_category, formal_faulty, problem_path, public_dir, action, target)
    run_generate_llm_input(llm_context_path, llm_input_path, prompt_mode=public_prompt_mode)
    write_mock_llm_output(mock_output_path, action, spec)
    run_apply_repair_actions(formal_faulty, repaired_flowsheet, mock_output_path)
    repaired_run = run_metrics(
        repaired_flowsheet,
        hidden_dir / "repaired_run.json",
        work_dir / "repaired_calculated.dwxmz",
        resolved_target["guid"],
    )

    metric_key = parameter_metric_key(key)
    metrics_report = {
        "instance_id": instance_id,
        "repairable": True,
        "selection_rule": "fixed fault spec; no sweep performed by the general builder",
        "source_flowsheet": spec["source_flowsheet"],
        "target": {
            **target_metric_for_manifest(target),
            "stream_tag": target["stream_tag"],
            "stream_id": target.get("stream_id"),
            "component": target.get("component"),
            "product_mole_fraction_min": target.get("product_mole_fraction_min"),
        },
        "base": {
            metric_key: parameter_run_value(base_run, key),
            "target_value": target_value(base_run, target),
            "target_mole_fraction": target_value(base_run, target)
            if target.get("metric") == "mole_fraction"
            else None,
        },
        "faulty": {
            metric_key: parameter_run_value(faulty_run, key),
            "target_value": target_value(faulty_run, target),
            "target_mole_fraction": target_value(faulty_run, target)
            if target.get("metric") == "mole_fraction"
            else None,
        },
        "repaired": {
            metric_key: parameter_run_value(repaired_run, key),
            "target_value": target_value(repaired_run, target),
            "target_mole_fraction": target_value(repaired_run, target)
            if target.get("metric") == "mole_fraction"
            else None,
        },
        "gold_repair_action": action,
        "gold_proximity": gold_proximity(load_json(mock_output_path)["repair_actions"][0], action),
    }
    base_value = metrics_report["base"]["target_value"]
    faulty_value = metrics_report["faulty"]["target_value"]
    if isinstance(base_value, (int, float)) and isinstance(faulty_value, (int, float)):
        metrics_report["target_delta"] = base_value - faulty_value
        if target.get("metric") == "mole_fraction":
            metrics_report["purity_drop"] = base_value - faulty_value
    write_json(hidden_dir / "metrics_report.json", metrics_report)

    validate_generated_runs(
        key,
        fault_value,
        gold_value,
        target,
        base_run,
        faulty_run,
        repaired_run,
        metrics_report["gold_proximity"],
    )

    source = extract_source_metadata(
        formal_base,
        Path(spec["source_flowsheet"]),
        source_entry,
        spec.get("source_name", source_path.name),
        base_run,
    )
    if isinstance(spec.get("source_category"), str):
        source["source_category"] = spec["source_category"]
    source["detected_process_category"] = spec.get("process_category", "distillation")
    source["detected_unit_family"] = resolved_target.get("type")
    instance = {
        "id": instance_id,
        "process_category": spec.get("process_category", "distillation"),
        "reasoning_class": spec.get("reasoning_class", "P_parameter"),
        "base_flowsheet": "hidden/base.dwxmz",
        "faulty_flowsheet": "public/faulty.dwxmz",
        "problem_statement": "public/problem.md",
        "llm_input": "public/llm_input.md",
        "mock_llm_output": "hidden/mock_llm_output.json",
        "fault_type": spec.get("fault_type", FAULT_TYPE_BY_PARAMETER[key]),
        "fault_severity": spec.get("fault_severity", "medium"),
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
                **action,
                "rationale": spec.get(
                    "gold_rationale",
                    f"Restore the unit {parameter_label(key)} to the validated setting that satisfies the selected process target.",
                ),
            }
        ],
        "hints": spec.get(
            "hints",
            [
                {
                    "level": 1,
                    "type": "subsystem",
                    "message": "The abnormal behavior is localized in an existing unit operation.",
                },
                {
                    "level": 3,
                    "type": "target_object",
                    "target": resolved_target["guid"],
                    "message": f"Check whether the unit {parameter_label(key)} is consistent with the requested process target.",
                },
                {
                    "level": 5,
                    "type": "direct_repair",
                    "target": resolved_target["guid"],
                    "message": f"Set the {parameter_label(key)} of {resolved_target.get('tag') or resolved_target['guid']} to {gold_value}.",
                },
            ],
        ),
        "source": source,
        "reproducibility": {
            "base_flowsheet_sha256": sha256(formal_base),
            "faulty_flowsheet_sha256": sha256(formal_faulty),
            "fault_injector_version": "build_from_fault_spec.py:1",
            "observation_extractor_version": "builder_common.py:1;generate_llm_input.py:1",
            "executor_version": "apply_repair_actions.py:2",
            "dwsim_runner_version": "dwsim_metrics_worker.ps1:2",
            "evaluator_version": "builder_common.py:1",
        },
        "success_criteria": {
            "converged": True,
            "no_fatal_error": True,
            "target_stream_tag": target["stream_tag"],
            "target_component": target.get("component"),
            "product_mole_fraction_min": target.get("product_mole_fraction_min"),
            "target_metric": target_metric_for_manifest(target),
        },
    }
    write_json(output_dir / "instance.json", instance)
    return output_dir / "instance.json"


def action_semantics(action: dict[str, Any]) -> dict[str, Any]:
    target = action.get("target") if isinstance(action.get("target"), dict) else {}
    parameter = action.get("parameter") if isinstance(action.get("parameter"), dict) else {}
    return {
        "type": action.get("type"),
        "target": {key: target.get(key) for key in ("kind", "guid", "tag")},
        "parameter": {key: parameter.get(key) for key in ("namespace", "name")},
        "value": action.get("value"),
        "unit": action.get("unit"),
    }


def compare_semantic_equivalence(generated_instance_path: Path, reference_instance_path: Path) -> None:
    generated = load_json(generated_instance_path)
    reference = load_json(reference_instance_path)
    generated_metrics = load_json(generated_instance_path.parent / generated["run_artifacts"]["metrics_report"])
    reference_metrics = load_json(reference_instance_path.parent / reference["run_artifacts"]["metrics_report"])
    errors: list[str] = []

    generated_action = action_semantics(generated["gold_repair_actions"][0])
    reference_action = action_semantics(reference["gold_repair_actions"][0])
    for key in ("type", "target", "parameter", "unit"):
        if generated_action[key] != reference_action[key]:
            errors.append(f"gold action {key} differs: generated={generated_action[key]!r}, reference={reference_action[key]!r}")
    if not numeric_close(generated_action["value"], reference_action["value"]):
        errors.append(f"gold action value differs: generated={generated_action['value']!r}, reference={reference_action['value']!r}")

    for key in ("converged", "no_fatal_error", "target_stream_tag", "target_component", "product_mole_fraction_min"):
        if not numeric_close(generated["success_criteria"].get(key), reference["success_criteria"].get(key)):
            errors.append(f"success_criteria.{key} differs")

    generated_target = generated_metrics.get("target") if isinstance(generated_metrics.get("target"), dict) else {}
    reference_target = reference_metrics.get("target") if isinstance(reference_metrics.get("target"), dict) else {}
    for key in ("stream_tag", "stream_id", "component", "product_mole_fraction_min"):
        if not numeric_close(generated_target.get(key), reference_target.get(key)):
            errors.append(f"metrics_report.target.{key} differs")
    for key in ("target_match", "parameter_match", "unit_match"):
        if generated_metrics["gold_proximity"].get(key) != reference_metrics["gold_proximity"].get(key):
            errors.append(f"gold_proximity.{key} differs")
    for key in ("value_abs_error", "value_rel_error"):
        if not numeric_close(generated_metrics["gold_proximity"].get(key), reference_metrics["gold_proximity"].get(key)):
            errors.append(f"gold_proximity.{key} differs")
    if not numeric_close(
        generated_metrics.get("repaired", {}).get("target_mole_fraction"),
        reference_metrics.get("repaired", {}).get("target_mole_fraction"),
    ):
        errors.append("repaired target metric differs")
    if errors:
        raise RuntimeError("semantic equivalence check failed: " + "; ".join(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fault-spec", required=True, type=Path)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    parser.add_argument("--reference-instance", type=Path)
    args = parser.parse_args()

    spec = load_json(args.fault_spec)
    if not isinstance(spec, dict):
        raise ValueError("fault spec must be a JSON object")
    instance_path = build_instance(spec, args.output_root, args.overwrite)
    if args.reference_instance:
        compare_semantic_equivalence(instance_path, args.reference_instance)
        print(f"Semantic equivalence OK against {args.reference_instance}")
    print(f"Built generated instance: {instance_path}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
