# Native Unit Contract v0.1.5

## Summary

v0.1.5 keeps the v0.1 canonical action shape and expands the pilot scope from
distillation-only column parameters to native DWSIM unit-operation scalar
parameters. The release profile remains limited to the two column families.
The pilot profile accepts executor-backed provisional families.

## Registry

The shared source of truth is `scripts/repair_registry.py`. Prompt generation,
Gemini response schema construction, executor dispatch, discovery, validation,
and documentation should use the same registry entries.

| support level | target kind | parameter | native unit types | unit |
| --- | --- | --- | --- | --- |
| release-supported | `unit_operation` | `column_specification/reflux_ratio` | `DistillationColumn` | `null` |
| release-supported | `unit_operation` | `column_configuration/feed_stage` | `DistillationColumn` | `null` |
| pilot-supported | `unit_operation` | `pressure_specification/outlet_pressure` | `Valve`, `Pump`, `Compressor` with `CalcMode == OutletPressure` | `Pa` |
| pilot-supported | `unit_operation` | `thermal_specification/outlet_temperature` | `Heater`, `Cooler` with `CalcMode == OutletTemperature` | `K` |
| pilot-supported | `unit_operation` | `separator_specification/pressure` | `Vessel` with `OverrideP == true` | `Pa` |
| pilot-supported | `unit_operation` | `separator_specification/temperature` | `Vessel` with `OverrideT == true` | `K` |

Pressure XML fields are `OutletPressure` for Valve, `Pout` for Pump, and
`POut` for Compressor.
Thermal outlet-temperature XML field is `OutletTemperature`. Separator XML
fields are `FlashPressure` and `FlashTemperature`.

## Pair Selection

The CLI value remains `--prompt-mode parameter-selection`, but the task is now
allowed target-parameter pair selection. The prompt lists concrete repair
action pairs, for example:

- `VALV-01: pressure_specification/outlet_pressure`
- `P-01: pressure_specification/outlet_pressure`
- `SEP-01: separator_specification/pressure`
- `DC-01: column_specification/reflux_ratio`

The structured Gemini schema allows exactly one action from the listed target
GUID + parameter pairs. A selection benchmark instance should expose at least
two allowed pairs.

Selection-mode public artifacts must not expose the hidden gold parameter in
`public/parameters.json` as `target_parameter`, and `public/llm_input.md` must
be a pair-selection prompt rather than an oracle prompt.

## Target Metrics

v0.1.5 pilot discovery targets terminal material streams. New generated pilot
instances should use the `terminal_composition`, `terminal_flow`,
`terminal_temperature`, and `terminal_pressure` families defined in
`docs/design/target_metric_contract_v0_1_5.md`.

For compatibility, validators and evaluators continue to read legacy
`product_purity`, `impurity_max`, `product_flow`, and `stream_pressure`
targets from existing artifacts.

## Validation Profiles

- `release`: current strict column release seeds only.
- `pilot`: release families plus executor-backed pilot-supported families.

Pilot validation still requires canonical schema validity, public leakage
checks, successful base/faulty/repaired runs, target success, and gold proximity
fields.

Live-model failure taxonomy distinguishes `wrong_action_pair`, `wrong_target`,
and `wrong_parameter` so same-parameter wrong-unit pressure repairs do not look
like value-estimation failures.

## Boundaries

CapeOpenUO mutation, material-stream feed conditions, reactor families, topology
repair, and property-package repair are outside v0.1.5.
