# LLM Run Config Contract

This document defines the live model-run contract for `final_v0_1_5`.

## Required Run Metadata

Every live LLM aggregate must record:

```text
provider
model
prompt_mode
omit_simulator_log
dataset_split_id
git_commit
api_retry_max
model_output_retry
simulator_retry
structured_output_mode
provider_schema_variant
generation_settings
provider_capabilities
rows[]
```

Each row must include:

```text
instance_id
instance_path
omit_simulator_log
llm_output
llm_metadata
evaluation_report
provider_latency_sec
provider_usage_total_tokens
schema_valid
action_schema_valid
executor_success
dwsim_success
executor_timed_out
dwsim_timed_out
executor_timeout_sec
dwsim_timeout_sec
pipeline_success
executable_success
failure_type
error_stage
selected_action_pair
gold_action_pair
gold_proximity_type
gold_mismatch_success_type
```

## Prompt Log Condition

`omit_simulator_log` is a boolean prompt condition. The batch runner and
`generate_llm_input.py` accept `--omit-simulator-log` only together with
`--prompt-mode parameter-selection`; incompatible modes are rejected before
provider calls. The default is `false` and retains the existing full prompt.
When `true`, only the `Faulty Simulator Log` heading and body are omitted;
Target values and their formatting, candidate units, stream tables, allowed
actions, and output instructions remain identical.

The batch runner records the condition in `llm_metadata.json` for every case
(including input/provider failures and dry runs), aggregate JSON, JSON/CSV
rows, and the batch `llm_run_config`. `prompt_hash` still hashes the actual
sanitized prompt; `schema_hash` retains its existing meaning. Historical
aggregates without the field predate this option and use the full-log condition.
See `scripts/README.md` for a reproducible final-test preflight command.

## Current Dev Baseline Config

The current recorded dev baseline uses:

```text
dataset_split_id: final_v0_1_5_dev
provider: gemini
model: gemini-3.1-flash-lite
prompt_mode: parameter-selection
temperature: 0.0
structured_output: true
structured_output_mode: response_mime_type=application/json + response_json_schema
provider_schema_variant: canonical
api_retry_max: 0
model_output_retry: false
simulator_retry: false
executor_timeout_sec: 60
dwsim_timeout_sec: 180
```

Unspecified provider controls, such as `top_p` and thinking or reasoning
controls, remain provider default and must be recorded as provider default in
`generation_settings`.

## Output Directory Contract

Live runs write under the user supplied `--work-dir`.

Recommended path shape:

```text
results/final_v0_1_5/<split>/<model>/<prompt_mode>/run_<YYYYMMDD>_<NN>/
  aggregate.json
  aggregate.csv
  run_stdout.log
  run_stderr.log
  launcher_info.json
  instance_<hash>/
    llm_input.md
    <provider>_prompt.md
    <provider>_llm_output.json
    llm_metadata.json
    evaluation_report.json
    evaluation_work/
```

Per-instance work directories must use a short stable name such as
`instance_<hash>`. They must not use the full `instance_id` as the directory
name, because long source-derived instance ids can exceed Windows path-length
limits once `evaluation_work` artifacts are added.

The aggregate row keeps the full `instance_id`, `instance_path`, and report
paths, so shortening the work directory name does not change benchmark
identity.

The aggregate metadata fields `provider` and `model` are the canonical run
identity for live model results. Existing result directories use the historical
path shape `<split>/<model>/<prompt_mode>/...` for compatibility, so the path
is not the canonical provider label. Result tables should display live models
as `<provider>/<model>` using aggregate metadata.

## Timeout Contract

The evaluator has two internal simulator-facing timeout controls:

- `--executor-timeout-sec`: timeout for applying the repair action
- `--dwsim-timeout-sec`: timeout for the repaired DWSIM metric run

The dev baseline uses:

```text
executor_timeout_sec: 60
dwsim_timeout_sec: 180
```

If an outer watchdog is used, it must be longer than the internal DWSIM timeout
so the evaluator can write `evaluation_report.json`. Recommended outer timeout:

```text
outer_watchdog_timeout_sec: 240 to 300
```

`dwsim_timeout` is a normal benchmark failure subtype. It must be counted in
`failure_counts`, not collapsed into `model_output_failure` or a missing
aggregate.

## Failure Classification

Infrastructure and model-output failures:

- `provider_config_failure`
- `provider_call_failure`
- `model_output_failure`
- `schema_failure`

Repair application and simulator failures:

- `executor_failure`
- `executor_timeout`
- `dwsim_failure`
- `dwsim_timeout`

Target and gold-proximity failures after successful pipeline execution:

- `wrong_target`
- `wrong_parameter`
- `wrong_action_pair`
- `right_parameter_wrong_value`
- `target_failure`

`executable_success` is the primary metric. `gold_mismatch_success_type` is a
diagnostic field that records successful repairs that differ from the hidden
gold action.

## Reproduction Command

PowerShell:

```powershell
$ids = Get-Content instances\final_v0_1_5\splits\dev.txt | Where-Object { $_ }
$paths = foreach ($id in $ids) { Join-Path instances\final_v0_1_5\candidate_pool $id }

.\.venv\Scripts\python.exe scripts\llm\run_llm_pilot_batch.py `
  --provider gemini `
  --model gemini-3.1-flash-lite `
  --prompt-mode parameter-selection `
  --work-dir results\final_v0_1_5\dev\gemini-3.1-flash-lite\parameter-selection\run_YYYYMMDD_NN `
  --dataset-split-id final_v0_1_5_dev `
  --executor-timeout-sec 60 `
  --dwsim-timeout-sec 180 `
  --instances $paths
```
