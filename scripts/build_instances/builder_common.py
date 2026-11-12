"""Shared helpers for PSE-RepairBench instance builders."""

from __future__ import annotations

import csv
import hashlib
import json
import math
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import date
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dwsim_run_contract import is_successful_dwsim_run  # noqa: E402
from repair_registry import (  # noqa: E402
    entry_for_parameter,
    entry_supports_unit_type,
    parameter_key_text,
    pair_from_target_and_entry,
    required_state_mismatches,
    validate_unit_for_entry,
    xml_field_for_unit_type,
)


COMPONENTS = ("Oxygen", "Nitrogen")
METRIC_WORKER = Path("scripts/dwsim/dwsim_metrics_worker.ps1")
APPLY_REPAIR_ACTIONS = Path("scripts/dwsim/apply_repair_actions.py")
GENERATE_LLM_INPUT = Path("scripts/llm/generate_llm_input.py")


def repo_root() -> Path:
    return Path.cwd()


def write_json(path: Path, data: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def absolute_ref(path: Path) -> str:
    return str((repo_root() / path).resolve()).replace("\\", "/")


def artifact_path(path: Path | str | None) -> str | None:
    if path is None:
        return None
    raw = Path(path)
    try:
        resolved = raw.resolve()
        return resolved.relative_to(repo_root().resolve()).as_posix()
    except (OSError, ValueError):
        return raw.as_posix() if isinstance(path, Path) else str(path).replace("\\", "/")


def sanitize_artifact_paths(value: Any) -> Any:
    if isinstance(value, dict):
        return {key: sanitize_artifact_paths(item) for key, item in value.items()}
    if isinstance(value, list):
        return [sanitize_artifact_paths(item) for item in value]
    if isinstance(value, str):
        try:
            root = repo_root().resolve()
            resolved = Path(value).resolve()
            return resolved.relative_to(root).as_posix()
        except (OSError, ValueError):
            return value.replace("\\", "/")
    return value


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_of(element: ET.Element | None, name: str) -> str | None:
    if element is None:
        return None
    child = element.find(name)
    if child is None or child.text is None:
        return None
    text = child.text.strip()
    return text or None


def set_text(element: ET.Element, name: str, value: str) -> None:
    child = element.find(name)
    if child is None:
        child = ET.SubElement(element, name)
    child.text = value


def read_inner_dwsim_from_curated_zip(source: Path, target: Path) -> str:
    target.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(source) as archive:
        candidates = [
            name
            for name in archive.namelist()
            if Path(name).suffix.lower() in {".dwxmz", ".dwxml"} and not name.endswith("/")
        ]
        if not candidates:
            raise ValueError(f"no DWSIM file found in {source}")
        selected = sorted(candidates)[0]
        with archive.open(selected) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        return selected


def read_dwxmz_xml(path: Path) -> tuple[ET.ElementTree, str, list[str]]:
    if path.suffix.lower() == ".dwxml":
        return ET.parse(path), path.name, []
    with zipfile.ZipFile(path) as archive:
        entries = archive.namelist()
        xml_entries = [name for name in entries if Path(name).suffix.lower() == ".xml"]
        if not xml_entries:
            raise ValueError(f"no XML entry found in {path}")
        xml_name = sorted(xml_entries)[0]
        with archive.open(xml_name) as handle:
            return ET.parse(handle), xml_name, entries


def write_dwxmz_with_xml(source: Path, target: Path, xml_entry: str, tree: ET.ElementTree) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    xml_bytes = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True)
    if source.suffix.lower() == ".dwxml":
        target.write_bytes(xml_bytes)
        return

    with zipfile.ZipFile(source) as src, zipfile.ZipFile(target, "w", zipfile.ZIP_DEFLATED) as dst:
        for entry in src.infolist():
            if entry.filename == xml_entry:
                dst.writestr(entry, xml_bytes)
            else:
                dst.writestr(entry, src.read(entry.filename))


