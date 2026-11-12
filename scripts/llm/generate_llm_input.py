#!/usr/bin/env python3
"""Generate an LLM input packet from a benchmark instance's public artifacts."""

from __future__ import annotations

import argparse
import csv
import io
import json
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from repair_registry import (  # noqa: E402
    PROMPT_MODES,
    entries_for_profile,
    normalize_allowed_action_pair,
    pair_from_target_and_entry,
    parameter_key_text,
)

SUPPORTED_ACTION_TYPES = {"set_unit_parameter"}


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8-sig").strip()


def instance_ref(instance_path: Path, ref: str) -> Path:
    return instance_path.parent / ref


def target_from_instance(instance: dict[str, Any], parameters: dict[str, Any]) -> dict[str, Any]:
    success = instance.get("success_criteria", {})
    product_target = parameters.get("product_target", {}) if isinstance(parameters, dict) else {}
    parameter_target_metric = parameters.get("target_metric") if isinstance(parameters, dict) else None
    if not isinstance(success, dict):
        success = {}
    if not isinstance(product_target, dict):
        product_target = {}
    if not isinstance(parameter_target_metric, dict):
        parameter_target_metric = {}

    success_target_metric = success.get("target_metric")
    if isinstance(success_target_metric, dict):
        stream_tag = success_target_metric.get("stream_tag") or success_target_metric.get("stream")
        target = {
            "family": success_target_metric.get("family"),
            "stream_tag": stream_tag,
            "component": success_target_metric.get("component"),
            "metric": success_target_metric.get("metric"),
            "direction": success_target_metric.get("direction"),
            "threshold": success_target_metric.get("threshold")
            or success_target_metric.get("min")
            or success_target_metric.get("max"),
        }
    elif parameter_target_metric:
        stream_tag = parameter_target_metric.get("stream_tag") or parameter_target_metric.get("stream")
        target = {
            "family": parameter_target_metric.get("family"),
            "stream_tag": stream_tag,
            "component": parameter_target_metric.get("component"),
            "metric": parameter_target_metric.get("metric"),
            "direction": parameter_target_metric.get("direction"),
            "threshold": parameter_target_metric.get("threshold")
            or parameter_target_metric.get("min")
            or parameter_target_metric.get("max"),
        }
    else:
        target = {
            "stream_tag": success.get("target_stream_tag") or product_target.get("stream_tag"),
            "component": success.get("target_component") or product_target.get("component"),
            "metric": "mole_fraction",
            "direction": "min",
            "threshold": success.get("product_mole_fraction_min")
            or product_target.get("product_mole_fraction_min"),
            "family": "product_purity",
        }

    if not target.get("metric"):
        target["metric"] = "mole_fraction"
    if not target.get("direction"):
        target["direction"] = "max" if target.get("family") == "impurity_max" else "min"
    if target.get("family") == "product_purity" and target.get("metric") == "mole_fraction":
        target["product_mole_fraction_min"] = target["threshold"]
    missing = [key for key in ("stream_tag", "metric", "direction", "threshold") if target.get(key) is None]
    if missing:
        raise ValueError(f"missing target fields for llm_input: {', '.join(missing)}")
    return target


def action_type_from_instance(instance: dict[str, Any]) -> str:
    actions = instance.get("gold_repair_actions")
    if not isinstance(actions, list) or not actions or not isinstance(actions[0], dict):
        raise ValueError("instance must include gold_repair_actions[0] so the LLM input template can be selected")
    action_type = actions[0].get("type")
    if action_type not in SUPPORTED_ACTION_TYPES:
        raise ValueError(f"unsupported LLM input template action type: {action_type!r}")
    return str(action_type)


def target_parameter_from_instance(instance: dict[str, Any], parameters: dict[str, Any]) -> dict[str, str]:
    actions = instance.get("gold_repair_actions")
    if isinstance(actions, list) and actions and isinstance(actions[0], dict):
        parameter = actions[0].get("parameter")
        if isinstance(parameter, dict):
            namespace = parameter.get("namespace")
            name = parameter.get("name")
            if isinstance(namespace, str) and isinstance(name, str):
                return {"namespace": namespace, "name": name}

    parameter = parameters.get("target_parameter") if isinstance(parameters, dict) else None
    if isinstance(parameter, dict):
        namespace = parameter.get("namespace")
        name = parameter.get("name")
        if isinstance(namespace, str) and isinstance(name, str):
            return {"namespace": namespace, "name": name}

    raise ValueError("could not determine target repair parameter")


