#!/usr/bin/env python3
"""Apply canonical repair actions to a DWSIM flowsheet."""

from __future__ import annotations

import argparse
import json
import re
import shutil
import sys
import zipfile
from pathlib import Path
from typing import Any
from xml.etree import ElementTree as ET

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repair_registry import entry_for_parameter, required_state_mismatches, validate_unit_for_entry, xml_field_for_unit_type  # noqa: E402

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover - exercised only before dependencies exist.
    print(
        "ERROR: missing dependency 'jsonschema'. Install with: pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(2)


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


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


def read_dwsim_xml(path: Path) -> tuple[ET.ElementTree, str | None]:
    if path.suffix.lower() == ".dwxml":
        return ET.parse(path), None
    with zipfile.ZipFile(path) as archive:
        xml_entries = [name for name in archive.namelist() if Path(name).suffix.lower() == ".xml"]
        if not xml_entries:
            raise ValueError(f"no XML entry found in {path}")
        xml_entry = sorted(xml_entries)[0]
        with archive.open(xml_entry) as handle:
            return ET.parse(handle), xml_entry


def write_dwsim_xml(source: Path, target: Path, xml_entry: str | None, tree: ET.ElementTree) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    xml_bytes = ET.tostring(tree.getroot(), encoding="utf-8", xml_declaration=True)
    if source.suffix.lower() == ".dwxml":
        target.write_bytes(xml_bytes)
        return

    if source.resolve() == target.resolve():
        temporary = target.with_suffix(target.suffix + ".tmp")
    else:
        temporary = target

    with zipfile.ZipFile(source) as src, zipfile.ZipFile(temporary, "w", zipfile.ZIP_DEFLATED) as dst:
        for entry in src.infolist():
            if entry.filename == xml_entry:
                dst.writestr(entry, xml_bytes)
            else:
                dst.writestr(entry, src.read(entry.filename))

    if temporary != target:
        shutil.move(str(temporary), target)


def repair_actions(payload: Any) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        actions = payload
    elif isinstance(payload, dict):
        actions = payload.get("repair_actions")
    else:
        raise ValueError("repair action input must be an object or array")

    if not isinstance(actions, list) or not actions:
        raise ValueError("repair_actions must be a non-empty array")
    if not all(isinstance(action, dict) for action in actions):
        raise ValueError("each repair action must be a JSON object")
    return actions


def validate_actions(actions: list[dict[str, Any]], schema_path: Path) -> None:
    schema = load_json(schema_path)
    validator = Draft202012Validator(schema)
    for index, action in enumerate(actions):
        errors = sorted(validator.iter_errors(action), key=lambda error: list(error.absolute_path))
        if errors:
            messages: list[str] = []
            for error in errors:
                location = ".".join(str(part) for part in error.absolute_path)
                prefix = f"repair_actions[{index}]"
                if location:
                    prefix = f"{prefix}.{location}"
                messages.append(f"{prefix}: {error.message}")
            raise ValueError("; ".join(messages))


def find_column_by_guid(root: ET.Element, guid: str) -> ET.Element:
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        raise ValueError("missing SimulationObjects section")
    for obj in simulation_objects:
        if text_of(obj, "Type") == "DWSIM.UnitOperations.UnitOperations.DistillationColumn":
            if text_of(obj, "Name") == guid:
                return obj
    raise ValueError(f"target distillation column not found: {guid}")


def find_unit_by_guid(root: ET.Element, guid: str) -> ET.Element:
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        raise ValueError("missing SimulationObjects section")
    for obj in simulation_objects:
        if text_of(obj, "Name") == guid:
            return obj
    raise ValueError(f"target unit operation not found: {guid}")


def target_guid(action: dict[str, Any]) -> str:
    target = action.get("target")
    if not isinstance(target, dict):
        raise ValueError("set_unit_parameter.target must be an object")
    if target.get("kind") != "unit_operation":
        raise ValueError("set_unit_parameter.target.kind must be 'unit_operation'")
    guid = target.get("guid")
    if not isinstance(guid, str) or not guid:
        raise ValueError("set_unit_parameter requires target.guid")
    return guid


def parameter_ref(action: dict[str, Any]) -> tuple[str, str]:
    parameter = action.get("parameter")
    if not isinstance(parameter, dict):
        raise ValueError("set_unit_parameter.parameter must be an object")
    namespace = parameter.get("namespace")
    name = parameter.get("name")
    if not isinstance(namespace, str) or not namespace:
        raise ValueError("set_unit_parameter.parameter.namespace must be a non-empty string")
    if not isinstance(name, str) or not name:
        raise ValueError("set_unit_parameter.parameter.name must be a non-empty string")
    return namespace, name


def apply_set_column_reflux_ratio(tree: ET.ElementTree, action: dict[str, Any]) -> None:
    guid = target_guid(action)
    value = action.get("value")
    if not isinstance(value, (int, float)):
        raise ValueError("set_unit_parameter.value must be numeric")
    if action.get("unit") is not None:
        raise ValueError("column_specification/reflux_ratio requires unit=null")
    ratio_text = repr(float(value))

    column = find_column_by_guid(tree.getroot(), guid)
    set_text(column, "RefluxRatio", ratio_text)

    specs = column.find("Specs")
    if specs is None:
        raise ValueError(f"target column has no Specs section: {guid}")

    updated = False
    for spec in specs:
        if text_of(spec, "SType") == "Stream_Ratio":
            set_text(spec, "SpecValue", ratio_text)
            set_text(spec, "CalculatedValue", ratio_text)
            updated = True

    if not updated:
        raise ValueError(f"target column has no Stream_Ratio ColumnSpec: {guid}")


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
    raise ValueError(f"target column has no numbered stage {stage_number}")


def apply_set_column_feed_stage(tree: ET.ElementTree, action: dict[str, Any]) -> None:
    guid = target_guid(action)
    value = action.get("value")
    if isinstance(value, bool) or not isinstance(value, int):
        raise ValueError("column_configuration/feed_stage requires integer value")
    if value < 1:
        raise ValueError("column_configuration/feed_stage requires value >= 1")
    if action.get("unit") is not None:
        raise ValueError("column_configuration/feed_stage requires unit=null")

    column = find_column_by_guid(tree.getroot(), guid)
    stage_id = stage_id_for_number(column, value)
    material_streams = column.find("MaterialStreams")
    if material_streams is None:
        raise ValueError(f"target column has no MaterialStreams section: {guid}")
    feed_streams = [stream for stream in material_streams if text_of(stream, "StreamBehavior") == "Feed"]
    if len(feed_streams) != 1:
        raise ValueError(f"target column must have exactly one feed stream, found {len(feed_streams)}: {guid}")
    set_text(feed_streams[0], "AssociatedStage", stage_id)


def apply_set_pressure_outlet_pressure(tree: ET.ElementTree, action: dict[str, Any]) -> None:
    guid = target_guid(action)
    value = action.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
        raise ValueError("pressure_specification/outlet_pressure requires positive numeric value")

    entry = entry_for_parameter(("pressure_specification", "outlet_pressure"))
    validate_unit_for_entry(entry, action.get("unit"))
    unit = find_unit_by_guid(tree.getroot(), guid)
    unit_type = text_of(unit, "Type")
    if unit_type not in entry["dwsim_unit_types"]:
        raise ValueError(f"pressure_specification/outlet_pressure does not support unit type: {unit_type}")

    for field, expected, actual in required_state_mismatches(entry, lambda name: text_of(unit, name)):
        raise ValueError(f"pressure_specification/outlet_pressure requires {field}={expected!r}, found {actual!r}")

    set_text(unit, xml_field_for_unit_type(entry, unit_type), repr(float(value)))


def apply_set_thermal_outlet_temperature(tree: ET.ElementTree, action: dict[str, Any]) -> None:
    guid = target_guid(action)
    value = action.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
        raise ValueError("thermal_specification/outlet_temperature requires positive numeric value")

    entry = entry_for_parameter(("thermal_specification", "outlet_temperature"))
    validate_unit_for_entry(entry, action.get("unit"))
    unit = find_unit_by_guid(tree.getroot(), guid)
    unit_type = text_of(unit, "Type")
    if unit_type not in entry["dwsim_unit_types"]:
        raise ValueError(f"thermal_specification/outlet_temperature does not support unit type: {unit_type}")

    for field, expected, actual in required_state_mismatches(entry, lambda name: text_of(unit, name)):
        raise ValueError(f"thermal_specification/outlet_temperature requires {field}={expected!r}, found {actual!r}")

    set_text(unit, xml_field_for_unit_type(entry, unit_type), repr(float(value)))


def apply_set_separator_pressure(tree: ET.ElementTree, action: dict[str, Any]) -> None:
    guid = target_guid(action)
    value = action.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
        raise ValueError("separator_specification/pressure requires positive numeric value")

    entry = entry_for_parameter(("separator_specification", "pressure"))
    validate_unit_for_entry(entry, action.get("unit"))
    unit = find_unit_by_guid(tree.getroot(), guid)
    unit_type = text_of(unit, "Type")
    if unit_type not in entry["dwsim_unit_types"]:
        raise ValueError(f"separator_specification/pressure does not support unit type: {unit_type}")

    for field, expected, actual in required_state_mismatches(entry, lambda name: text_of(unit, name)):
        raise ValueError(f"separator_specification/pressure requires {field}={expected!r}, found {actual!r}")

    set_text(unit, xml_field_for_unit_type(entry, unit_type), repr(float(value)))


def apply_set_separator_temperature(tree: ET.ElementTree, action: dict[str, Any]) -> None:
    guid = target_guid(action)
    value = action.get("value")
    if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
        raise ValueError("separator_specification/temperature requires positive numeric value")

    entry = entry_for_parameter(("separator_specification", "temperature"))
    validate_unit_for_entry(entry, action.get("unit"))
    unit = find_unit_by_guid(tree.getroot(), guid)
    unit_type = text_of(unit, "Type")
    if unit_type not in entry["dwsim_unit_types"]:
        raise ValueError(f"separator_specification/temperature does not support unit type: {unit_type}")

    for field, expected, actual in required_state_mismatches(entry, lambda name: text_of(unit, name)):
        raise ValueError(f"separator_specification/temperature requires {field}={expected!r}, found {actual!r}")

    set_text(unit, xml_field_for_unit_type(entry, unit_type), repr(float(value)))


def apply_action(tree: ET.ElementTree, action: dict[str, Any]) -> None:
    action_type = action.get("type")
    if action_type == "set_unit_parameter":
        namespace, name = parameter_ref(action)
        if (namespace, name) == ("column_specification", "reflux_ratio"):
            apply_set_column_reflux_ratio(tree, action)
            return
        if (namespace, name) == ("column_configuration", "feed_stage"):
            apply_set_column_feed_stage(tree, action)
            return
        if (namespace, name) == ("pressure_specification", "outlet_pressure"):
            apply_set_pressure_outlet_pressure(tree, action)
            return
        if (namespace, name) == ("thermal_specification", "outlet_temperature"):
            apply_set_thermal_outlet_temperature(tree, action)
            return
        if (namespace, name) == ("separator_specification", "pressure"):
            apply_set_separator_pressure(tree, action)
            return
        if (namespace, name) == ("separator_specification", "temperature"):
            apply_set_separator_temperature(tree, action)
            return
        raise ValueError(f"unsupported unit parameter: {namespace}/{name}")
    raise ValueError(f"unsupported repair action type: {action_type!r}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input-flowsheet", required=True, type=Path)
    parser.add_argument("--repair-output", required=True, type=Path)
    parser.add_argument("--repair-actions-json", required=True, type=Path)
    parser.add_argument("--schema", default=Path("schemas/repair_action.schema.json"), type=Path)
    args = parser.parse_args()

    try:
        actions = repair_actions(load_json(args.repair_actions_json))
        validate_actions(actions, args.schema)
        tree, xml_entry = read_dwsim_xml(args.input_flowsheet)
        for action in actions:
            apply_action(tree, action)
        write_dwsim_xml(args.input_flowsheet, args.repair_output, xml_entry, tree)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Applied {len(actions)} repair action(s) to {args.repair_output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
