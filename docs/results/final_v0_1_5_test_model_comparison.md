# final_v0_1_5 Test Model Comparison

## Summary

This note records the current `final_v0_1_5_test` results for nine live LLM
runs.

```text
split: final_v0_1_5_test
instance_count: 100
prompt_mode: parameter-selection
executor_timeout_sec: 60
dwsim_timeout_sec: 180
```

Primary metric: `executable_success`.

| Method | Run | Pipeline Success | Executable Success |
| --- | --- | ---: | ---: |
| `openai/gpt-5.4-mini` | `results/final_v0_1_5/test/gpt-5.4-mini/parameter-selection/run_20260608_01_backfilled` | 96/100 | 34/100 |
| `anthropic/claude-haiku-4-5-20251001` | `results/final_v0_1_5/test/claude-haiku-4-5-20251001/parameter-selection/run_20260609_01` | 78/100 | 36/100 |
| `gemini/gemini-3.1-flash-lite` | `results/final_v0_1_5/test/gemini-3.1-flash-lite/parameter-selection/run_20260608_01` | 87/100 | 38/100 |
| `openai/gpt-5.4-nano` | `results/final_v0_1_5/test/gpt-5.4-nano/parameter-selection/run_20260609_01_backfilled_provider_520` | 93/100 | 41/100 |
| `anthropic/claude-sonnet-4-6` | `results/final_v0_1_5/test/claude-sonnet-4-6/parameter-selection/run_20260609_01` | 83/100 | 47/100 |
| `anthropic/claude-opus-4-8` | `results/final_v0_1_5/test/claude-opus-4-8/parameter-selection/run_20260609_01` | 79/100 | 48/100 |
| `gemini/gemini-3.5-flash` | `results/final_v0_1_5/test/gemini-3.5-flash/parameter-selection/run_20260608_01` | 91/100 | 60/100 |
| `gemini/gemini-3.1-pro-preview` | `results/final_v0_1_5/test/gemini-3.1-pro-preview/parameter-selection/run_20260609_01_backfilled_provider_errors` | 90/100 | 66/100 |
| `openai/gpt-5.5` | `results/final_v0_1_5/test/gpt-5.5/parameter-selection/run_20260609_01_backfilled_provider_520` | 91/100 | 67/100 |

## Random Baseline

The [one-shot random baseline](../design/random_baseline_contract.md#recorded-run)
has a mean executable success rate of **8.6%** across five fixed seeds, with
sample standard deviation **1.14 percentage points**. Each seed evaluates one
proposal on each of the same 100 test tasks. These are five separate seeded
runs; no best-of-five repair or seed selection is used.

Its published JSON files use the basic evaluator aggregate schema:
`success_count` and per-row `report_path`, instead of the LLM aggregate fields
`executable_success_count` and `evaluation_report`. The row-level primary flag
remains `executable_success`. Provider metadata and the LLM batch failure
taxonomy are absent; execution errors are recorded as per-row `error_stage`.

## Simulator-Log Ablation

The [GPT-5.5 no-log aggregate](../../results/final_v0_1_5/test/gpt-5.5/parameter-selection/run_20261009_01_no_log_merged_quota/aggregate.json)
records 56/100 executable successes and 93/100 pipeline successes with
`omit_simulator_log=true`. Only the 38 tasks with no output due to quota errors
were rerun; the 62 already evaluated tasks were retained in the final 100-task
aggregate. Its per-instance artifact paths refer to unpublished local records.

The full-log result above is 67/100. The full-log run was conducted in June and
the no-log run in October 2026, so this comparison does not isolate a causal
effect of removing the log.

## Review Artifacts

The repository tracks sanitized `aggregate.json` files for the final test runs
listed above. These JSON aggregates are the machine-readable source for this
summary and include per-instance row outcomes.

The corresponding `aggregate.csv` files, per-instance prompts, provider
responses, provider metadata, and simulator work directories remain local run
artifacts unless separately curated. Tracked result aggregates must not contain
local absolute paths.

The two model responses discussed as manuscript case examples are copied under
[examples/manuscript_cases](../../examples/manuscript_cases/README.md).

## Backfill Policy

Provider-transient failures were backfilled only when the base run failed before
or during provider response parsing. Simulator failures, schema failures, and
semantic repair failures were not retried.

Backfilled final runs:

```text
openai/gpt-5.5:
  provider_call_failure 7 -> replaced by backfill rows

gemini/gemini-3.1-pro-preview:
  provider_call_failure/provider_response 3 -> replaced by backfill rows
  residual model_output_failure 1 is a repeated Gemini MAX_TOKENS JSON truncation

openai/gpt-5.4-mini:
  provider_call_failure 1 -> replaced by backfill row

openai/gpt-5.4-nano:
  provider_call_failure 1 -> replaced by backfill row
```

The Claude runs, `gemini/gemini-3.1-flash-lite`, and `gemini/gemini-3.5-flash`
did not need backfill.

## Failure Counts

| Method | Failure Counts |
| --- | --- |
| `openai/gpt-5.4-mini` | `dwsim_failure=4`, `right_parameter_wrong_value=13`, `wrong_action_pair=22`, `wrong_parameter=2`, `wrong_target=25` |
| `anthropic/claude-haiku-4-5-20251001` | `dwsim_failure=12`, `right_parameter_wrong_value=11`, `schema_failure=10`, `wrong_action_pair=11`, `wrong_parameter=1`, `wrong_target=19` |
| `gemini/gemini-3.1-flash-lite` | `dwsim_failure=13`, `right_parameter_wrong_value=14`, `wrong_action_pair=14`, `wrong_parameter=3`, `wrong_target=18` |
| `openai/gpt-5.4-nano` | `dwsim_failure=7`, `right_parameter_wrong_value=17`, `wrong_action_pair=15`, `wrong_parameter=3`, `wrong_target=17` |
| `anthropic/claude-sonnet-4-6` | `dwsim_failure=9`, `right_parameter_wrong_value=12`, `schema_failure=8`, `wrong_action_pair=11`, `wrong_target=13` |
| `anthropic/claude-opus-4-8` | `dwsim_failure=12`, `right_parameter_wrong_value=7`, `schema_failure=9`, `wrong_action_pair=10`, `wrong_parameter=1`, `wrong_target=13` |
| `gemini/gemini-3.5-flash` | `dwsim_failure=9`, `right_parameter_wrong_value=13`, `wrong_action_pair=10`, `wrong_parameter=1`, `wrong_target=7` |
| `gemini/gemini-3.1-pro-preview` | `dwsim_failure=9`, `model_output_failure=1`, `right_parameter_wrong_value=5`, `wrong_action_pair=12`, `wrong_parameter=3`, `wrong_target=4` |
| `openai/gpt-5.5` | `dwsim_failure=8`, `model_output_failure=1`, `right_parameter_wrong_value=9`, `wrong_action_pair=6`, `wrong_parameter=2`, `wrong_target=7` |

## Interpretation

Executable success remains the primary metric. Exact gold matching is useful as
a diagnostic, but several model successes are valid target recoveries despite
not matching the hidden gold repair value exactly.
