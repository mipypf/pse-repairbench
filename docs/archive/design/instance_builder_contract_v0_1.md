# Instance Builder Contract v0.1

## Summary

The v0.1 instance builder turns a fixed fault spec into a release-style
benchmark instance. It does not search for faults or select target metrics.
Those exploratory workflows remain in the reference builders.

This layer is intentionally separated from sensitivity discovery:

- discovery chooses candidate fault values and target metrics;
- the fixed-spec builder materializes one already chosen fault spec;
- evaluator/validator decide whether the generated instance is executable and
  release-style.

The supported scope is the v0.1 release-supported executable semantic repair
surface plus v0.1.5 pilot-supported native-unit extensions:

- `unit_operation + column_specification/reflux_ratio`
- `unit_operation + column_configuration/feed_stage`
- pilot `unit_operation + pressure_specification/outlet_pressure`
- pilot `unit_operation + thermal_specification/outlet_temperature`
- pilot `unit_operation + separator_specification/pressure`
- pilot `unit_operation + separator_specification/temperature`

Generated artifacts default to `.tmp/generated_pilot_native_units/<instance_id>/`.
Tracked `instances/seed` artifacts must be updated only by an explicit caller
choice, not by the default builder path.

## Fault Spec Shape

```json
{
  "instance_id": "distillation_002_reflux_ratio_single",
  "source_flowsheet": "curated_data/dwsim_headless_successes/distillation/002_air_liquefaction_using_linde_single_column_system.zip",
  "source_name": "FOSSEE DWSIM Flowsheeting Project: Air Liquefaction using Linde Single Column System",
  "process_category": "distillation",
  "reasoning_class": "P_parameter",
  "fault_type": "column_reflux_ratio_error",
  "fault_severity": "medium",
  "fault": {
    "target": {
      "kind": "unit_operation",
      "guid": "DC-84eedf9c-acf3-4dfc-8675-2245dc73de75",
      "tag": "DC-01"
    },
    "parameter": {
      "namespace": "column_specification",
      "name": "reflux_ratio"
    },
    "fault_value": 0.01,
    "gold_value": 7.50199999999571,
    "unit": null
  },
  "target_metric": {
    "stream": "S-08",
    "property": "oxygen_mole_fraction",
    "min": 0.99
  },
  "public_problem": {
    "title": "Repair Task: Distillation Column Reflux Ratio",
    "body": "The DWSIM flowsheet runs headlessly, but the selected product stream misses its purity target..."
  }
}
```

`target_metric.property` currently supports `<component>_mole_fraction` only.
The builder normalizes this to the existing release `success_criteria` fields:
`target_stream_tag`, `target_component`, and `product_mole_fraction_min`.

The builder also accepts the generic discovery form. New v0.1.5 discovery
uses terminal target families:

```json
{
  "family": "terminal_pressure",
  "stream": "S-08",
  "stream_role": "terminal_material_stream",
  "metric": "pressure",
  "direction": "max",
  "threshold": 620000
}
```

For compatibility, product-purity mole-fraction specs may keep the legacy
`product_mole_fraction_min` fields in generated `success_criteria`. Generic
targets are represented under `success_criteria.target_metric`. Validators and
evaluators still read legacy `product_purity`, `impurity_max`, `product_flow`,
and `stream_pressure` families from older generated artifacts.

## Builder Behavior

The general builder must:

- extract or copy the source DWSIM flowsheet into `hidden/base.dwxmz`;
- resolve the target unit operation by GUID/tag;
- inject the configured scalar fault into `public/faulty.dwxmz`;
- write public topology, parameters, streams, log, problem, and LLM input;
- write hidden gold/mock output, base/faulty/repaired run artifacts, repaired
  flowsheet, and metrics report;
- apply the hidden mock output through the canonical executor;
- require base/faulty/repaired DWSIM runs to solve successfully;
- require the faulty run to miss the target and the repaired run to satisfy it;
- require exact gold proximity for the hidden mock output.

The builder does not perform candidate sweeps. Reference builders may keep
sweep logic for reproducibility and comparison.

## Reference Equivalence

For the two v0.1 baseline instances, the generated artifacts are compared to
the reference seed instances semantically rather than byte-for-byte. The
equivalence check covers:

- canonical gold action type, target, parameter, unit, and numeric value;
- success criteria;
- metrics target definition;
- repaired target metric;
- `gold_proximity` fields.

Exact `.dwxmz` zip hashes are not required to match because archive metadata
and XML serialization can vary without changing benchmark semantics.

## Allowed Repair Actions

Generated `public/parameters.json` may include `allowed_repair_actions`, a list
of model-visible target+parameter pairs for diagnostic `parameter-selection`
prompts. New pilot selection instances should expose at least two pairs. The
hidden gold action still defines the single correct repair.

Generated `public/parameters.json` for parameter-selection mode should also
include `observed_candidate_units`, a compact JSON array with one summary for
each unique target GUID in `allowed_repair_actions`. This keeps candidate units
at a uniform observation granularity instead of exposing one hidden faulty unit.
The summary may include GUID, tag, DWSIM type, supported parameter keys,
calculation mode, column configuration/specification fields, outlet
pressure/temperature fields, and separator override/flash pressure/temperature
fields.

For parameter-selection artifacts, `public/parameters.json` must not include
`target_parameter`, and `public/llm_input.md` must use the pair-selection prompt
rather than an oracle-parameter prompt. Oracle prompt generation is a separate
condition and should not leak the gold parameter into model-visible selection
artifacts.

## Boundaries

The v0.1.5 general builder does not support `material_stream`, reactor
families, CapeOpenUO mutation, property-package repair, topology repair, or
automatic source curation. Those remain future builder extensions after the
native-unit pilot is stable.
