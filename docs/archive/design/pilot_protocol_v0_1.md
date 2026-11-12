# v0.1 Pilot Evaluation Protocol

## Summary

The v0.1 pilot is the pre-production benchmark used to stabilize dataset
generation and evaluation before final measurement. The v0.1 baseline remains
distillation-only; v0.1.5 adds a native-unit pilot layer for executor-backed
pressure, thermal, and separator scalar unit-parameter faults.

- simulator: DWSIM only;
- v0.1 release process category: distillation only;
- v0.1 release parameter families: `column_specification/reflux_ratio` and
  `column_configuration/feed_stage`;
- v0.1.5 pilot parameter families: `pressure_specification/outlet_pressure`
  for native Valve, Pump, and Compressor units with
  `CalcMode == OutletPressure`, `thermal_specification/outlet_temperature` for
  native Heater/Cooler units with `CalcMode == OutletTemperature`, and
  `separator_specification/pressure` / `separator_specification/temperature`
  for native Vessel units with pressure/temperature override enabled;
- new pilot target metric families: `terminal_composition`, `terminal_flow`,
  `terminal_temperature`, and `terminal_pressure`;
- problem wording: terminal stream recovery template only.

Prompt variants and new parameter families are not varied at the same time in
the pilot.

## Prompt Modes

- `oracle-parameter`: localized prompt condition. The prompt and Gemini response
  schema identify the parameter family to adjust.
- `parameter-selection`: diagnostic prompt condition. The CLI name is kept for
  compatibility, but the task is target-parameter pair selection. The prompt
  ignores `public/parameters.json` `target_parameter`, does not include the raw
  oracle-specific problem statement, and asks the model to choose exactly one
  allowed repair action pair, such as
  `DC-01: column_specification/reflux_ratio` or
  `COMP-01: pressure_specification/outlet_pressure`.

Selection benchmark instances must expose at least two allowed repair action
pairs. The Gemini response schema constrains the output to exactly one of those
target GUID + parameter pairs.

Generated parameter-selection public artifacts must not expose the hidden gold
parameter through `public/parameters.json` `target_parameter` or through an
oracle-style `public/llm_input.md`. Oracle prompts are a separate condition and
must be generated transiently or kept out of model-visible selection artifacts.
Final-oriented parameter-selection prompts must also avoid spotlighting one
suspect unit. They should show `Observed Candidate Unit Parameters` as a JSON
array covering every target unit present in `allowed_repair_actions`, with the
same compact fields for each unit. The old single-unit heading
`Faulty Target Unit Parameters` is oracle/localized wording and must not appear
in selection prompts.

## Generation Protocol

Pilot generation runs bulk sensitivity discovery over curated headless-success
DWSIM flowsheets, writes source-level reports, selects balanced accepted
candidates, and materializes generated instances under
`.tmp/generated_pilot_native_units`.

Selection is balanced by:

- source id;
- parameter family;
- target metric family.

Feasibility-guided source selection may use
`.tmp/native_unit_feasibility/feasibility_report.json` to scan only sources
with at least two executor-backed target+parameter pairs, then round-robin
across source categories before running DWSIM sensitivity discovery.

Tracked `instances/pilot/` artifacts are not written by default. Generated
instances should be promoted only after release validation, hidden-mock
evaluation, leakage review, and distribution review.

## Evaluation Fields

The standard aggregate fields for v0.1 pilot and later v0.1-final are:

- `target_value`
- `target_direction`
- `target_threshold`
- `executable_success`
- `target_match`
- `parameter_match`
- `unit_match`
- `value_abs_error`
- `value_rel_error`
- `gold_proximity_type`
- `gold_mismatch_success_type`
- `failure_type`

Primary metric is executable target success. Gold proximity is a diagnostic
secondary metric.

## Failure Taxonomy

Live-model pilot measurements use `failure_type` only for executable failures.
If `executable_success=true`, `failure_type` must be `null` even when the
repair action differs from hidden gold.

Failure buckets are:

- `model_output_failure`
- `schema_failure`
- `executor_failure`
- `dwsim_failure`
- `wrong_parameter`
- `wrong_target`
- `wrong_action_pair`
- `right_parameter_wrong_value`
- `target_failure`
- `pipeline_failure`

Invalid JSON and response-schema failures are counted under
`model_output_failure` unless an evaluator report exists and classifies the
failure more specifically.

For parameter-selection measurements, `wrong_action_pair` means both selected
target and selected parameter differ from hidden gold. `wrong_target` means the
parameter family matches but the target unit differs. `wrong_parameter` means
the target matches but the selected parameter does not match hidden gold.
`right_parameter_wrong_value` means the selected parameter matches hidden gold,
the pipeline completes, the target is missed, and the numeric value differs
from hidden gold.

Gold semantic differences are tracked separately through
`gold_proximity_type` and `gold_mismatch_success_type`. This keeps the primary
metric executable success separate from the secondary gold-proximity diagnostic.

Prompt-only dry runs use `dry_run_sanitize`; this is recorded in
`preflight_counts`, not in live-model `failure_counts`.

## Freeze Rule

After the pilot, freeze the evaluation protocol, leakage policy, failure
taxonomy, and aggregate fields before expanding the problem scope. The first
scope expansion should change either parameter family or problem wording, not
both in the same experiment.
