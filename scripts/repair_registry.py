"""Shared v0.1/v0.1.5 repair action registry."""

from __future__ import annotations

from typing import Any


PROMPT_MODES = {"oracle-parameter", "parameter-selection"}

DISTILLATION_COLUMN_TYPE = "DWSIM.UnitOperations.UnitOperations.DistillationColumn"
VALVE_TYPE = "DWSIM.UnitOperations.UnitOperations.Valve"
PUMP_TYPE = "DWSIM.UnitOperations.UnitOperations.Pump"
COMPRESSOR_TYPE = "DWSIM.UnitOperations.UnitOperations.Compressor"
HEATER_TYPE = "DWSIM.UnitOperations.UnitOperations.Heater"
COOLER_TYPE = "DWSIM.UnitOperations.UnitOperations.Cooler"
VESSEL_TYPE = "DWSIM.UnitOperations.UnitOperations.Vessel"

RELEASE_PROFILE = "release"
PILOT_PROFILE = "pilot"

REGISTRY: tuple[dict[str, Any], ...] = (
    {
        "key": "column_specification/reflux_ratio",
        "support_level": "release-supported",
        "profiles": {RELEASE_PROFILE, PILOT_PROFILE},
        "target_kind": "unit_operation",
        "dwsim_unit_types": (DISTILLATION_COLUMN_TYPE,),
        "parameter": {"namespace": "column_specification", "name": "reflux_ratio"},
        "value_type": "number",
        "minimum": None,
        "unit": None,
        "unit_policy": "must_be_null",
        "xml_field": "RefluxRatio",
        "required_unit_state": {},
        "discovery_perturbation": {"type": "multipliers", "values": (0.1, 0.3, 0.5, 0.7, 0.9, 1.2, 1.5)},
    },
    {
        "key": "column_configuration/feed_stage",
        "support_level": "release-supported",
        "profiles": {RELEASE_PROFILE, PILOT_PROFILE},
        "target_kind": "unit_operation",
        "dwsim_unit_types": (DISTILLATION_COLUMN_TYPE,),
        "parameter": {"namespace": "column_configuration", "name": "feed_stage"},
        "value_type": "integer",
        "minimum": 1,
        "unit": None,
        "unit_policy": "must_be_null",
        "xml_field": "AssociatedStage",
        "required_unit_state": {},
        "discovery_perturbation": {
            "type": "feed_stage_candidates",
            "deltas": (-4, -3, -2, -1, 1, 2, 3, 4),
            "positions": (0.2, 0.35, 0.5, 0.65, 0.8),
        },
    },
    {
        "key": "pressure_specification/outlet_pressure",
        "support_level": "pilot-supported",
        "profiles": {PILOT_PROFILE},
        "target_kind": "unit_operation",
        "dwsim_unit_types": (VALVE_TYPE, PUMP_TYPE, COMPRESSOR_TYPE),
        "parameter": {"namespace": "pressure_specification", "name": "outlet_pressure"},
        "value_type": "number",
        "minimum": 0.0,
        "unit": "Pa",
        "unit_policy": "must_equal",
        "xml_field_by_unit_type": {
            VALVE_TYPE: "OutletPressure",
            PUMP_TYPE: "Pout",
            COMPRESSOR_TYPE: "POut",
        },
        "required_unit_state": {"CalcMode": "OutletPressure"},
        "discovery_perturbation": {"type": "multipliers", "values": (0.5, 0.7, 0.9, 1.1, 1.3, 1.5)},
    },
    {
        "key": "thermal_specification/outlet_temperature",
        "support_level": "pilot-supported",
        "profiles": {PILOT_PROFILE},
        "target_kind": "unit_operation",
        "dwsim_unit_types": (HEATER_TYPE, COOLER_TYPE),
        "parameter": {"namespace": "thermal_specification", "name": "outlet_temperature"},
        "value_type": "number",
        "minimum": 0.0,
        "unit": "K",
        "unit_policy": "must_equal",
        "xml_field": "OutletTemperature",
        "required_unit_state": {"CalcMode": "OutletTemperature"},
        "discovery_perturbation": {"type": "offsets", "values": (-30.0, -20.0, -10.0, 10.0, 20.0, 30.0)},
    },
    {
        "key": "separator_specification/pressure",
        "support_level": "pilot-supported",
        "profiles": {PILOT_PROFILE},
        "target_kind": "unit_operation",
        "dwsim_unit_types": (VESSEL_TYPE,),
        "parameter": {"namespace": "separator_specification", "name": "pressure"},
        "value_type": "number",
        "minimum": 0.0,
        "unit": "Pa",
        "unit_policy": "must_equal",
        "xml_field": "FlashPressure",
        "required_unit_state": {"OverrideP": "true"},
        "discovery_perturbation": {"type": "multipliers", "values": (0.5, 0.7, 0.9, 1.1, 1.3, 1.5)},
    },
    {
        "key": "separator_specification/temperature",
        "support_level": "pilot-supported",
        "profiles": {PILOT_PROFILE},
        "target_kind": "unit_operation",
        "dwsim_unit_types": (VESSEL_TYPE,),
        "parameter": {"namespace": "separator_specification", "name": "temperature"},
        "value_type": "number",
        "minimum": 0.0,
        "unit": "K",
        "unit_policy": "must_equal",
        "xml_field": "FlashTemperature",
        "required_unit_state": {"OverrideT": "true"},
        "discovery_perturbation": {"type": "offsets", "values": (-30.0, -20.0, -10.0, 10.0, 20.0, 30.0)},
    },
)