def csv_rows(text: str) -> list[dict[str, str]]:
    reader = csv.DictReader(io.StringIO(text))
    return list(reader)


def faulty_observed_value(stream_table_text: str, target: dict[str, Any]) -> str:
    component = target.get("component")
    if isinstance(component, str) and component:
        key = f"{component.lower()}_{target['metric']}"
    else:
        key = str(target["metric"])
    for row in csv_rows(stream_table_text):
        if row.get("stream_tag") == target["stream_tag"] and row.get(key):
            return row[key]
    return "not available in stream table"


def target_metric_label(target: dict[str, Any]) -> str:
    component = target.get("component")
    if isinstance(component, str) and component:
        return f"{component} {target['metric']}"
    return str(target["metric"])


def target_requirement_text(target: dict[str, Any]) -> str:
    comparator = "at least" if target["direction"] == "min" else "at most"
    return f"{target_metric_label(target)} {comparator} {float(target['threshold']):.12g}"


def compact_column_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    column = parameters.get("target_column") if isinstance(parameters, dict) else None
    if not isinstance(column, dict):
        return {}
    return {
        "guid": column.get("guid"),
        "tag": column.get("tag"),
        "type": column.get("type"),
        "reflux_ratio": column.get("reflux_ratio"),
        "feed_stage": column.get("feed_stage"),
        "feed_stage_name": column.get("feed_stage_name"),
        "feed_stream_id": column.get("feed_stream_id"),
        "number_of_stages": column.get("number_of_stages"),
        "condenser_duty": column.get("condenser_duty"),
        "reboiler_duty": column.get("reboiler_duty"),
        "specs": column.get("specs", []),
    }


def compact_target_unit_parameters(parameters: dict[str, Any]) -> dict[str, Any]:
    unit = parameters.get("target_unit") if isinstance(parameters, dict) else None
    if not isinstance(unit, dict):
        return {}
    return {
        "guid": unit.get("guid"),
        "tag": unit.get("tag"),
        "type": unit.get("type"),
        "calc_mode": unit.get("calc_mode"),
        "reflux_ratio": unit.get("reflux_ratio"),
        "feed_stage": unit.get("feed_stage"),
        "feed_stage_name": unit.get("feed_stage_name"),
        "feed_stream_id": unit.get("feed_stream_id"),
        "number_of_stages": unit.get("number_of_stages"),
        "outlet_pressure": unit.get("outlet_pressure"),
        "pout": unit.get("pout"),
        "p_out": unit.get("p_out"),
        "delta_p": unit.get("delta_p"),
        "outlet_temperature": unit.get("outlet_temperature"),
        "override_p": unit.get("override_p"),
        "override_t": unit.get("override_t"),
        "flash_pressure": unit.get("flash_pressure"),
        "flash_temperature": unit.get("flash_temperature"),
        "specs": unit.get("specs", []),
    }