def graphic_tags(root: ET.Element) -> dict[str, str]:
    tags: dict[str, str] = {}
    graphic_objects = root.find("GraphicObjects")
    if graphic_objects is None:
        return tags
    for graphic in graphic_objects:
        name = text_of(graphic, "Name")
        tag = text_of(graphic, "Tag")
        if name and tag:
            tags[name] = tag
    return tags


def simulation_object_types(root: ET.Element) -> dict[str, str]:
    types: dict[str, str] = {}
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        return types
    for obj in simulation_objects:
        guid = text_of(obj, "Name")
        object_type = text_of(obj, "Type")
        if guid and object_type:
            types[guid] = object_type
    return types


def _connector_attached_id(connector: ET.Element, direction: str) -> str | None:
    if connector.attrib.get("IsAttached", "").lower() != "true":
        return None
    if connector.attrib.get("AttachedToEnergyConn", "").lower() == "true":
        return None
    if connector.attrib.get("AttachedFromEnergyConn", "").lower() == "true":
        return None
    key = "AttachedFromObjID" if direction == "upstream" else "AttachedToObjID"
    value = connector.attrib.get(key)
    return value or None


def _is_material_stream_type(object_type: str | None) -> bool:
    return bool(object_type and "MaterialStream" in object_type and "EnergyStream" not in object_type)


def _is_unit_operation_type(object_type: str | None) -> bool:
    if not object_type:
        return False
    return "MaterialStream" not in object_type and "EnergyStream" not in object_type


def stream_graph(root: ET.Element) -> dict[str, Any]:
    tags = graphic_tags(root)
    object_types = simulation_object_types(root)
    graphic_objects = root.find("GraphicObjects")
    streams: list[dict[str, Any]] = []
    if graphic_objects is None:
        return {"streams": streams, "terminal_material_streams": []}

    for graphic in graphic_objects:
        guid = text_of(graphic, "Name")
        if not guid:
            continue
        object_type = object_types.get(guid) or text_of(graphic, "ObjectType")
        if not _is_material_stream_type(object_type):
            continue

        upstream_units: list[str] = []
        downstream_units: list[str] = []
        input_connectors = graphic.find("InputConnectors")
        if input_connectors is not None:
            for connector in input_connectors:
                attached = _connector_attached_id(connector, "upstream")
                if attached and _is_unit_operation_type(object_types.get(attached)):
                    upstream_units.append(attached)
        output_connectors = graphic.find("OutputConnectors")
        if output_connectors is not None:
            for connector in output_connectors:
                attached = _connector_attached_id(connector, "downstream")
                if attached and _is_unit_operation_type(object_types.get(attached)):
                    downstream_units.append(attached)

        is_terminal = bool(upstream_units) and not downstream_units
        streams.append(
            {
                "id": guid,
                "tag": tags.get(guid),
                "type": object_type,
                "upstream_unit_guids": sorted(set(upstream_units)),
                "downstream_unit_guids": sorted(set(downstream_units)),
                "has_upstream_unit": bool(upstream_units),
                "has_downstream_unit": bool(downstream_units),
                "is_terminal_material_stream": is_terminal,
            }
        )

    terminal = [
        {
            "id": item["id"],
            "tag": item.get("tag"),
            "upstream_unit_guids": item["upstream_unit_guids"],
        }
        for item in streams
        if item["is_terminal_material_stream"]
    ]
    return {"streams": streams, "terminal_material_streams": terminal}


def find_distillation_column(root: ET.Element, column_guid: str) -> ET.Element:
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        raise ValueError("missing SimulationObjects section")
    for obj in simulation_objects:
        if text_of(obj, "Type") == "DWSIM.UnitOperations.UnitOperations.DistillationColumn":
            if text_of(obj, "Name") == column_guid:
                return obj
    raise ValueError(f"target column not found: {column_guid}")


