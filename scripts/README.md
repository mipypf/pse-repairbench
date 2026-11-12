# Scripts

This directory separates everyday benchmark operations from lower-frequency
data regeneration tasks.

## Validate

- `validate/validate_instances.py`: validate `instances/**/instance.json`
  manifests against the schema and selected validation profile.
  The release profile currently supports the `distillation_002`
  `column_specification/reflux_ratio` and `column_configuration/feed_stage`
  seeds. Add validator and executor support together before promoting another
  parameter family to release.

## Evaluate

- `evaluate/evaluate_repair_output.py`: evaluate one repair-output JSON against
  an instance by running schema validation, the repair executor, DWSIM metrics,
  executable success checks, and gold-proximity scoring.
- `evaluate/evaluate_release_set.py`: evaluate all release instances with the
  same procedure and write per-instance reports plus aggregate JSON/CSV. The
  first supported mode is deterministic hidden mock output:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate\evaluate_release_set.py --instances instances\seed --mode hidden-mock --require-success
```

## DWSIM

- `dwsim/run_dwsim_headless.ps1`: run one `.zip`, `.dwxmz`, or `.dwxml`
  flowsheet through DWSIM Automation3 without opening the GUI.
- `dwsim/dwsim_headless_worker.ps1`: isolated worker used by the headless
  runner.
- `dwsim/dwsim_metrics_worker.ps1`: run one flowsheet, save the calculated
  file, and write target-unit metrics plus stream metrics to
  `-ResultJsonPath`.
- `dwsim/apply_repair_actions.py`: apply structured repair actions to a DWSIM
  flowsheet. The release executor supports canonical `set_unit_parameter`
  actions for `column_specification/reflux_ratio` and
  `column_configuration/feed_stage`; the pilot executor also supports
  `pressure_specification/outlet_pressure` for native Valve, Pump, and
  Compressor units in `OutletPressure` mode and
  `thermal_specification/outlet_temperature` for native Heater/Cooler units in
  `OutletTemperature` mode, plus `separator_specification/pressure` and
  `separator_specification/temperature` for native Vessel units with
  `OverrideP`/`OverrideT` enabled.

## Build Instances

- `build_instances/reference/build_distillation_002_reflux_slice.py`: reference
  sweep for the original reflux-ratio release seed.
- `build_instances/reference/build_distillation_002_feed_stage_slice.py`:
  reference sweep for the original feed-stage release seed.
- `build_instances/general/build_from_fault_spec.py`: build a release-style
  instance from a fixed v0.1/v0.1.5 fault spec. Defaults write generated
  artifacts to `.tmp/generated_pilot_native_units/<instance_id>/`.
- `build_instances/general/scan_registry_feasibility.py`: scan curated
  headless-success sources for executor-backed target+parameter pairs without
  running DWSIM solves.
- `build_instances/general/scan_family_feasibility.py`: read-only scan for
  future v0.1 final repair families. It checks candidate object counts,
  required mode/state coverage, XML field presence, and scalar value readability
  without mutating flowsheets or running DWSIM solves.
- `build_instances/general/discover_fault_specs.py`: perturb supported native
  unit parameters, score terminal material stream metric sensitivity, write
  candidate fault specs, and optionally build the top candidates under
  `.tmp/fault_discovery/`.
- `build_instances/general/run_bulk_discovery.py`: run sensitivity discovery
  across curated headless-success sources, select balanced pilot candidates,
  and optionally materialize generated pilot instances under `.tmp/`.
- `build_instances/general/specs/`: checked-in fault specs that regenerate the
  two v0.1 baseline seeds through the general builder.
- `build_instances/builder_common.py`: shared DWSIM XML/zip, metrics,
  observation, mock/gold, and proximity helpers used by release builders.
- `build_instances/prepare_dwsim_seed.py`: prepare the legacy
  `distillation_001_feed_stage_single` manifest and observation stubs.

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\build_from_fault_spec.py --fault-spec scripts\build_instances\general\specs\distillation_002_reflux_ratio_single.json --reference-instance instances\seed\distillation_002_reflux_ratio_single\instance.json
```

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\scan_registry_feasibility.py --category all --output-dir .tmp\native_unit_feasibility --overwrite
```

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\scan_family_feasibility.py --category all --output-dir .tmp\final_family_feasibility --overwrite
```

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\discover_fault_specs.py --source-flowsheet curated_data\dwsim_headless_successes\distillation\002_air_liquefaction_using_linde_single_column_system.zip --output-dir .tmp\fault_discovery\distillation_002 --source-id distillation_002 --write-specs --build-top-k 2
```

Discovery auto-replaces existing output only under `.tmp`; pass `--overwrite`
for any deliberate non-`.tmp` output directory replacement.

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\run_bulk_discovery.py --category all --limit 3 --max-instances 6 --max-per-target-pair 1 --build-selected --allow-source-errors
```

