# final_v0_1_5 Dev Gemini Flash-Lite Baseline

## Summary

This note records the current dev baseline for `final_v0_1_5`.

```text
split: final_v0_1_5_dev
method: gemini/gemini-3.1-flash-lite
provider: gemini
model: gemini-3.1-flash-lite
prompt_mode: parameter-selection
run: results/final_v0_1_5/dev/gemini-3.1-flash-lite/parameter-selection/run_20260608_02
git_commit: ba12709
```

Primary result:

```text
instance_count: 23
pipeline_success: 22/23
executable_success: 9/23
```

Failure counts:

```text
wrong_target: 5
wrong_action_pair: 3
wrong_parameter: 3
right_parameter_wrong_value: 2
dwsim_timeout: 1
```

No path-length or malformed-output failures were observed in this run:

```text
model_output_failure: 0
path_length_error: 0
```

## Artifacts

- Aggregate JSON:
  `results/final_v0_1_5/dev/gemini-3.1-flash-lite/parameter-selection/run_20260608_02/aggregate.json`
- Aggregate CSV:
  `results/final_v0_1_5/dev/gemini-3.1-flash-lite/parameter-selection/run_20260608_02/aggregate.csv`
- Standard output log:
  `results/final_v0_1_5/dev/gemini-3.1-flash-lite/parameter-selection/run_20260608_02/run_stdout.log`

The raw per-instance outputs and simulator work directories are also present
under the run directory. For public summaries, `aggregate.json`,
`aggregate.csv`, and this note are the important artifacts.

## Timeout Case

The single timeout is:

```text
instance_id: 011_ethylene_oxide_production_from_styrene_c_1_outlet_pressure_003
failure_type: dwsim_timeout
error_stage: dwsim_timeout
dwsim_timed_out: true
dwsim_timeout_sec: 180
selected_action_pair: COOL-cb8be045-7787-47c1-8f6e-65adbaea6517: thermal_specification/outlet_temperature
gold_action_pair: C-1: pressure_specification/outlet_pressure
```

This is not a dataset corruption signal. The model returned a schema-valid
repair action quickly, but the selected action was the wrong process
intervention. The repaired flowsheet did not finish the DWSIM rerun within the
configured simulator timeout.

## Interpretation

Flash-Lite succeeds on 9/23 dev instances. All 9 executable successes are gold
mismatch successes:

```text
right_parameter_different_value_success: 8
wrong_action_pair_success: 1
```

This supports using executable success as the primary metric. Exact gold action
matching is useful diagnostically, but it is too strict as the main benchmark
score because alternate executable repairs can satisfy the target.

The main failure pattern is selecting the wrong target or action pair, rather
than failing to emit valid JSON. This is consistent with the intended benchmark
focus: process-grounded action selection and simulator-grounded recovery.
