# v0.1.5 Terminal Native Units Gemini Pilot

Date: 2026-06-02

This note records the first terminal-material-stream v0.1.5 pilot run with
target+parameter pair selection. The run uses generated DWSIM native-unit
instances and evaluates the model by executable target success first, with
gold proximity as a secondary diagnostic.

## Run Configuration

- Model: `gemini-2.5-flash`
- Prompt mode: `parameter-selection`
- Dataset: generated terminal native-unit pilot under
  `.tmp/generated_terminal_native_units_30`
- Instance count: 19
- Output location: raw model outputs and evaluator reports were written under
  `.tmp/live_runs/gemini_terminal_native_units_30` and are intentionally
  untracked
- API mode: live network/API run
- Primary metric: executable target success
- Secondary diagnostics: gold proximity and failure taxonomy

## Dataset Distribution

- `column_specification/reflux_ratio`: 3
- `column_configuration/feed_stage`: 3
- `pressure_specification/outlet_pressure`: 13

Target metric families:

- `terminal_composition`: 2
- `terminal_flow`: 3
- `terminal_pressure`: 2
- `terminal_temperature`: 12

The set is useful as a first pilot, but `terminal_temperature` is overrepresented
and should be balanced before treating the set as a protocol baseline.

## Aggregate Result

- Pipeline success: 19/19
- Executable target success: 12/19
- Executable failures:
  - `wrong_parameter`: 3
  - `right_parameter_wrong_value`: 4
- `wrong_parameter_success_count`: 0
- `exec_success_with_gold_mismatch_count`: 10

Gold proximity diagnostics:

- `gold_exact`: 2
- `right_parameter_different_value`: 14
- `wrong_parameter`: 3

Successful gold mismatch diagnostics:

- `gold_exact`: 2
- `right_parameter_different_value_success`: 10

## Interpretation

Gold exact match is too strict as a primary benchmark metric for this setting.
Ten runs used values different from hidden gold but still met the terminal
process target after execution. This supports the v0.1.5 evaluation policy:
executable target success is the primary metric, while gold proximity remains a
diagnostic for repair semantics and value estimation.

The next dataset step is target-family-balanced selection from the accepted
candidate pool before increasing scope or adding more parameter families.