For the v0.1.5 terminal-stream pilot, use feasibility-guided source selection:

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\run_bulk_discovery.py --category all --source-selection feasible-balanced --feasibility-report .tmp\native_unit_feasibility\feasibility_report.json --max-instances 30 --max-per-source 2 --max-per-target-pair 1 --build-selected --allow-source-errors --overwrite --output-root .tmp\pilot_discovery_terminal_native_units_30 --generated-output-root .tmp\generated_terminal_native_units_30
```

After a discovery pass, rebalance from existing source reports without
rerunning source-level sensitivity sweeps:

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\run_bulk_discovery.py --reuse-discovery-root .tmp\pilot_discovery_terminal_native_units_30 --selection-strategy target-family-balanced --max-instances 24 --max-per-source 2 --max-per-target-pair 1 --build-selected --allow-source-errors --overwrite --output-root .tmp\pilot_discovery_terminal_native_units_balanced --generated-output-root .tmp\generated_terminal_native_units_balanced
```

With `--build-selected`, the runner exits nonzero unless at least
`--min-selected` candidates are selected and every selected candidate builds.
`--max-per-target-pair` prevents selecting multiple perturbation severities for
the same source target GUID and parameter family.

## LLM

- `llm/generate_llm_input.py`: assemble an LLM input packet from an instance
  manifest and public faulty observations. The default `oracle-parameter` mode
  uses the public problem statement; `parameter-selection` keeps the CLI name
  for compatibility but creates a transient target+parameter pair-selection
  prompt from observations and `allowed_repair_actions`. Parameter-selection
  prompts show `Observed Candidate Unit Parameters` for every allowed target
  unit and do not use the single suspect-unit `Faulty Target Unit Parameters`
  wording. Parameter-selection public artifacts generated by the general
  builder omit `target_parameter`.
  `--omit-simulator-log` removes only the `Faulty Simulator Log` section in
  `parameter-selection` mode; omitting the flag preserves the full packet,
  including the existing Target number formatting.
- `llm/llm_provider.py`: small provider adapter for structured live model calls.
  Gemini uses `google-genai`; OpenAI uses the Responses API; Anthropic uses the
  Messages API. Live runs read `GEMINI_API_KEY`, `OPENAI_API_KEY`, or
  `CLAUDE_API_KEY` from the environment first, then from `.env`.
- `llm/generate_llm_output.py`: call a live provider with structured output to
  produce a repair-action JSON from `llm_input.md`. Defaults remain Gemini for
  compatibility, and outputs write to `.tmp/` so live model output does not
  replace deterministic mock artifacts.
- `llm/run_gemini_repair_smoke.py`: run one live provider output through the
  repair executor and DWSIM metrics worker, then report pipeline success
  separately from repair success.
- `llm/run_gemini_pilot_batch.py`: legacy-compatible batch entrypoint for live
  provider output generation and evaluator scoring across a pilot instance set.
- `llm/run_llm_pilot_batch.py`: provider-neutral alias for the same pilot batch
  runner.
  Both batch entrypoints write per-instance output plus aggregate JSON/CSV.
  `failure_type` classifies executable failures only; successful non-gold
  repairs are recorded through gold-proximity diagnostic fields. Use
  `--dry-run-sanitize` to check prompts without network access.
  Both accept `--omit-simulator-log` with `--prompt-mode parameter-selection`.
  The boolean `omit_simulator_log` is recorded in per-instance
  `llm_metadata.json`, aggregate JSON, and JSON/CSV rows, including failures
  and dry runs. Existing prompt/schema hashes retain their meanings.