def find_unit_by_guid(root: ET.Element, guid: str) -> ET.Element:
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        raise ValueError("missing SimulationObjects section")
    for obj in simulation_objects:
        if text_of(obj, "Name") == guid:
            return obj
    raise ValueError(f"target unit not found: {guid}")


def unit_summary(root: ET.Element, unit: ET.Element) -> dict[str, Any]:
    guid = text_of(unit, "Name")
    tags = graphic_tags(root)
    return {
        "kind": "unit_operation",
        "guid": guid,
        "tag": tags.get(guid or "", ""),
        "type": text_of(unit, "Type"),
        "calc_mode": text_of(unit, "CalcMode"),
    }


def parse_stage_number(stage_name: str | None) -> int | None:
    if not stage_name:
        return None
    match = re.fullmatch(r"Stage_?(\d+)", stage_name.strip())
    return int(match.group(1)) if match else None


def stage_id_for_number(column: ET.Element, stage_number: int) -> str:
    stages = column.find("Stages")
    if stages is None:
        raise ValueError("target column has no Stages section")
    for stage in stages:
        if parse_stage_number(text_of(stage, "Name")) == stage_number:
            stage_id = text_of(stage, "ID")
            if not stage_id:
                raise ValueError(f"stage {stage_number} has no ID")
            return stage_id
    raise ValueError(f"target column has no stage named Stage{stage_number}")


def feed_stage_number(column: ET.Element) -> int:
    material_streams = column.find("MaterialStreams")
    if material_streams is None:
        raise ValueError("target column has no MaterialStreams section")
    feed_streams = [stream for stream in material_streams if text_of(stream, "StreamBehavior") == "Feed"]
    if len(feed_streams) != 1:
        raise ValueError(f"target column must have exactly one feed stream, found {len(feed_streams)}")
    associated_stage = text_of(feed_streams[0], "AssociatedStage")
    if not associated_stage:
        raise ValueError("target feed stream has no AssociatedStage")

    stages = column.find("Stages")
    if stages is None:
        raise ValueError("target column has no Stages section")
    for stage in stages:
        if text_of(stage, "ID") == associated_stage:
            number = parse_stage_number(text_of(stage, "Name"))
            if number is None:
                raise ValueError(f"feed is attached to a non-numbered stage: {text_of(stage, 'Name')}")
            return number
    raise ValueError(f"feed AssociatedStage does not match a column stage: {associated_stage}")


def set_column_feed_stage(tree: ET.ElementTree, column_guid: str, stage_number: int) -> None:
    column = find_distillation_column(tree.getroot(), column_guid)
    stage_id = stage_id_for_number(column, stage_number)
    material_streams = column.find("MaterialStreams")
    if material_streams is None:
        raise ValueError("target column has no MaterialStreams section")
    feed_streams = [stream for stream in material_streams if text_of(stream, "StreamBehavior") == "Feed"]
    if len(feed_streams) != 1:
        raise ValueError(f"target column must have exactly one feed stream, found {len(feed_streams)}")
    set_text(feed_streams[0], "AssociatedStage", stage_id)


def set_column_reflux_ratio(tree: ET.ElementTree, column_guid: str, ratio: str) -> None:
    column = find_distillation_column(tree.getroot(), column_guid)
    set_text(column, "RefluxRatio", ratio)

    specs = column.find("Specs")
    if specs is None:
        raise ValueError("target column has no Specs section")
    updated = False
    for spec in specs:
        if text_of(spec, "SType") == "Stream_Ratio":
            set_text(spec, "SpecValue", ratio)
            set_text(spec, "CalculatedValue", ratio)
            updated = True
    if not updated:
        raise ValueError("target column has no Stream_Ratio ColumnSpec")


def pressure_outlet_value(unit: ET.Element) -> float | None:
    unit_type = text_of(unit, "Type")
    entry = entry_for_parameter(("pressure_specification", "outlet_pressure"))
    if not entry_supports_unit_type(entry, unit_type):
        return None
    field = xml_field_for_unit_type(entry, unit_type)
    value = text_of(unit, field)
    if value is None:
        return None
    try:
        return float(value)
    except ValueError:
        return None


