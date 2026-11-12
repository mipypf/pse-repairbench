#!/usr/bin/env python3
"""Validate PSE-RepairBench instance manifests."""

from __future__ import annotations

import argparse
import json
import math
import zipfile
import sys
import warnings
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from dwsim_run_contract import is_successful_dwsim_run  # noqa: E402
from repair_registry import entry_for_parameter, supported_parameter_keys, validate_unit_for_entry  # noqa: E402

warnings.filterwarnings("ignore", category=DeprecationWarning)

try:
    from jsonschema import Draft202012Validator, RefResolver
    from jsonschema.exceptions import ValidationError
except ImportError:  # pragma: no cover - exercised only before dependencies exist.
    print(
        "ERROR: missing dependency 'jsonschema'. Install with: pip install -r requirements.txt",
        file=sys.stderr,
    )
    raise SystemExit(2)


PLACEHOLDER_VALUES = {"pending", "not-yet-implemented"}
REPRO_VERSION_FIELDS = {
    "fault_injector_version",
    "observation_extractor_version",
    "executor_version",
    "dwsim_runner_version",
    "evaluator_version",
}
RELEASE_SUPPORTED_PARAMETERS = supported_parameter_keys("release")
PILOT_SUPPORTED_PARAMETERS = supported_parameter_keys("pilot")


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8-sig"))
    except Exception as exc:  # noqa: BLE001
        raise ValueError(f"failed to parse JSON: {exc}") from exc


def schema_validator(repo_root: Path) -> Draft202012Validator:
    schema_dir = repo_root / "schemas"
    instance_schema = load_json(schema_dir / "instance.schema.json")
    repair_action_schema = load_json(schema_dir / "repair_action.schema.json")
    repair_output_schema = load_json(schema_dir / "repair_output.schema.json")
    repair_action_uri = (schema_dir / "repair_action.schema.json").resolve().as_uri()
    repair_output_uri = (schema_dir / "repair_output.schema.json").resolve().as_uri()
    store = {
        instance_schema["$id"]: instance_schema,
        repair_action_schema["$id"]: repair_action_schema,
        repair_output_schema["$id"]: repair_output_schema,
        repair_action_uri: repair_action_schema,
        repair_output_uri: repair_output_schema,
    }
    resolver = RefResolver(
        base_uri=(schema_dir / "instance.schema.json").resolve().as_uri(),
        referrer=instance_schema,
        store=store,
    )
    Draft202012Validator.check_schema(instance_schema)
    Draft202012Validator.check_schema(repair_action_schema)
    Draft202012Validator.check_schema(repair_output_schema)
    return Draft202012Validator(instance_schema, resolver=resolver)


def repair_action_validator(repo_root: Path) -> Draft202012Validator:
    schema = load_json(repo_root / "schemas" / "repair_action.schema.json")
    Draft202012Validator.check_schema(schema)
    return Draft202012Validator(schema)


def repair_output_validator(repo_root: Path) -> Draft202012Validator:
    schema_dir = repo_root / "schemas"
    output_schema = load_json(schema_dir / "repair_output.schema.json")
    action_schema = load_json(schema_dir / "repair_action.schema.json")
    store = {
        output_schema["$id"]: output_schema,
        action_schema["$id"]: action_schema,
        (schema_dir / "repair_output.schema.json").resolve().as_uri(): output_schema,
        (schema_dir / "repair_action.schema.json").resolve().as_uri(): action_schema,
    }
    resolver = RefResolver(
        base_uri=(schema_dir / "repair_output.schema.json").resolve().as_uri(),
        referrer=output_schema,
        store=store,
    )
    Draft202012Validator.check_schema(output_schema)
    Draft202012Validator.check_schema(action_schema)
    return Draft202012Validator(output_schema, resolver=resolver)


def format_schema_error(path: Path, error: ValidationError) -> str:
    location = ".".join(str(part) for part in error.absolute_path)
    if location:
        return f"{path}:{location}: {error.message}"
    return f"{path}: {error.message}"