def parameter_key(parameter: dict[str, Any] | None) -> tuple[str, str] | None:
    if not isinstance(parameter, dict):
        return None
    namespace = parameter.get("namespace")
    name = parameter.get("name")
    if not isinstance(namespace, str) or not isinstance(name, str):
        return None
    return namespace, name


def parameter_key_text(parameter: dict[str, Any] | tuple[str, str] | None) -> str:
    if isinstance(parameter, tuple):
        return f"{parameter[0]}/{parameter[1]}"
    key = parameter_key(parameter)
    return f"{key[0]}/{key[1]}" if key else "unknown/unknown"


def entry_for_parameter(parameter: dict[str, Any] | tuple[str, str]) -> dict[str, Any]:
    key = parameter if isinstance(parameter, tuple) else parameter_key(parameter)
    for entry in REGISTRY:
        if parameter_key(entry["parameter"]) == key:
            return entry
    raise KeyError(f"unsupported repair parameter: {parameter_key_text(parameter)}")


def entries_for_profile(profile: str) -> tuple[dict[str, Any], ...]:
    return tuple(entry for entry in REGISTRY if profile in entry["profiles"])


def supported_parameter_keys(profile: str) -> set[tuple[str, str]]:
    return {parameter_key(entry["parameter"]) for entry in entries_for_profile(profile)}  # type: ignore[misc]


def entry_supports_unit_type(entry: dict[str, Any], unit_type: str | None) -> bool:
    if not isinstance(unit_type, str):
        return False
    return unit_type in entry.get("dwsim_unit_types", ())


def required_state_value_matches(actual: Any, expected: Any) -> bool:
    if actual is None:
        return False
    if isinstance(expected, str):
        actual_text = str(actual).strip()
        expected_text = expected.strip()
        if expected_text.lower() in {"true", "false"}:
            return actual_text.lower() == expected_text.lower()
        return actual_text == expected_text
    return actual == expected


def required_state_mismatches(entry: dict[str, Any], value_getter: Any) -> list[tuple[str, Any, Any]]:
    required = entry.get("required_unit_state")
    if not isinstance(required, dict):
        return []
    mismatches: list[tuple[str, Any, Any]] = []
    for field, expected in required.items():
        actual = value_getter(field)
        if not required_state_value_matches(actual, expected):
            mismatches.append((field, expected, actual))
    return mismatches


def xml_field_for_unit_type(entry: dict[str, Any], unit_type: str | None) -> str:
    fields = entry.get("xml_field_by_unit_type")
    if isinstance(fields, dict):
        field = fields.get(unit_type)
        if isinstance(field, str):
            return field
    field = entry.get("xml_field")
    if isinstance(field, str):
        return field
    raise KeyError(f"no XML field for {entry['key']} on unit type {unit_type!r}")


def parameter_label(parameter: dict[str, Any] | tuple[str, str]) -> str:
    key = parameter_key_text(parameter)
    labels = {
        "column_specification/reflux_ratio": "reflux ratio",
        "column_configuration/feed_stage": "feed stage",
        "pressure_specification/outlet_pressure": "outlet pressure",
        "thermal_specification/outlet_temperature": "outlet temperature",
        "separator_specification/pressure": "separator pressure",
        "separator_specification/temperature": "separator temperature",
    }
    return labels.get(key, key)