def set_pressure_outlet_pressure(tree: ET.ElementTree, guid: str, value: float, unit: str = "Pa") -> None:
    entry = entry_for_parameter(("pressure_specification", "outlet_pressure"))
    validate_unit_for_entry(entry, unit)
    target = find_unit_by_guid(tree.getroot(), guid)
    unit_type = text_of(target, "Type")
    if not entry_supports_unit_type(entry, unit_type):
        raise ValueError(f"{parameter_key_text(entry['parameter'])} does not support unit type: {unit_type}")
    for field, expected, actual in required_state_mismatches(entry, lambda name: text_of(target, name)):
        raise ValueError(f"{parameter_key_text(entry['parameter'])} requires {field}={expected!r}, found {actual!r}")
    set_text(target, xml_field_for_unit_type(entry, unit_type), repr(float(value)))


def set_thermal_outlet_temperature(tree: ET.ElementTree, guid: str, value: float, unit: str = "K") -> None:
    entry = entry_for_parameter(("thermal_specification", "outlet_temperature"))
    validate_unit_for_entry(entry, unit)
    target = find_unit_by_guid(tree.getroot(), guid)
    unit_type = text_of(target, "Type")
    if not entry_supports_unit_type(entry, unit_type):
        raise ValueError(f"{parameter_key_text(entry['parameter'])} does not support unit type: {unit_type}")
    for field, expected, actual in required_state_mismatches(entry, lambda name: text_of(target, name)):
        raise ValueError(f"{parameter_key_text(entry['parameter'])} requires {field}={expected!r}, found {actual!r}")
    set_text(target, xml_field_for_unit_type(entry, unit_type), repr(float(value)))


def set_separator_pressure(tree: ET.ElementTree, guid: str, value: float, unit: str = "Pa") -> None:
    entry = entry_for_parameter(("separator_specification", "pressure"))
    validate_unit_for_entry(entry, unit)
    target = find_unit_by_guid(tree.getroot(), guid)
    unit_type = text_of(target, "Type")
    if not entry_supports_unit_type(entry, unit_type):
        raise ValueError(f"{parameter_key_text(entry['parameter'])} does not support unit type: {unit_type}")
    for field, expected, actual in required_state_mismatches(entry, lambda name: text_of(target, name)):
        raise ValueError(f"{parameter_key_text(entry['parameter'])} requires {field}={expected!r}, found {actual!r}")
    set_text(target, xml_field_for_unit_type(entry, unit_type), repr(float(value)))


def set_separator_temperature(tree: ET.ElementTree, guid: str, value: float, unit: str = "K") -> None:
    entry = entry_for_parameter(("separator_specification", "temperature"))
    validate_unit_for_entry(entry, unit)
    target = find_unit_by_guid(tree.getroot(), guid)
    unit_type = text_of(target, "Type")
    if not entry_supports_unit_type(entry, unit_type):
        raise ValueError(f"{parameter_key_text(entry['parameter'])} does not support unit type: {unit_type}")
    for field, expected, actual in required_state_mismatches(entry, lambda name: text_of(target, name)):
        raise ValueError(f"{parameter_key_text(entry['parameter'])} requires {field}={expected!r}, found {actual!r}")
    set_text(target, xml_field_for_unit_type(entry, unit_type), repr(float(value)))


def update_dwxmz(source: Path, target: Path, updater: Any) -> None:
    tree, xml_entry, _entries = read_dwxmz_xml(source)
    updater(tree)
    write_dwxmz_with_xml(source, target, xml_entry, tree)