def observed_candidate_units_from_parameters(
    parameters: dict[str, Any],
    allowed_pairs: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    raw_units = parameters.get("observed_candidate_units") if isinstance(parameters, dict) else None
    if isinstance(raw_units, list) and raw_units:
        units = [unit for unit in raw_units if isinstance(unit, dict)]
        allowed_guids = {
            pair["target"]["guid"]
            for pair in allowed_pairs
            if isinstance(pair.get("target"), dict) and isinstance(pair["target"].get("guid"), str)
        }
        observed_guids = {unit.get("guid") for unit in units if isinstance(unit.get("guid"), str)}
        missing = sorted(allowed_guids - observed_guids)
        if missing:
            raise ValueError(f"observed_candidate_units missing allowed target GUID(s): {', '.join(missing)}")
        return units

    fallback = compact_target_unit_parameters(parameters) or compact_column_parameters(parameters)
    return [fallback] if fallback else []


def target_guid(instance: dict[str, Any], parameters: dict[str, Any]) -> str:
    column = parameters.get("target_column") if isinstance(parameters, dict) else None
    if isinstance(column, dict) and isinstance(column.get("guid"), str):
        return column["guid"]
    actions = instance.get("gold_repair_actions")
    if isinstance(actions, list) and actions and isinstance(actions[0], dict):
        target = actions[0].get("target")
        if isinstance(target, dict) and isinstance(target.get("guid"), str):
            return target["guid"]
    raise ValueError("could not determine target column GUID")


def allowed_repair_actions_from_parameters(instance: dict[str, Any], parameters: dict[str, Any]) -> list[dict[str, Any]]:
    raw_allowed = parameters.get("allowed_repair_actions") if isinstance(parameters, dict) else None
    if isinstance(raw_allowed, list) and raw_allowed:
        return [normalize_allowed_action_pair(pair) for pair in raw_allowed if isinstance(pair, dict)]

    # Backward-compatible fallback for existing v0.1 generated artifacts. New
    # pilot instances should provide explicit target+parameter pairs.
    target = None
    column = parameters.get("target_column") if isinstance(parameters, dict) else None
    unit = parameters.get("target_unit") if isinstance(parameters, dict) else None
    if isinstance(unit, dict) and isinstance(unit.get("guid"), str):
        target = unit
    elif isinstance(column, dict) and isinstance(column.get("guid"), str):
        target = column
    if target is None:
        actions = instance.get("gold_repair_actions")
        if isinstance(actions, list) and actions and isinstance(actions[0], dict):
            target = actions[0].get("target")
    if not isinstance(target, dict) or not isinstance(target.get("guid"), str):
        raise ValueError("could not determine allowed repair action targets")
    return [pair_from_target_and_entry(target, entry) for entry in entries_for_profile("release")]


def demote_markdown_headings(text: str, levels: int = 2) -> str:
    prefix = "#" * levels
    lines: list[str] = []
    for line in text.splitlines():
        if line.startswith("#"):
            lines.append(f"{prefix}{line}")
        else:
            lines.append(line)
    return "\n".join(lines).strip()


def render_set_unit_parameter_packet(
    problem_text: str,
    target: dict[str, Any],
    observed_value: str,
    column_parameters: dict[str, Any],
    stream_table_text: str,
    simulator_log: str,
    guid: str,
) -> str:
    column_json = json.dumps(column_parameters, indent=2, sort_keys=True)
    task_text = demote_markdown_headings(problem_text)
    return f"""# LLM Input Packet: Distillation Reflux-Ratio Repair

## Task

{task_text}

## Target

- Target stream: `{target['stream_tag']}`
- Required target: `{target_requirement_text(target)}`
- Faulty observed target value: `{observed_value}`

## Faulty Column Parameters

```json
{column_json}
```

## Faulty Stream Table

```csv
{stream_table_text.strip()}
```

## Faulty Simulator Log

```text
{simulator_log.strip()}
```

## Required Output

Return one JSON object. The `repair_actions` array must contain a canonical `set_unit_parameter` action targeting the column GUID below. Choose the numeric reflux-ratio value you recommend.

```json
{{
  "diagnosis": "short diagnosis",
  "repair_actions": [
    {{
      "type": "set_unit_parameter",
      "target": {{
        "kind": "unit_operation",
        "guid": "{guid}"
      }},
      "parameter": {{
        "namespace": "column_specification",
        "name": "reflux_ratio"
      }},
      "value": 0.0,
      "unit": null,
      "rationale": "why this reflux ratio should restore the target"
    }}
  ],
  "rationale": "brief overall reasoning"
}}
```
"""


def render_feed_stage_packet(
    problem_text: str,
    target: dict[str, Any],
    observed_value: str,
    column_parameters: dict[str, Any],
    stream_table_text: str,
    simulator_log: str,
    guid: str,
) -> str:
    column_json = json.dumps(column_parameters, indent=2, sort_keys=True)
    task_text = demote_markdown_headings(problem_text)
    return f"""# LLM Input Packet: Distillation Feed-Stage Repair

## Task

{task_text}

## Target

- Target stream: `{target['stream_tag']}`
- Required target: `{target_requirement_text(target)}`
- Faulty observed target value: `{observed_value}`

## Faulty Column Parameters

```json
{column_json}
```

## Faulty Stream Table

```csv
{stream_table_text.strip()}
```

## Faulty Simulator Log

```text
{simulator_log.strip()}
```

## Required Output

Return one JSON object. The `repair_actions` array must contain a canonical `set_unit_parameter` action targeting the column GUID below. Choose the integer feed-stage value you recommend.

```json
{{
  "diagnosis": "short diagnosis",
  "repair_actions": [
    {{
      "type": "set_unit_parameter",
      "target": {{
        "kind": "unit_operation",
        "guid": "{guid}"
      }},
      "parameter": {{
        "namespace": "column_configuration",
        "name": "feed_stage"
      }},
      "value": 1,
      "unit": null,
      "rationale": "why this feed stage should restore the target"
    }}
  ],
  "rationale": "brief overall reasoning"
}}
```
"""


def render_pressure_outlet_packet(
    problem_text: str,
    target: dict[str, Any],
    observed_value: str,
    unit_parameters: dict[str, Any],
    stream_table_text: str,
    simulator_log: str,
    guid: str,
) -> str:
    unit_json = json.dumps(unit_parameters, indent=2, sort_keys=True)
    task_text = demote_markdown_headings(problem_text)
    return f"""# LLM Input Packet: Unit Outlet-Pressure Repair

## Task

{task_text}

## Target

- Target stream: `{target['stream_tag']}`
- Required target: `{target_requirement_text(target)}`
- Faulty observed target value: `{observed_value}`

## Faulty Target Unit Parameters

```json
{unit_json}
```

## Faulty Stream Table

```csv
{stream_table_text.strip()}
```

## Faulty Simulator Log

```text
{simulator_log.strip()}
```

## Required Output

Return one JSON object. The `repair_actions` array must contain a canonical `set_unit_parameter` action targeting the unit GUID below. Choose the outlet pressure in Pa you recommend.

```json
{{
  "diagnosis": "short diagnosis",
  "repair_actions": [
    {{
      "type": "set_unit_parameter",
      "target": {{
        "kind": "unit_operation",
        "guid": "{guid}"
      }},
      "parameter": {{
        "namespace": "pressure_specification",
        "name": "outlet_pressure"
      }},
      "value": 101325.0,
      "unit": "Pa",
      "rationale": "why this outlet pressure should restore the target"
    }}
  ],
  "rationale": "brief overall reasoning"
}}
```
"""


def allowed_repair_actions_text(allowed_pairs: list[dict[str, Any]]) -> str:
    return "\n".join(
        f"- `{pair['target'].get('tag') or pair['target']['guid']}` / GUID `{pair['target']['guid']}`: "
        f"`{parameter_key_text(pair['parameter'])}` (unit: `{ 'null' if pair['unit'] is None else pair['unit'] }`)"
        for pair in allowed_pairs
    )


def render_parameter_selection_packet(
    target: dict[str, Any],
    observed_value: str,
    candidate_units: list[dict[str, Any]],
    stream_table_text: str,
    simulator_log: str,
    allowed_pairs: list[dict[str, Any]],
    omit_simulator_log: bool = False,
) -> str:
    candidate_json = json.dumps(candidate_units, indent=2, sort_keys=True)
    simulator_log_section = "" if omit_simulator_log else f"""## Faulty Simulator Log

```text
{simulator_log.strip()}
```

"""
    return f"""# LLM Input Packet: Target-Parameter Pair Selection Repair

## Task

The DWSIM flowsheet runs headlessly, but the selected process stream misses its target.
Select exactly one allowed target-parameter pair to change, and propose a canonical repair action that restores the target after rerunning the flowsheet.

## Target

- Target stream: `{target['stream_tag']}`
- Required target: `{target_requirement_text(target)}`
- Faulty observed target value: `{observed_value}`

## Observed Candidate Unit Parameters

```json
{candidate_json}
```

## Faulty Stream Table

```csv
{stream_table_text.strip()}
```

{simulator_log_section}## Allowed Repair Actions

{allowed_repair_actions_text(allowed_pairs)}

Choose exactly one `set_unit_parameter` action.

## Required Output

Return one JSON object with exactly one canonical `set_unit_parameter` action. The action target GUID and parameter must match exactly one allowed repair action above.
"""


def generate(
    instance_path: Path,
    output_path: Path,
    prompt_mode: str = "oracle-parameter",
    omit_simulator_log: bool = False,
) -> None:
    if prompt_mode not in PROMPT_MODES:
        raise ValueError(f"unsupported prompt mode: {prompt_mode!r}")
    if omit_simulator_log and prompt_mode != "parameter-selection":
        raise ValueError("--omit-simulator-log requires --prompt-mode parameter-selection")
    instance = load_json(instance_path)
    if not isinstance(instance, dict):
        raise ValueError("instance file must contain a JSON object")

    observations = instance.get("observations")
    if not isinstance(observations, dict):
        raise ValueError("instance.observations must be an object")
    problem_ref = instance.get("problem_statement")
    if not isinstance(problem_ref, str):
        raise ValueError("instance.problem_statement is required")

    parameters_ref = observations.get("parameters")
    stream_table_ref = observations.get("stream_table")
    log_ref = observations.get("simulator_log")
    if not all(isinstance(ref, str) for ref in (parameters_ref, stream_table_ref, log_ref)):
        raise ValueError("instance observations must include parameters, stream_table, and simulator_log paths")

    parameters = load_json(instance_ref(instance_path, str(parameters_ref)))
    stream_table_text = read_text(instance_ref(instance_path, str(stream_table_ref)))
    simulator_log = read_text(instance_ref(instance_path, str(log_ref)))

    target = target_from_instance(instance, parameters)
    observed_value = faulty_observed_value(stream_table_text, target)
    column_parameters = compact_column_parameters(parameters)

    if prompt_mode == "parameter-selection":
        allowed_pairs = allowed_repair_actions_from_parameters(instance, parameters)
        if len(allowed_pairs) < 2:
            raise ValueError("parameter-selection mode requires at least two allowed target-parameter pairs")
        candidate_units = observed_candidate_units_from_parameters(parameters, allowed_pairs)
        if not candidate_units:
            raise ValueError("parameter-selection mode requires observed candidate unit summaries")
        output = render_parameter_selection_packet(
            target,
            observed_value,
            candidate_units,
            stream_table_text,
            simulator_log,
            allowed_pairs,
            omit_simulator_log=omit_simulator_log,
        )
    else:
        action_type = action_type_from_instance(instance)
        guid = target_guid(instance, parameters)
        problem_text = read_text(instance_ref(instance_path, problem_ref))
        target_parameter = target_parameter_from_instance(instance, parameters)

        if action_type == "set_unit_parameter" and target_parameter == {
            "namespace": "column_specification",
            "name": "reflux_ratio",
        }:
            output = render_set_unit_parameter_packet(
                problem_text,
                target,
                observed_value,
                column_parameters,
                stream_table_text,
                simulator_log,
                guid,
            )
        elif action_type == "set_unit_parameter" and target_parameter == {
            "namespace": "column_configuration",
            "name": "feed_stage",
        }:
            output = render_feed_stage_packet(
                problem_text,
                target,
                observed_value,
                column_parameters,
                stream_table_text,
                simulator_log,
                guid,
            )
        elif action_type == "set_unit_parameter" and target_parameter == {
            "namespace": "pressure_specification",
            "name": "outlet_pressure",
        }:
            target_parameters = compact_target_unit_parameters(parameters) or column_parameters
            output = render_pressure_outlet_packet(
                problem_text,
                target,
                observed_value,
                target_parameters,
                stream_table_text,
                simulator_log,
                guid,
            )
        else:  # pragma: no cover - guarded by action_type_from_instance
            raise ValueError(f"unsupported LLM input template parameter: {target_parameter!r}")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(output, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--instance", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--prompt-mode", choices=sorted(PROMPT_MODES), default="oracle-parameter")
    parser.add_argument(
        "--omit-simulator-log", action="store_true",
        help="Omit only the Faulty Simulator Log section (parameter-selection mode only).",
    )
    args = parser.parse_args()

    try:
        generate(
            args.instance, args.output, prompt_mode=args.prompt_mode,
            omit_simulator_log=args.omit_simulator_log,
        )
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    print(f"Wrote LLM input packet to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
