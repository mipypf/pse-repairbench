# v0.1.5 Terminal Native Units 40-Instance Gemini Flash-Lite Run

Date: 2026-06-03

This note records a single live Gemini Flash-Lite run on the clean 40-instance
terminal native-unit pilot set. The run is a pre-separator-expansion baseline.

## Dataset

- Dataset: generated clean terminal native-unit pilot
- Instance root: `.tmp/generated_terminal_native_units_40_clean`
- Instance count: 40
- Prompt mode: `parameter-selection`
- Primary metric: executable target success
- Hidden-mock check: 40/40 executable success before live model execution

Target metric family distribution:

- `terminal_composition`: 10
- `terminal_flow`: 10
- `terminal_pressure`: 8
- `terminal_temperature`: 12

Repair family distribution:

- `column_configuration/feed_stage`: 3
- `column_specification/reflux_ratio`: 6
- `pressure_specification/outlet_pressure`: 16
- `thermal_specification/outlet_temperature`: 15

## Run Config

```json
{
  "provider": "gemini",
  "model": "gemini-3.1-flash-lite",
  "prompt_mode": "parameter-selection",
  "temperature": null,
  "thinking": "provider_default",
  "structured_output": true
}
```

## Aggregate Results

- Pipeline success: 40/40
- Executable success: 19/40
- Executable success with gold mismatch: 19
- Wrong-parameter success: 0

Executable failure taxonomy:

- `right_parameter_wrong_value`: 17
- `wrong_parameter`: 3
- `wrong_target`: 1

Gold proximity diagnostics:

- `right_parameter_different_value`: 36
- `wrong_parameter`: 3
- `wrong_target`: 1

## Breakdown

By target family:

| target family | executable success |
| --- | ---: |
| `terminal_composition` | 4/10 |
| `terminal_flow` | 3/10 |
| `terminal_pressure` | 6/8 |
| `terminal_temperature` | 6/12 |

By repair family:

| repair family | executable success |
| --- | ---: |
| `column_configuration/feed_stage` | 0/3 |
| `column_specification/reflux_ratio` | 2/6 |
| `pressure_specification/outlet_pressure` | 9/16 |
| `thermal_specification/outlet_temperature` | 8/15 |

## Output Location

- `.tmp/live_runs/gemini_terminal_native_units_40_clean_flash_lite/aggregate.json`
- `.tmp/live_runs/gemini_terminal_native_units_40_clean_flash_lite/aggregate.csv`

Raw model outputs and evaluator reports remain untracked under `.tmp`.

## Interpretation

The infrastructure remained stable: every model output passed schema,
executor, and DWSIM pipeline stages. The signal is therefore concentrated in
action-pair choice and numeric value quality.

Flash-Lite solved pressure and thermal repairs more often than column repairs.
All three feed-stage instances failed by selecting the wrong parameter, which
suggests feed-stage remains a hard diagnostic family under the current
target+parameter pair-selection prompt. Gold exact match is again too strict:
all executable successes used values different from the hidden gold while still
satisfying the terminal process target.