def referenced_files(instance: dict[str, Any]) -> list[str]:
    refs: list[str] = []
    for key in ("base_flowsheet", "faulty_flowsheet", "problem_statement", "llm_input", "mock_llm_output"):
        value = instance.get(key)
        if isinstance(value, str):
            refs.append(value)
    observations = instance.get("observations")
    if isinstance(observations, dict):
        refs.extend(value for value in observations.values() if isinstance(value, str))
    run_artifacts = instance.get("run_artifacts")
    if isinstance(run_artifacts, dict):
        refs.extend(value for value in run_artifacts.values() if isinstance(value, str))
    return refs


def instance_ref(path: Path, ref: str) -> Path:
    return path.parent / ref


def validate_file_references(path: Path, instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    for ref in referenced_files(instance):
        if not instance_ref(path, ref).exists():
            errors.append(f"{path}: missing referenced file: {ref}")
    return errors


def validate_profile(path: Path, instance: dict[str, Any], profile: str) -> list[str]:
    if profile == "draft":
        return []

    errors: list[str] = []
    source = instance.get("source", {})
    repro = instance.get("reproducibility", {})

    if isinstance(source, dict):
        for key, value in source.items():
            if isinstance(value, str) and value in PLACEHOLDER_VALUES:
                errors.append(f"{path}: source.{key} must not be {value!r} in {profile} profile")

    if isinstance(repro, dict):
        for key in ("base_flowsheet_sha256", "faulty_flowsheet_sha256"):
            if repro.get(key) == "pending":
                errors.append(f"{path}: reproducibility.{key} must not be 'pending' in {profile} profile")
        for key in REPRO_VERSION_FIELDS:
            if repro.get(key) in PLACEHOLDER_VALUES:
                errors.append(f"{path}: reproducibility.{key} must not be {repro.get(key)!r} in {profile} profile")

    if profile in {"release", "pilot"} and "unfaulted_placeholder_until_fault_injection" in instance.get("leakage_flags", []):
        errors.append(f"{path}: {profile} profile forbids unfaulted placeholder seed files")

    if profile in {"release", "pilot"}:
        if not isinstance(instance.get("problem_statement"), str):
            errors.append(f"{path}: {profile} profile requires problem_statement")
        elif not instance_ref(path, instance["problem_statement"]).exists():
            errors.append(f"{path}: {profile} profile requires existing problem_statement file")
        if not isinstance(instance.get("llm_input"), str):
            errors.append(f"{path}: {profile} profile requires llm_input")
        elif not instance_ref(path, instance["llm_input"]).exists():
            errors.append(f"{path}: {profile} profile requires existing llm_input file")
        if not isinstance(instance.get("mock_llm_output"), str):
            errors.append(f"{path}: {profile} profile requires mock_llm_output")
        else:
            errors.extend(validate_mock_llm_output(path, instance, profile))
        errors.extend(validate_release_artifacts(path, instance, profile))
        errors.extend(validate_public_leakage(path, instance))

    return errors


def is_successful_run(run: Any) -> bool:
    return is_successful_dwsim_run(run)


def target_mole_fraction(run: Any, stream_tag: str, component: str) -> float | None:
    if not isinstance(run, dict):
        return None
    for stream in run.get("streams", []):
        if not isinstance(stream, dict) or stream.get("tag") != stream_tag:
            continue
        compounds = stream.get("compounds")
        if not isinstance(compounds, dict):
            return None
        component_metrics = compounds.get(component)
        if not isinstance(component_metrics, dict):
            return None
        value = component_metrics.get("mole_fraction")
        return float(value) if isinstance(value, (int, float)) else None
    return None


def target_metric_value(run: Any, target: dict[str, Any]) -> float | None:
    if not isinstance(run, dict):
        return None
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
            component_metrics = compounds.get(component)
            if not isinstance(component_metrics, dict):
                return None
            value = component_metrics.get(metric)
        else:
            value = stream.get(metric)
        return float(value) if isinstance(value, (int, float)) else None
    return None


def target_missed(value: Any, target: dict[str, Any]) -> bool:
    threshold = target.get("threshold")
    if not isinstance(value, (int, float)) or not isinstance(threshold, (int, float)):
        return False
    if target.get("direction") == "max":
        return value > threshold
    return value < threshold


def target_met(value: Any, target: dict[str, Any]) -> bool:
    threshold = target.get("threshold")
    if not isinstance(value, (int, float)) or not isinstance(threshold, (int, float)):
        return False
    if target.get("direction") == "max":
        return value <= threshold
    return value >= threshold


def target_from_instance_or_metrics(instance: dict[str, Any], metrics: dict[str, Any]) -> dict[str, Any]:
    success = instance.get("success_criteria")
    metrics_target = metrics.get("target")
    if not isinstance(success, dict):
        success = {}
    if not isinstance(metrics_target, dict):
        metrics_target = {}
    target_metric = success.get("target_metric")
    if not isinstance(target_metric, dict):
        target_metric = metrics_target if isinstance(metrics_target.get("threshold"), (int, float)) else {}
    if isinstance(target_metric, dict) and target_metric:
        direction = target_metric.get("direction") or "min"
        threshold = target_metric.get("threshold")
        if threshold is None:
            threshold = target_metric.get("max") if direction == "max" else target_metric.get("min")
        return {
            "family": target_metric.get("family"),
            "stream_tag": target_metric.get("stream_tag") or target_metric.get("stream"),
            "stream_id": target_metric.get("stream_id"),
            "stream_role": target_metric.get("stream_role"),
            "component": target_metric.get("component"),
            "metric": target_metric.get("metric") or "mole_fraction",
            "direction": direction,
            "threshold": threshold,
            "product_mole_fraction_min": target_metric.get("product_mole_fraction_min")
            or (threshold if direction == "min" and target_metric.get("metric", "mole_fraction") == "mole_fraction" else None),
        }
    return {
        "family": metrics_target.get("family"),
        "stream_tag": success.get("target_stream_tag") or metrics_target.get("stream_tag"),
        "stream_id": metrics_target.get("stream_id"),
        "stream_role": metrics_target.get("stream_role"),
        "component": success.get("target_component") or metrics_target.get("component"),
        "metric": "mole_fraction",
        "direction": "min",
        "threshold": success.get("product_mole_fraction_min")
        or metrics_target.get("product_mole_fraction_min"),
        "product_mole_fraction_min": success.get("product_mole_fraction_min")
        or metrics_target.get("product_mole_fraction_min"),
    }


def summary_target_value(summary: Any) -> Any:
    if not isinstance(summary, dict):
        return None
    if isinstance(summary.get("target_value"), (int, float)):
        return summary.get("target_value")
    return summary.get("target_mole_fraction")


def validate_gold_proximity(path: Path, metrics: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    proximity = metrics.get("gold_proximity")
    if not isinstance(proximity, dict):
        return [f"{path}: release profile requires metrics_report.gold_proximity"]
    for key in ("target_match", "parameter_match", "unit_match"):
        if not isinstance(proximity.get(key), bool):
            errors.append(f"{path}: metrics_report.gold_proximity.{key} must be boolean")
    for key in ("value_abs_error", "value_rel_error"):
        if not isinstance(proximity.get(key), (int, float)):
            errors.append(f"{path}: metrics_report.gold_proximity.{key} must be numeric")
    return errors


def terminal_stream_tags(run: dict[str, Any]) -> set[str]:
    tags: set[str] = set()
    for stream in run.get("terminal_material_streams", []):
        if not isinstance(stream, dict):
            continue
        for key in ("tag", "id"):
            value = stream.get(key)
            if isinstance(value, str) and value:
                tags.add(value)
    return tags


def validate_release_artifacts(path: Path, instance: dict[str, Any], profile: str = "release") -> list[str]:
    errors: list[str] = []
    run_artifacts = instance.get("run_artifacts")
    if not isinstance(run_artifacts, dict):
        return [f"{path}: release profile requires run_artifacts"]

    required = ("base_run", "faulty_run", "repaired_run", "metrics_report")
    for key in required:
        if not isinstance(run_artifacts.get(key), str):
            errors.append(f"{path}: release profile requires run_artifacts.{key}")
    if errors:
        return errors

    base_hash = instance.get("reproducibility", {}).get("base_flowsheet_sha256")
    faulty_hash = instance.get("reproducibility", {}).get("faulty_flowsheet_sha256")
    if isinstance(base_hash, str) and isinstance(faulty_hash, str) and base_hash == faulty_hash:
        errors.append(f"{path}: release profile requires different base and faulty checksums")

    try:
        base_run = load_json(instance_ref(path, run_artifacts["base_run"]))
        faulty_run = load_json(instance_ref(path, run_artifacts["faulty_run"]))
        repaired_run = load_json(instance_ref(path, run_artifacts["repaired_run"]))
        metrics = load_json(instance_ref(path, run_artifacts["metrics_report"]))
    except Exception as exc:  # noqa: BLE001
        return [f"{path}: failed to load release run artifact JSON: {exc}"]

    if not is_successful_run(base_run):
        errors.append(f"{path}: release profile requires a successful base_run")
    if not is_successful_run(faulty_run):
        errors.append(f"{path}: release profile requires a successful faulty_run")
    if not is_successful_run(repaired_run):
        errors.append(f"{path}: release profile requires a successful repaired_run")

    if not isinstance(metrics, dict) or metrics.get("repairable") is not True:
        errors.append(f"{path}: release profile requires metrics_report.repairable=true")
        return errors
    errors.extend(validate_gold_proximity(path, metrics))

    target = target_from_instance_or_metrics(instance, metrics)
    faulty_summary = metrics.get("faulty", {})
    repaired_summary = metrics.get("repaired", {})
    threshold = target.get("threshold")
    faulty_value = summary_target_value(faulty_summary)
    repaired_value = summary_target_value(repaired_summary)
    stream_tag = target.get("stream_tag")
    metric = target.get("metric")
    if not isinstance(stream_tag, str) or not isinstance(metric, str):
        errors.append(f"{path}: release profile requires target stream/metric for run artifact checks")
    if profile == "pilot" and isinstance(target.get("family"), str) and target["family"].startswith("terminal_"):
        terminals = terminal_stream_tags(base_run)
        if stream_tag not in terminals and target.get("stream_id") not in terminals:
            errors.append(f"{path}: pilot profile requires terminal target stream {stream_tag!r} in base_run.terminal_material_streams")
    faulty_run_value = target_metric_value(faulty_run, target)
    repaired_run_value = target_metric_value(repaired_run, target)
    if is_successful_run(faulty_run):
        if not isinstance(threshold, (int, float)) or not isinstance(faulty_value, (int, float)):
            errors.append(f"{path}: release profile requires numeric faulty target metric")
        elif not target_missed(faulty_value, target):
            errors.append(f"{path}: release profile requires faulty_run to miss the selected target")
        if not isinstance(threshold, (int, float)) or faulty_run_value is None:
            errors.append(f"{path}: release profile requires numeric faulty target metric in faulty_run")
        elif not target_missed(faulty_run_value, target):
            errors.append(f"{path}: release profile requires faulty_run artifact to miss the selected target")
    if not isinstance(threshold, (int, float)) or not isinstance(repaired_value, (int, float)):
        errors.append(f"{path}: release profile requires numeric repaired target metric")
    elif not target_met(repaired_value, target):
        errors.append(f"{path}: release profile requires repaired_run to satisfy the selected target")
    if not isinstance(threshold, (int, float)) or repaired_run_value is None:
        errors.append(f"{path}: release profile requires numeric repaired target metric in repaired_run")
    elif not target_met(repaired_run_value, target):
        errors.append(f"{path}: release profile requires repaired_run artifact to satisfy the selected target")

    return errors


def supported_parameters_for_profile(profile: str) -> set[tuple[str, str]]:
    return PILOT_SUPPORTED_PARAMETERS if profile == "pilot" else RELEASE_SUPPORTED_PARAMETERS


def validate_mock_llm_output(path: Path, instance: dict[str, Any], profile: str) -> list[str]:
    errors: list[str] = []
    mock_path = instance.get("mock_llm_output")
    if not isinstance(mock_path, str):
        return []
    if Path(mock_path).parts and Path(mock_path).parts[0] == "public":
        errors.append(f"{path}: release profile requires mock_llm_output outside public/")
    try:
        mock = load_json(instance_ref(path, mock_path))
    except Exception as exc:  # noqa: BLE001
        return [f"{path}: failed to load mock_llm_output JSON: {exc}"]
    if not isinstance(mock, dict):
        return [f"{path}: mock_llm_output must be a JSON object"]

    output_validator = repair_output_validator(Path.cwd())
    output_errors = sorted(output_validator.iter_errors(mock), key=lambda error: list(error.absolute_path))
    for error in output_errors:
        location = ".".join(str(part) for part in error.absolute_path)
        prefix = "mock_llm_output"
        if location:
            prefix = f"{prefix}.{location}"
        errors.append(f"{path}:{prefix}: {error.message}")

    if errors:
        return errors

    repair_actions = mock.get("repair_actions")
    if not isinstance(repair_actions, list) or not repair_actions:
        return [f"{path}: mock_llm_output.repair_actions must be a non-empty array"]
    mock_action = repair_actions[0]
    gold_actions = instance.get("gold_repair_actions")
    if not isinstance(gold_actions, list) or not gold_actions:
        return [f"{path}: release profile requires gold_repair_actions for mock output comparison"]
    gold_action = gold_actions[0]
    if not isinstance(gold_action, dict):
        return [f"{path}: gold_repair_actions[0] must be an object"]

    errors.extend(validate_release_action(path, mock_action, "mock_llm_output.repair_actions[0]", profile))
    errors.extend(validate_release_action(path, gold_action, "gold_repair_actions[0]", profile))
    errors.extend(compare_repair_actions(path, mock_action, gold_action, "mock_llm_output.repair_actions[0]", "gold_repair_actions[0]"))

    run_artifacts = instance.get("run_artifacts")
    if isinstance(run_artifacts, dict) and isinstance(run_artifacts.get("metrics_report"), str):
        try:
            metrics = load_json(instance_ref(path, run_artifacts["metrics_report"]))
        except Exception as exc:  # noqa: BLE001
            return [f"{path}: failed to load metrics_report for mock output comparison: {exc}"]
        metrics_action = metrics.get("gold_repair_action") if isinstance(metrics, dict) else None
        if isinstance(metrics_action, dict):
            errors.extend(validate_repair_action_schema(path, metrics_action, "metrics_report.gold_repair_action"))
            errors.extend(validate_release_action(path, metrics_action, "metrics_report.gold_repair_action", profile))
            errors.extend(compare_repair_actions(path, mock_action, metrics_action, "mock_llm_output.repair_actions[0]", "metrics_report.gold_repair_action"))
        else:
            errors.append(f"{path}: metrics_report.gold_repair_action must be an object")
        repaired_value = repaired_metric_value_for_action(metrics, mock_action) if isinstance(metrics, dict) else None
        if is_supported_action(mock_action, profile):
            mock_value = mock_action.get("value")
            if not numeric_close(mock_value, repaired_value):
                errors.append(
                    f"{path}: mock_llm_output.repair_actions[0].value must match metrics_report.repaired parameter value"
                )

    return errors


def action_parameter_key(action: dict[str, Any]) -> tuple[str, str] | None:
    parameter = action.get("parameter")
    if action.get("type") != "set_unit_parameter" or not isinstance(parameter, dict):
        return None
    namespace = parameter.get("namespace")
    name = parameter.get("name")
    if not isinstance(namespace, str) or not isinstance(name, str):
        return None
    return namespace, name


def is_supported_action(action: dict[str, Any], profile: str) -> bool:
    return action_parameter_key(action) in supported_parameters_for_profile(profile)


def repaired_metric_value_for_action(metrics: dict[str, Any], action: dict[str, Any]) -> Any:
    repaired = metrics.get("repaired")
    if not isinstance(repaired, dict):
        return None
    parameter = action_parameter_key(action)
    if parameter == ("column_specification", "reflux_ratio"):
        return repaired.get("reflux_ratio")
    if parameter == ("column_configuration", "feed_stage"):
        return repaired.get("feed_stage")
    if parameter == ("pressure_specification", "outlet_pressure"):
        return repaired.get("outlet_pressure")
    if parameter == ("thermal_specification", "outlet_temperature"):
        return repaired.get("outlet_temperature")
    if parameter == ("separator_specification", "pressure"):
        return repaired.get("separator_pressure")
    if parameter == ("separator_specification", "temperature"):
        return repaired.get("separator_temperature")
    return None


def validate_release_action(path: Path, action: dict[str, Any], action_name: str, profile: str = "release") -> list[str]:
    errors: list[str] = []
    parameter = action_parameter_key(action)
    if parameter not in supported_parameters_for_profile(profile):
        errors.append(
            f"{path}: {action_name} must be a {profile}-supported set_unit_parameter action"
        )
    target = action.get("target")
    if not isinstance(target, dict) or target.get("kind") != "unit_operation":
        errors.append(f"{path}: {action_name}.target.kind must be 'unit_operation' in release profile")
    if parameter == ("column_specification", "reflux_ratio"):
        if not isinstance(action.get("value"), (int, float)):
            errors.append(f"{path}: {action_name}.value must be numeric")
        if action.get("unit") is not None:
            errors.append(f"{path}: {action_name}.unit must be null for column_specification/reflux_ratio")
    elif parameter == ("column_configuration", "feed_stage"):
        value = action.get("value")
        if isinstance(value, bool) or not isinstance(value, int):
            errors.append(f"{path}: {action_name}.value must be an integer for column_configuration/feed_stage")
        elif value < 1:
            errors.append(f"{path}: {action_name}.value must be >= 1 for column_configuration/feed_stage")
        if action.get("unit") is not None:
            errors.append(f"{path}: {action_name}.unit must be null for column_configuration/feed_stage")
    elif parameter == ("pressure_specification", "outlet_pressure"):
        value = action.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
            errors.append(f"{path}: {action_name}.value must be positive numeric for pressure_specification/outlet_pressure")
        try:
            validate_unit_for_entry(entry_for_parameter(parameter), action.get("unit"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {action_name}.{exc}")
    elif parameter == ("thermal_specification", "outlet_temperature"):
        value = action.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
            errors.append(f"{path}: {action_name}.value must be positive numeric for thermal_specification/outlet_temperature")
        try:
            validate_unit_for_entry(entry_for_parameter(parameter), action.get("unit"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {action_name}.{exc}")
    elif parameter == ("separator_specification", "pressure"):
        value = action.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
            errors.append(f"{path}: {action_name}.value must be positive numeric for separator_specification/pressure")
        try:
            validate_unit_for_entry(entry_for_parameter(parameter), action.get("unit"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {action_name}.{exc}")
    elif parameter == ("separator_specification", "temperature"):
        value = action.get("value")
        if not isinstance(value, (int, float)) or isinstance(value, bool) or float(value) <= 0:
            errors.append(f"{path}: {action_name}.value must be positive numeric for separator_specification/temperature")
        try:
            validate_unit_for_entry(entry_for_parameter(parameter), action.get("unit"))
        except Exception as exc:  # noqa: BLE001
            errors.append(f"{path}: {action_name}.{exc}")
    return errors


def validate_repair_action_schema(path: Path, action: dict[str, Any], action_name: str) -> list[str]:
    errors: list[str] = []
    validator = repair_action_validator(Path.cwd())
    for error in sorted(validator.iter_errors(action), key=lambda error: list(error.absolute_path)):
        location = ".".join(str(part) for part in error.absolute_path)
        prefix = action_name
        if location:
            prefix = f"{prefix}.{location}"
        errors.append(f"{path}:{prefix}: {error.message}")
    return errors


def compare_repair_actions(
    path: Path,
    actual: dict[str, Any],
    expected: dict[str, Any],
    actual_name: str,
    expected_name: str,
) -> list[str]:
    errors: list[str] = []
    if actual.get("type") != expected.get("type"):
        errors.append(f"{path}: {actual_name}.type must match {expected_name}.type")

    actual_target = actual.get("target", {})
    expected_target = expected.get("target", {})
    if not isinstance(actual_target, dict) or not isinstance(expected_target, dict):
        errors.append(f"{path}: {actual_name}.target and {expected_name}.target must be objects")
    else:
        for key in ("kind", "guid", "tag"):
            expected_value = expected_target.get(key)
            if expected_value is not None and actual_target.get(key) != expected_value:
                errors.append(f"{path}: {actual_name}.target.{key} must match {expected_name}.target.{key}")

    actual_parameter = actual.get("parameter", {})
    expected_parameter = expected.get("parameter", {})
    if not isinstance(actual_parameter, dict) or not isinstance(expected_parameter, dict):
        errors.append(f"{path}: {actual_name}.parameter and {expected_name}.parameter must be objects")
    else:
        for key in ("namespace", "name"):
            expected_value = expected_parameter.get(key)
            if expected_value is not None and actual_parameter.get(key) != expected_value:
                errors.append(f"{path}: {actual_name}.parameter.{key} must match {expected_name}.parameter.{key}")

    if actual.get("unit") != expected.get("unit"):
        errors.append(f"{path}: {actual_name}.unit must match {expected_name}.unit")

    if "value" in expected and not numeric_close(actual.get("value"), expected.get("value")):
        errors.append(f"{path}: {actual_name}.value must match {expected_name}.value")

    return errors


def numeric_close(actual: Any, expected: Any) -> bool:
    if not isinstance(actual, (int, float)) or not isinstance(expected, (int, float)):
        return actual == expected
    return math.isclose(float(actual), float(expected), rel_tol=1e-9, abs_tol=1e-9)


def number_tokens(value: Any) -> set[str]:
    # Small integer repair values such as feed stage 3 appear naturally in
    # public topology/parameter context. Release leakage checks catch these via
    # direct-repair text and structured hidden labels rather than raw token scan.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        return set()
    if isinstance(value, int):
        return set()
    as_float = float(value)
    if as_float.is_integer():
        return set()
    return {
        json.dumps(value),
        repr(as_float),
        format(as_float, ".15g"),
        format(as_float, ".16g"),
        format(as_float, ".17g"),
    }


def leakage_text(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".dwxmz":
        chunks: list[str] = [path.name]
        try:
            with zipfile.ZipFile(path) as archive:
                chunks.extend(archive.namelist())
                for name in archive.namelist():
                    if Path(name).suffix.lower() in {".xml", ".json", ".txt", ".csv", ".md"}:
                        chunks.append(archive.read(name).decode("utf-8", errors="ignore"))
        except Exception as exc:  # noqa: BLE001
            chunks.append(f"<failed to inspect archive: {exc}>")
        return "\n".join(chunks)
    if suffix in {".dwxml", ".json", ".txt", ".csv", ".md", ".xml"}:
        return path.name + "\n" + path.read_text(encoding="utf-8-sig", errors="ignore")
    return path.name + "\n" + path.read_bytes().decode("utf-8", errors="ignore")


def public_files(instance_path: Path) -> list[Path]:
    public_dir = instance_path.parent / "public"
    if not public_dir.exists():
        return []
    return sorted(path for path in public_dir.rglob("*") if path.is_file())


def forbidden_leakage_patterns(path: Path, instance: dict[str, Any]) -> set[str]:
    patterns = {
        "hidden/",
        "hidden\\",
        "mock_llm_output",
        "change_reflux_ratio",
        "change_feed_stage",
        "restore_reflux_ratio",
        "move_feed_stage_to_gold",
        "fault_reflux_ratio",
        "fault_feed_stage",
    }
    fault_type = instance.get("fault_type")
    if isinstance(fault_type, str) and fault_type:
        patterns.add(fault_type)

    gold_actions = instance.get("gold_repair_actions")
    if isinstance(gold_actions, list):
        for action in gold_actions:
            if isinstance(action, dict):
                if action_parameter_key(action) not in {
                    ("column_configuration", "feed_stage"),
                    ("pressure_specification", "outlet_pressure"),
                    ("thermal_specification", "outlet_temperature"),
                    ("separator_specification", "pressure"),
                    ("separator_specification", "temperature"),
                }:
                    patterns.update(number_tokens(action.get("value")))

    run_artifacts = instance.get("run_artifacts")
    if isinstance(run_artifacts, dict) and isinstance(run_artifacts.get("metrics_report"), str):
        try:
            metrics = load_json(instance_ref(path, run_artifacts["metrics_report"]))
        except Exception:  # noqa: BLE001
            metrics = None
        if isinstance(metrics, dict):
            target = metrics.get("target") if isinstance(metrics.get("target"), dict) else {}
            terminal_target = isinstance(target.get("family"), str) and target["family"].startswith("terminal_")
            base = metrics.get("base")
            if isinstance(base, dict):
                for key, value in base.items():
                    if terminal_target and key in {
                        "target_value",
                        "target_mole_fraction",
                        "outlet_pressure",
                        "outlet_temperature",
                        "separator_pressure",
                        "separator_temperature",
                    }:
                        continue
                    patterns.update(number_tokens(value))
            metrics_action = metrics.get("gold_repair_action")
            if isinstance(metrics_action, dict):
                if action_parameter_key(metrics_action) not in {
                    ("column_configuration", "feed_stage"),
                    ("pressure_specification", "outlet_pressure"),
                    ("thermal_specification", "outlet_temperature"),
                    ("separator_specification", "pressure"),
                    ("separator_specification", "temperature"),
                }:
                    patterns.update(number_tokens(metrics_action.get("value")))

    return {pattern for pattern in patterns if pattern}


def validate_public_leakage(path: Path, instance: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    patterns = forbidden_leakage_patterns(path, instance)
    for public_file in public_files(path):
        relative = public_file.relative_to(path.parent).as_posix()
        haystack = relative + "\n" + leakage_text(public_file)
        lowered = haystack.lower()
        for pattern in sorted(patterns):
            if pattern.lower() in lowered:
                errors.append(f"{path}: public leakage forbidden pattern {pattern!r} in {relative}")
    return errors


def validate_instance(
    path: Path,
    validator: Draft202012Validator,
    require_files: bool,
    profile: str,
) -> list[str]:
    errors: list[str] = []
    try:
        data = load_json(path)
    except ValueError as exc:
        return [f"{path}: {exc}"]

    schema_errors = sorted(validator.iter_errors(data), key=lambda error: list(error.absolute_path))
    errors.extend(format_schema_error(path, error) for error in schema_errors)

    if not isinstance(data, dict):
        return errors

    errors.extend(validate_profile(path, data, profile))
    if require_files:
        errors.extend(validate_file_references(path, data))

    return errors


def collect_instance_files(paths: list[str]) -> list[Path]:
    files: list[Path] = []
    for raw in paths:
        path = Path(raw)
        if path.is_dir():
            files.extend(sorted(path.rglob("instance.json")))
        else:
            files.append(path)
    return files


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("paths", nargs="*", default=["instances/seed"])
    parser.add_argument("--require-files", action="store_true")
    parser.add_argument("--profile", choices=["draft", "seed", "release", "pilot"], default="draft")
    args = parser.parse_args()

    repo_root = Path.cwd()
    validator = schema_validator(repo_root)
    files = collect_instance_files(args.paths)

    all_errors: list[str] = []
    for file_path in files:
        all_errors.extend(validate_instance(file_path, validator, args.require_files, args.profile))

    if all_errors:
        for error in all_errors:
            print(f"ERROR: {error}")
        return 1

    print(f"OK: validated {len(files)} instance file(s) with profile={args.profile}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
