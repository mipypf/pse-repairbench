# v0.1.5 Terminal Native Units Multi-Model Comparison

Date: 2026-06-02

This note records the first multi-model comparison on the balanced v0.1.5
terminal native-unit pilot set.

## Dataset

- Dataset: generated balanced terminal native-unit pilot
- Instance root: `.tmp/generated_terminal_native_units_balanced`
- Instance count: 19
- Prompt mode: `parameter-selection`
- Primary metric: executable target success
- Secondary diagnostics: failure taxonomy and gold proximity

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

## Run Config

All runs used structured JSON output. Temperature and provider
thinking/reasoning controls were not explicitly set by PSE-RepairBench, so they
are recorded as provider defaults under the v0.1.5 LLM run config contract.

## Aggregate Results

| provider/model | pipeline success | executable success | executable failures |
| --- | ---: | ---: | --- |
| `gemini/gemini-3.1-flash-lite` | 19/19 | 9/19 | `right_parameter_wrong_value=6`, `wrong_parameter=3`, `wrong_target=1` |
| `gemini/gemini-3.5-flash` | 19/19 | 10/19 | `right_parameter_wrong_value=6`, `wrong_parameter=2`, `wrong_target=1` |
| `gemini/gemini-3.1-pro-preview` | 19/19 | 14/19 | `right_parameter_wrong_value=1`, `wrong_parameter=3`, `wrong_target=1` |
| `openai/gpt-5.4-nano` | 19/19 | 6/19 | `right_parameter_wrong_value=9`, `wrong_action_pair=1`, `wrong_parameter=2`, `wrong_target=1` |
| `openai/gpt-5.4-mini` | 19/19 | 9/19 | `right_parameter_wrong_value=8`, `wrong_parameter=2` |
| `openai/gpt-5.5` | 19/19 | 12/19 | `right_parameter_wrong_value=4`, `wrong_parameter=3` |

Gold proximity diagnostics:

| provider/model | `gold_exact` | `right_parameter_different_value` | `wrong_parameter` | `wrong_target` |
| --- | ---: | ---: | ---: | ---: |
| `gemini/gemini-3.1-flash-lite` | 1 | 14 | 3 | 1 |
| `gemini/gemini-3.5-flash` | 2 | 13 | 2 | 2 |
| `gemini/gemini-3.1-pro-preview` | 5 | 9 | 3 | 2 |
| `openai/gpt-5.4-nano` | 0 | 15 | 2 | 1 |
| `openai/gpt-5.4-mini` | 2 | 14 | 3 | 0 |
| `openai/gpt-5.5` | 3 | 12 | 3 | 1 |

Successful gold mismatch diagnostics:

| provider/model | `exec_success_with_gold_mismatch_count` | `wrong_parameter_success_count` |
| --- | ---: | ---: |
| `gemini/gemini-3.1-flash-lite` | 8 | 0 |
| `gemini/gemini-3.5-flash` | 8 | 0 |
| `gemini/gemini-3.1-pro-preview` | 9 | 0 |
| `openai/gpt-5.4-nano` | 6 | 0 |
| `openai/gpt-5.4-mini` | 7 | 1 |
| `openai/gpt-5.5` | 9 | 0 |

## Output Locations

- `.tmp/live_runs/gemini_terminal_native_units_balanced_gemini_3_1_flash_lite/aggregate.json`
- `.tmp/live_runs/gemini_terminal_native_units_balanced_gemini_3_5_flash/aggregate.json`
- `.tmp/live_runs/gemini_terminal_native_units_balanced_gemini_3_1_pro_preview/aggregate.json`
- `.tmp/live_runs/openai_terminal_native_units_balanced_gpt_5_4_nano/aggregate.json`
- `.tmp/live_runs/openai_terminal_native_units_balanced_gpt_5_4_mini/aggregate.json`
- `.tmp/live_runs/openai_terminal_native_units_balanced_gpt_5_5/aggregate.json`

Raw model outputs and evaluator reports remain untracked under `.tmp`.

## Interpretation

The benchmark shows meaningful model separation. All three models produced
schema-valid, executable pipelines for every instance, so the differentiating
signal comes from repair selection and value quality rather than infrastructure
failure.

`gemini-3.1-pro-preview` achieved the highest executable success and the most
gold-exact repairs. It also sharply reduced `right_parameter_wrong_value`,
suggesting better numeric/specification inference. The two Flash models were
close to each other, with `gemini-3.5-flash` slightly ahead of
`gemini-3.1-flash-lite` on executable success.

`openai/gpt-5.4-mini` matched `gemini-3.1-flash-lite` on executable success in
this first run. It had no `wrong_target` executable failures, but produced more
right-parameter wrong-value misses. It also produced one wrong-parameter
successful repair, which is useful evidence that executable success and gold
proximity diagnostics should remain separated.

The OpenAI family shows the expected internal ordering on this pilot:
`gpt-5.4-nano` < `gpt-5.4-mini` < `gpt-5.5` by executable success. `gpt-5.5`
reduced value-quality failures relative to mini, but did not reach
`gemini-3.1-pro-preview` on this 19-instance set. `gpt-5.4-nano` still kept the
pipeline stable for every instance, but its lower executable score and one
wrong-action-pair failure make it a useful low-cost floor rather than a ceiling
candidate.

Gold exact match remains too strict as a primary metric. Across all models,
many successful repairs differ from hidden gold while still satisfying the
terminal process target. This supports the v0.1.5 protocol choice: executable
target success is primary, and gold proximity is diagnostic.