def normalize_value_for_entry(entry: dict[str, Any], value: Any, field_name: str) -> int | float:
    if entry["value_type"] == "integer":
        if isinstance(value, bool) or not isinstance(value, int):
            raise ValueError(f"{field_name} must be an integer for {entry['key']}")
        minimum = entry.get("minimum")
        if isinstance(minimum, (int, float)) and value < minimum:
            raise ValueError(f"{field_name} must be >= {minimum:g} for {entry['key']}")
        return value
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric for {entry['key']}")
    value = float(value)
    minimum = entry.get("minimum")
    if isinstance(minimum, (int, float)) and value <= minimum:
        raise ValueError(f"{field_name} must be > {minimum:g} for {entry['key']}")
    return value


def validate_unit_for_entry(entry: dict[str, Any], unit: Any) -> None:
    if entry.get("unit_policy") == "must_be_null":
        if unit is not None:
            raise ValueError(f"{entry['key']} requires unit=null")
        return
    expected = entry.get("unit")
    if unit != expected:
        raise ValueError(f"{entry['key']} requires unit={expected!r}")


def value_schema_for_entry(entry: dict[str, Any]) -> dict[str, Any]:
    if entry["value_type"] == "integer":
        schema: dict[str, Any] = {"type": "integer"}
    else:
        schema = {"type": "number"}
    minimum = entry.get("minimum")
    if isinstance(minimum, (int, float)):
        if entry["value_type"] == "integer":
            schema["minimum"] = minimum
        else:
            schema["exclusiveMinimum"] = minimum
    return schema


def unit_schema_for_entry(entry: dict[str, Any]) -> dict[str, Any]:
    if entry.get("unit_policy") == "must_be_null":
        return {"type": "null"}
    return {"type": "string", "enum": [entry["unit"]]}


def action_pair_label(pair: dict[str, Any]) -> str:
    target = pair.get("target") if isinstance(pair.get("target"), dict) else {}
    parameter = pair.get("parameter") if isinstance(pair.get("parameter"), dict) else {}
    tag = target.get("tag") or target.get("guid") or "target"
    return f"{tag}: {parameter_key_text(parameter)}"


def normalize_allowed_action_pair(pair: dict[str, Any]) -> dict[str, Any]:
    target = pair.get("target")
    parameter = pair.get("parameter")
    if not isinstance(target, dict) or not isinstance(parameter, dict):
        raise ValueError("allowed_repair_actions entries must include target and parameter objects")
    entry = entry_for_parameter(parameter)
    guid = target.get("guid")
    if not isinstance(guid, str) or not guid:
        raise ValueError("allowed repair action target.guid is required")
    normalized = {
        "target": {
            "kind": target.get("kind") or entry["target_kind"],
            "guid": guid,
        },
        "parameter": {"namespace": entry["parameter"]["namespace"], "name": entry["parameter"]["name"]},
        "unit": entry["unit"],
        "value_type": entry["value_type"],
        "support_level": entry["support_level"],
    }
    for key in ("tag", "type"):
        if isinstance(target.get(key), str):
            normalized["target"][key] = target[key]
    normalized["label"] = pair.get("label") if isinstance(pair.get("label"), str) else action_pair_label(normalized)
    return normalized


def action_schema_for_pair(pair: dict[str, Any]) -> dict[str, Any]:
    pair = normalize_allowed_action_pair(pair)
    entry = entry_for_parameter(pair["parameter"])
    target = pair["target"]
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
                    "kind": {"type": "string", "enum": [entry["target_kind"]]},
                    "guid": {"type": "string", "enum": [target["guid"]]},
                    "tag": {"type": "string"},
                },
            },
            "parameter": {
                "type": "object",
                "additionalProperties": False,
                "required": ["namespace", "name"],
                "properties": {
                    "namespace": {"type": "string", "enum": [entry["parameter"]["namespace"]]},
                    "name": {"type": "string", "enum": [entry["parameter"]["name"]]},
                },
            },
            "value": value_schema_for_entry(entry),
            "unit": unit_schema_for_entry(entry),
            "rationale": {"type": "string"},
        },
    }


def pair_from_target_and_entry(target: dict[str, Any], entry: dict[str, Any]) -> dict[str, Any]:
    return normalize_allowed_action_pair(
        {
            "target": {
                "kind": target.get("kind") or entry["target_kind"],
                "guid": target["guid"],
                "tag": target.get("tag"),
                "type": target.get("type"),
            },
            "parameter": entry["parameter"],
        }
    )