def run_metrics(sim_path: Path, result_path: Path, save_path: Path, column_guid: str) -> dict[str, Any]:
    result_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    for stale_path in (result_path, save_path):
        if stale_path.exists():
            stale_path.unlink()
    command = [
        "powershell",
        "-ExecutionPolicy",
        "Bypass",
        "-File",
        str(METRIC_WORKER),
        "-SimPath",
        str(sim_path),
        "-ResultJsonPath",
        str(result_path),
        "-SavePath",
        str(save_path),
        "-ColumnGuid",
        column_guid,
    ]
    completed = subprocess.run(
        command,
        cwd=repo_root(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    if not result_path.exists():
        raise RuntimeError(f"metric worker did not create {result_path}")
    result = load_json(result_path)
    if isinstance(result, dict):
        result["worker_returncode"] = completed.returncode
        result = sanitize_artifact_paths(result)
        write_json(result_path, result)
    if not is_successful_run(result if isinstance(result, dict) else {}):
        raise RuntimeError(
            f"metric worker failed for {sim_path}; "
            f"returncode={completed.returncode} status={result.get('status') if isinstance(result, dict) else None} "
            f"success={result.get('success') if isinstance(result, dict) else None} "
            f"solved_after={result.get('solved_after') if isinstance(result, dict) else None} "
            f"exception_count={result.get('exception_count') if isinstance(result, dict) else None}\n"
            f"STDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )
    return result


def run_python_script(args: list[str | Path]) -> None:
    command = [sys.executable, *[str(arg) for arg in args]]
    completed = subprocess.run(
        command,
        cwd=repo_root(),
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=180,
        check=False,
    )
    if completed.returncode != 0:
        raise RuntimeError(
            f"script failed: {' '.join(command)}\nSTDOUT:\n{completed.stdout}\nSTDERR:\n{completed.stderr}"
        )


def run_generate_llm_input(instance_path: Path, output_path: Path, prompt_mode: str = "oracle-parameter") -> None:
    run_python_script([GENERATE_LLM_INPUT, "--instance", instance_path, "--output", output_path, "--prompt-mode", prompt_mode])


def run_apply_repair_actions(input_flowsheet: Path, repair_output: Path, repair_actions_json: Path) -> None:
    if repair_output.exists():
        repair_output.unlink()
    run_python_script(
        [
            APPLY_REPAIR_ACTIONS,
            "--input-flowsheet",
            input_flowsheet,
            "--repair-output",
            repair_output,
            "--repair-actions-json",
            repair_actions_json,
        ]
    )


def is_successful_run(run: dict[str, Any]) -> bool:
    return is_successful_dwsim_run(run)


def stream_key(stream: dict[str, Any]) -> str:
    return str(stream.get("tag") or stream.get("id") or "")


def component_metric(run: dict[str, Any], tag: str, component: str, metric: str = "mole_fraction") -> float | None:
    for stream in run.get("streams", []):
        if stream_key(stream) != tag:
            continue
        value = stream.get("compounds", {}).get(component, {}).get(metric)
        return value if isinstance(value, (int, float)) else None
    return None


def base_threshold(value: float) -> float:
    return math.floor(value * 100.0) / 100.0


def target_candidates(base_run: dict[str, Any], components: tuple[str, ...] = COMPONENTS) -> list[dict[str, Any]]:
    candidates: list[dict[str, Any]] = []
    for stream in base_run.get("streams", []):
        tag = stream_key(stream)
        if not tag:
            continue
        compounds = stream.get("compounds", {})
        for component in components:
            metrics = compounds.get(component, {})
            mole_fraction = metrics.get("mole_fraction")
            molar_flow = metrics.get("molar_flow")
            if not isinstance(mole_fraction, (int, float)) or not isinstance(molar_flow, (int, float)):
                continue
            if mole_fraction < 0.5 or molar_flow <= 1e-8:
                continue
            threshold = base_threshold(float(mole_fraction))
            if threshold <= 0:
                continue
            candidates.append(
                {
                    "stream_tag": tag,
                    "stream_id": stream.get("id"),
                    "component": component,
                    "base_mole_fraction": float(mole_fraction),
                    "base_molar_flow": float(molar_flow),
                    "product_mole_fraction_min": threshold,
                }
            )
    return candidates


def compact_candidate_result(parameter_name: str, value: Any, faulty_run: dict[str, Any], repaired_run: dict[str, Any]) -> dict[str, Any]:
    return {
        parameter_name: value,
        "faulty_success": is_successful_run(faulty_run),
        "repaired_success": is_successful_run(repaired_run),
        "faulty_exception_count": faulty_run.get("exception_count"),
        "repaired_exception_count": repaired_run.get("exception_count"),
    }


def write_topology(faulty_path: Path, output_path: Path, target_column: dict[str, Any], extraction_note: str) -> None:
    tree, _xml_entry, _entries = read_dwxmz_xml(faulty_path)
    root = tree.getroot()
    tags = graphic_tags(root)
    simulation_objects = root.find("SimulationObjects")
    graphic_objects = root.find("GraphicObjects")

    objects: list[dict[str, Any]] = []
    if simulation_objects is not None:
        for obj in simulation_objects:
            guid = text_of(obj, "Name")
            objects.append(
                {
                    "guid": guid,
                    "tag": tags.get(guid or ""),
                    "type": text_of(obj, "Type"),
                    "object_class": text_of(obj, "ObjectClass"),
                    "component_description": text_of(obj, "ComponentDescription"),
                }
            )

    graphics: list[dict[str, Any]] = []
    if graphic_objects is not None:
        for graphic in graphic_objects:
            graphics.append(
                {
                    "name": text_of(graphic, "Name"),
                    "tag": text_of(graphic, "Tag"),
                    "object_type": text_of(graphic, "ObjectType"),
                }
            )
    graph = stream_graph(root)

    write_json(
        output_path,
        {
            "schema_version": "draft-0",
            "extraction_note": extraction_note,
            "simulation_object_count": len(objects),
            "graphic_object_count": len(graphics),
            "objects": objects,
            "graphic_objects": graphics,
            "stream_graph": graph,
            "terminal_material_streams": graph["terminal_material_streams"],
            "target_column": target_column,
            "target_unit": target_column,
        },
    )


def write_parameters(
    faulty_run: dict[str, Any],
    target: dict[str, Any],
    output_path: Path,
    target_parameter: dict[str, str],
) -> None:
    write_json(
        output_path,
        {
            "schema_version": "draft-0",
            "extraction_note": "Parameters extracted from the calculated faulty flowsheet.",
            "target_column": faulty_run.get("column"),
            "target_parameter": target_parameter,
            "product_target": {
                "stream_tag": target["stream_tag"],
                "component": target["component"],
                "product_mole_fraction_min": target["product_mole_fraction_min"],
            },
        },
    )


def stream_components(run: dict[str, Any]) -> tuple[str, ...]:
    components: set[str] = set()
    for stream in run.get("streams", []):
        compounds = stream.get("compounds") if isinstance(stream, dict) else None
        if isinstance(compounds, dict):
            components.update(str(component) for component in compounds)
    return tuple(sorted(components)) or COMPONENTS


def write_stream_table(run: dict[str, Any], output_path: Path, components: tuple[str, ...] | None = None) -> None:
    if components is None:
        components = stream_components(run)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    component_fields = []
    for component in components:
        prefix = component.lower()
        component_fields.extend([f"{prefix}_mole_fraction", f"{prefix}_molar_flow"])
    fieldnames = [
        "stream_tag",
        "stream_id",
        "temperature",
        "pressure",
        "molar_flow",
        "mass_flow",
        *component_fields,
    ]
    with output_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for stream in run.get("streams", []):
            row: dict[str, Any] = {
                "stream_tag": stream.get("tag"),
                "stream_id": stream.get("id"),
                "temperature": stream.get("temperature"),
                "pressure": stream.get("pressure"),
                "molar_flow": stream.get("molar_flow"),
                "mass_flow": stream.get("mass_flow"),
            }
            for component in components:
                prefix = component.lower()
                metrics = stream.get("compounds", {}).get(component, {})
                row[f"{prefix}_mole_fraction"] = metrics.get("mole_fraction")
                row[f"{prefix}_molar_flow"] = metrics.get("molar_flow")
            writer.writerow(row)


def write_log(run: dict[str, Any], target: dict[str, Any], output_path: Path) -> None:
    target_value = component_metric(run, target["stream_tag"], target["component"])
    lines = [
        f"DWSIM headless status: {run.get('status')}",
        f"Solved after calculation: {run.get('solved_after')}",
        f"Exception count: {run.get('exception_count')}",
        f"Messages log count: {run.get('messages_log_count')}",
        f"Target stream: {target['stream_tag']}",
        f"Target component: {target['component']}",
        f"Observed target mole fraction: {target_value}",
        f"Required target mole fraction: {target['product_mole_fraction_min']:.2f}",
    ]
    for exception in run.get("exceptions", []):
        lines.append(f"Exception: {exception.get('type')}: {exception.get('message')}")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def extract_source_metadata(
    base_path: Path,
    source_archive: Path,
    source_entry: str,
    source_name: str,
    base_run: dict[str, Any],
) -> dict[str, Any]:
    tree, _xml_entry, entries = read_dwxmz_xml(base_path)
    root = tree.getroot()
    sections = [child.tag for child in root]
    supported = {
        "GeneralInfo",
        "SimulationObjects",
        "Settings",
        "GraphicObjects",
        "PropertyPackages",
        "Compounds",
        "ReactionSets",
        "Reactions",
        "Spreadsheet",
        "MessagesLog",
    }
    simulation_objects = root.find("SimulationObjects")
    return {
        "source_format": base_path.suffix.lower().lstrip("."),
        "source_name": source_name,
        "license": "Creative Commons Attribution-ShareAlike 4.0 International License",
        "retrieved_at": date.today().isoformat(),
        "dwsim_build_version": base_run.get("dwsim_version", "DWSIM version unknown"),
        "internal_archive_entries": entries,
        "contains_database": any(Path(name).suffix.lower() == ".db" for name in entries),
        "root_element": root.tag,
        "sections": sections,
        "object_count": len(simulation_objects) if simulation_objects is not None else 0,
        "unsupported_sections": [section for section in sections if section not in supported],
        "curated_archive": artifact_path(source_archive),
        "curated_source_entry": source_entry,
    }


def gold_proximity(actual: dict[str, Any], expected: dict[str, Any]) -> dict[str, Any]:
    actual_target = actual.get("target") if isinstance(actual.get("target"), dict) else {}
    expected_target = expected.get("target") if isinstance(expected.get("target"), dict) else {}
    actual_parameter = actual.get("parameter") if isinstance(actual.get("parameter"), dict) else {}
    expected_parameter = expected.get("parameter") if isinstance(expected.get("parameter"), dict) else {}
    actual_value = actual.get("value")
    expected_value = expected.get("value")
    value_abs_error = None
    value_rel_error = None
    if isinstance(actual_value, (int, float)) and isinstance(expected_value, (int, float)):
        value_abs_error = abs(float(actual_value) - float(expected_value))
        denominator = max(abs(float(expected_value)), 1e-12)
        value_rel_error = value_abs_error / denominator
    return {
        "target_match": actual_target.get("guid") == expected_target.get("guid")
        and actual_target.get("tag") == expected_target.get("tag")
        and actual_target.get("kind") == expected_target.get("kind"),
        "parameter_match": actual_parameter.get("namespace") == expected_parameter.get("namespace")
        and actual_parameter.get("name") == expected_parameter.get("name"),
        "unit_match": actual.get("unit") == expected.get("unit"),
        "value_abs_error": value_abs_error,
        "value_rel_error": value_rel_error,
    }
