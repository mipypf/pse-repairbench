# v0.1.5 Terminal Native Units Balanced Gemini Pilot

Date: 2026-06-02

This note records the target-family-balanced rerun of the v0.1.5 terminal
native-unit pilot. The balanced set was selected from the existing accepted
candidate pool without rerunning source-level sensitivity discovery.

## Run Configuration

- Model: `gemini-2.5-flash`
- Prompt mode: `parameter-selection`
- Dataset: generated balanced terminal native-unit pilot under
  `.tmp/generated_terminal_native_units_balanced`
- Instance count: 19
- Discovery reuse root: `.tmp/pilot_discovery_terminal_native_units_30`
- Output location: raw model outputs and evaluator reports were written under
  `.tmp/live_runs/gemini_terminal_native_units_balanced` and are intentionally
  untracked
- API mode: live network/API run
- Primary metric: executable target success
- Secondary diagnostics: gold proximity and failure taxonomy

## Selection Result

- Source count from original discovery: 39
- Discovery-success sources: 17
- Source errors: 22
- Accepted candidate pool: 129
- Selected instances: 19
- Built instances: 19
- Build errors: 0

Parameter distribution:

- `column_specification/reflux_ratio`: 4
- `column_configuration/feed_stage`: 3
- `pressure_specification/outlet_pressure`: 12

Target metric family distribution:

- `terminal_composition`: 6
- `terminal_flow`: 5
- `terminal_pressure`: 4
- `terminal_temperature`: 4

Source category distribution:

- `distillation`: 4
- `flash_separator`: 2
- `other_candidate`: 6
- `reaction_recycle`: 7

## Validation Result

- Pilot validation: 19/19
- Hidden-mock executable target success: 19/19
- Parameter-selection dry-run sanitize: 19/19

## Gemini Result

- Pipeline success: 19/19
- Executable target success: 11/19
- Executable failures:
  - `wrong_parameter`: 3
  - `right_parameter_wrong_value`: 5
- `wrong_parameter_success_count`: 0
- `exec_success_with_gold_mismatch_count`: 10

Gold proximity diagnostics:

- `gold_exact`: 1
- `right_parameter_different_value`: 15
- `wrong_parameter`: 3

Successful gold mismatch diagnostics:

- `gold_exact`: 1
- `right_parameter_different_value_success`: 10

## Interpretation

The balanced selector removed the earlier terminal-temperature dominance while
preserving a 19-instance executable pilot set. The Gemini executable success
rate dropped slightly from the score-selected set, but the qualitative pattern
remained: pipeline execution is robust, most successful repairs are not exact
gold matches, and wrong-parameter successes did not occur in this run.