```powershell
.\.venv\Scripts\python.exe scripts\llm\run_gemini_pilot_batch.py --instances .tmp\generated_pilot_instances --dry-run-sanitize
```

Dry-run prompt checks are reported under `preflight_counts`; live-model
execution failures are reported under `failure_counts`.

Reproduce a simulator-log ablation preflight for the final 100 test instances
(no API or simulator calls):

```powershell
$ids = Get-Content instances\final_v0_1_5\splits\test.txt | Where-Object { $_ }
$paths = foreach ($id in $ids) { Join-Path instances\final_v0_1_5\candidate_pool $id }
.\.venv\Scripts\python.exe scripts\llm\run_llm_pilot_batch.py `
  --provider openai --model gpt-5.5 --prompt-mode parameter-selection `
  --omit-simulator-log --dry-run-sanitize `
  --dataset-split-id final_v0_1_5_test `
  --work-dir .tmp\prompt_ablation\no_log_preflight `
  --instances $paths
```

For the full-log control, omit `--omit-simulator-log` and use a separate work
directory. Removing `--dry-run-sanitize` runs the same provider, output
validator, repair evaluator, and success criteria used by the existing batch
runner. Generated experiment artifacts remain under `.tmp/`.

```powershell
.\.venv\Scripts\python.exe scripts\llm\run_gemini_pilot_batch.py --instances .tmp\generated_pilot_instances --prompt-mode parameter-selection --work-dir .tmp\live_runs\gemini_parameter_selection_pilot --dry-run-sanitize
```

OpenAI smoke/dry-run examples:

```powershell
.\.venv\Scripts\python.exe scripts\llm\run_llm_pilot_batch.py --provider openai --model gpt-5.4-mini --instances .tmp\generated_terminal_native_units_balanced --prompt-mode parameter-selection --work-dir .tmp\live_runs\openai_terminal_native_units_balanced_gpt_5_4_mini --dry-run-sanitize
```

```powershell
.\.venv\Scripts\python.exe scripts\llm\run_llm_pilot_batch.py --provider openai --model gpt-5.4-mini --instances .tmp\generated_terminal_native_units_balanced --prompt-mode parameter-selection --work-dir .tmp\live_runs\openai_terminal_native_units_balanced_gpt_5_4_mini
```

Separator pilot smoke after a registry-feasibility scan:

```powershell
.\.venv\Scripts\python.exe scripts\build_instances\general\run_bulk_discovery.py --category all --source-selection feasible-balanced --feasibility-report .tmp\native_unit_feasibility_separator_bool_flexible\feasibility_report.json --max-instances 15 --min-selected 15 --max-per-source 2 --max-per-parameter 4 --max-per-target-family 5 --max-per-target-pair 1 --selection-strategy target-family-balanced --build-selected --allow-source-errors --overwrite --output-root .tmp\pilot_discovery_candidate_units_separator_15 --generated-output-root .tmp\generated_candidate_units_separator_15
```

Gate the live run on pilot validation, hidden-mock success, dry-run sanitize,
and at least one selected separator pressure or temperature instance.

## Baselines

- `baselines/run_random_baseline.py`: generate every one-shot random proposal
  before evaluating saved outputs with the existing evaluator. Uses explicit
  public candidate pairs/current values, fixed per-task random seeds, and no
  LLM provider or simulator feedback. The default
  `baselines/random_baseline_final_v0_1_5.json` fixes five seeds and the 100-task
  test split. `--phase generate` needs no DWSIM; `--phase evaluate` does.
  See [the baseline contract](../docs/design/random_baseline_contract.md) for
  formal commands and the one-task dev smoke check. Existing evaluation reports
  prevent duplicate evaluation, and altered saved proposals stop preflight.

## Maintenance

- `maintenance/catalog_raw_data.py`: rebuild the raw FOSSEE/DWSIM source
  archive catalog.
- `maintenance/screen_dwsim_headless.ps1`: screen raw DWSIM archives in bulk
  with Automation3.
- `maintenance/curate_headless_successes.py`: curate successful raw archives
  into `curated_data/dwsim_headless_successes/`, exclude source abstract PDFs,
  and write the curated manifest.
