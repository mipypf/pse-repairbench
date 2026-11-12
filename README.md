# PSE-RepairBench

This repository contains the code and benchmark data accompanying the paper:

“PSE-RepairBench: A simulator-grounded benchmark for evaluating large language model-based setpoint correction in executable chemical process flowsheets”
Digital Discovery.
https://doi.org/10.1039/d6dd00673f

The code and benchmark data accompanying the paper are archived on Zenodo:
- Paper-associated version: https://doi.org/10.5281/zenodo.23657528
- All versions: https://doi.org/10.5281/zenodo.23657527

PSE-RepairBench is a research benchmark for evaluating whether language models
can diagnose and repair executable DWSIM chemical-process flowsheets from
process-engineering observations.

Models do not edit DWSIM XML directly. They receive a faulty flowsheet plus
public observations and return a canonical structured repair action. The
evaluator applies that action, reruns DWSIM, and checks whether the target
process metric is recovered.

## Current Artifact

The current benchmark artifact is `final_v0_1_5`.

- Dataset: `instances/final_v0_1_5/candidate_pool`
- Candidate pool: 123 instances
- Dev split: 23 instances
- Test split: 100 instances
- Canonical contract:
  [docs/design/final_benchmark_contract.md](docs/design/final_benchmark_contract.md)
- Split contract: [docs/design/split_contract.md](docs/design/split_contract.md)
- Live-run contract:
  [docs/design/llm_run_config_contract.md](docs/design/llm_run_config_contract.md)
- Random baseline protocol:
  [docs/design/random_baseline_contract.md](docs/design/random_baseline_contract.md)
- Documentation entry point: [docs/index.md](docs/index.md)

Historical fixtures under `instances/seed/` and `instances/legacy/` are retained
for smoke tests, examples, reference checks, and provenance. They are not part
of the current `final_v0_1_5` benchmark surface.

## License

PSE-RepairBench is a mixed-license repository. The licenses apply by file type;
the repository is not distributed under a single blanket license.

- Project-authored source code, schemas, tests, documentation, and configuration
  files are licensed under the
  [Apache License, Version 2.0](LICENSE).
- Benchmark data, generated instances, source-derived DWSIM flowsheets,
  source-derived metadata, and tracked evaluation data are distributed under the
  [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/)
  (CC BY-SA 4.0), except where an individual file records a different source
  license. See [DATA_LICENSE.md](DATA_LICENSE.md) for the exact path scope.
- Source attribution and modification information is recorded in
  [docs/source_attribution.md](docs/source_attribution.md), the structured
  [FOSSEE source manifest](metadata/dwsim_sources/source_attribution_manifest.json),
  and each generated instance's `source` object.

[DWSIM](https://dwsim.org/) is third-party software licensed under GPLv3. DWSIM
itself is not included in this repository and must be installed separately.
The repository's Apache-2.0 license does not relicense DWSIM or the source
flowsheets.

## Contents

### 1. `instances/final_v0_1_5/`

The current benchmark artifact.

- `candidate_pool/`: 123 generated instances
- `splits/dev.txt`: dev split instance ids
- `splits/test.txt`: test split instance ids
- `splits/split_manifest.json`: source-level stratified split metadata

Each candidate instance contains `instance.json`, model-visible `public/`
artifacts, hidden evaluator artifacts under `hidden/`, and tracked build
provenance under `_builder_work/`.

### 2. `docs/`

Reader and maintainer documentation.

- [docs/index.md](docs/index.md): documentation entry point
- [docs/docs_inventory.md](docs/docs_inventory.md): current and archived docs
- [docs/design/](docs/design): current benchmark contracts
- [docs/results/](docs/results): current result notes
- [docs/archive/](docs/archive): historical, non-canonical notes

### 3. `scripts/`

Validation, evaluation, DWSIM utilities, instance builders, live model runners,
and maintenance checks. See [scripts/README.md](scripts/README.md).

### 4. `results/final_v0_1_5/`

Tracked dev and test run artifacts for the current benchmark artifact. The
current result summaries are:

- [docs/results/final_v0_1_5_test_model_comparison.md](docs/results/final_v0_1_5_test_model_comparison.md)
- [docs/results/final_v0_1_5_dev_gemini_flash_lite.md](docs/results/final_v0_1_5_dev_gemini_flash_lite.md)

### 5. `schemas/`

JSON schemas for benchmark instances and repair outputs.

- [schemas/instance.schema.json](schemas/instance.schema.json)
- [schemas/repair_action.schema.json](schemas/repair_action.schema.json)
- [schemas/repair_output.schema.json](schemas/repair_output.schema.json)

### 6. `raw_data/`, `curated_data/`, and `metadata/`

Source data, curated headless-success DWSIM archives, and source screening
metadata. Source-derived metadata for DWSIM screening lives under
`metadata/dwsim_sources/`.

## How To Use

### 1. Install Python dependencies

Use Python 3.11 or newer.

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

### 2. Configure optional live-model credentials

Validation, unit tests, split reconstruction, and aggregate inspection do not
require API keys. Live LLM runs require credentials for the provider being
tested and access to a comparable model.

Copy [.env.example](.env.example) to `.env` and fill the providers you plan to
run:

```powershell
Copy-Item .env.example .env
```

The runner reads these names from the process environment first, then from
`.env`:

```text
GEMINI_API_KEY   # provider: gemini
OPENAI_API_KEY   # provider: openai
CLAUDE_API_KEY   # provider: anthropic
```

`.env` is ignored by git and must not be committed.

### 3. Validate the current artifact

```powershell
.\.venv\Scripts\python.exe scripts\maintenance\sanitize_artifact_paths.py --check instances metadata\dwsim_sources docs\dwsim
.\.venv\Scripts\python.exe scripts\validate\validate_instances.py instances\final_v0_1_5\candidate_pool --profile pilot --require-files
```

### 4. Reconstruct split instance paths

PowerShell:

```powershell
$ids = Get-Content instances\final_v0_1_5\splits\dev.txt | Where-Object { $_ }
$paths = foreach ($id in $ids) {
  Join-Path instances\final_v0_1_5\candidate_pool $id
}
```

Use the resulting `$paths` as the `--instances` argument for dev live-model
runs. Use `test.txt` only for frozen test comparisons.

### 5. Run a repeat live-model experiment

The batch runner covers the full live-model protocol: it builds the prompt from
each instance's public artifacts, calls the provider, validates the structured
repair output, applies the repair, reruns DWSIM, writes per-instance evaluation
reports, and writes aggregate JSON/CSV.

Use a dry run first to generate and sanitize prompts without provider calls or
DWSIM reruns:

```powershell
$Split = "dev"
$Provider = "gemini"
$Model = "gemini-3.1-flash-lite"
$PromptMode = "parameter-selection"
$RunId = "run_YYYYMMDD_01_dry_run"
$WorkDir = "results\final_v0_1_5\$Split\$Model\$PromptMode\$RunId"

$ids = Get-Content "instances\final_v0_1_5\splits\$Split.txt" | Where-Object { $_ }
$paths = foreach ($id in $ids) {
  Join-Path instances\final_v0_1_5\candidate_pool $id
}

.\.venv\Scripts\python.exe scripts\llm\run_llm_pilot_batch.py `
  --provider $Provider `
  --model $Model `
  --prompt-mode $PromptMode `
  --work-dir $WorkDir `
  --aggregate-json "$WorkDir\aggregate.json" `
  --aggregate-csv "$WorkDir\aggregate.csv" `
  --dataset-split-id "final_v0_1_5_$Split" `
  --executor-timeout-sec 60 `
  --dwsim-timeout-sec 180 `
  --dry-run-sanitize `
  --instances $paths
```

For a live simulator-backed run, remove `--dry-run-sanitize` and use a fresh
run id:

```powershell
$RunId = "run_YYYYMMDD_01"
$WorkDir = "results\final_v0_1_5\$Split\$Model\$PromptMode\$RunId"

.\.venv\Scripts\python.exe scripts\llm\run_llm_pilot_batch.py `
  --provider $Provider `
  --model $Model `
  --prompt-mode $PromptMode `
  --work-dir $WorkDir `
  --aggregate-json "$WorkDir\aggregate.json" `
  --aggregate-csv "$WorkDir\aggregate.csv" `
  --dataset-split-id "final_v0_1_5_$Split" `
  --executor-timeout-sec 60 `
  --dwsim-timeout-sec 180 `
  --instances $paths
```

The output directory contains:

```text
aggregate.json
aggregate.csv
instance_<hash>/
  llm_input.md
  <provider>_prompt.md
  <provider>_llm_output.json
  llm_metadata.json
  evaluation_report.json
  evaluation_work/
```

### 6. Run lightweight checks

```powershell
.\.venv\Scripts\python.exe -m unittest discover -s tests
```

### One-shot random baseline

The random baseline uses the same public candidate parameters and evaluator,
with five fixed seeds and one proposal per test task per seed. Commit the
generator/config before formal generation, save all proposals, then evaluate
the frozen files:

```powershell
$RunDir = "results\final_v0_1_5\test\random-one-shot-v1\parameter-selection\run_YYYYMMDD_01"
.\.venv\Scripts\python.exe scripts\baselines\run_random_baseline.py --phase generate --run-dir $RunDir
.\.venv\Scripts\python.exe scripts\baselines\run_random_baseline.py --phase evaluate --run-dir $RunDir
```

Generation requires no API key or simulator. See the
[baseline contract](docs/design/random_baseline_contract.md) for the sampling
ranges, feed-stage candidate assumption, dev smoke check, and seed aggregation
rules. Evaluation requires DWSIM and uses no feedback or retries.

### 7. Work with DWSIM-dependent flowsheets

DWSIM-dependent execution requires DWSIM installed on Windows with the
Automation3 interface available to the PowerShell runner. Lightweight metadata
validation and unit tests do not require DWSIM, but headless screening,
simulator-backed evaluation, and instance regeneration do.

The checked-in `final_v0_1_5` artifacts record DWSIM build `9.0.5.0`; rerunning
or regenerating simulator artifacts under another DWSIM build should be treated
as an environment change. For the current headless-screening and extraction
notes, see:

- [docs/dwsim/headless_screening.md](docs/dwsim/headless_screening.md)
- [docs/dwsim/extraction_notes.md](docs/dwsim/extraction_notes.md)

Example headless run:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\dwsim\run_dwsim_headless.ps1 -InputPath curated_data\dwsim_headless_successes\distillation\001_acetonitrile_water_distillation_combining_preconcentration_and_entrainer_column.zip
```

## Execution Environment

Lightweight validation and unit tests are expected to run on Python 3.11 or
newer. The repository CI runs these checks on Windows.

DWSIM-dependent workflows are Windows-local and environment-sensitive. Preserve
the recorded source attribution and sanitized artifact paths when sharing
regenerated instances or result aggregates.

## Reproduction Scope

This repository is intended to support repeat experiments under the same
artifact, split, prompt/evaluator contract, and result schema.

The following checks are reproducible from the checked-in files without DWSIM or
provider credentials:

- validate the current instance manifests and required files
- reconstruct dev/test split membership
- inspect and compare tracked sanitized result aggregates
- run lightweight unit tests

Simulator-backed reruns require Windows, Python 3.11 or newer, and a local
DWSIM Automation3 environment comparable to the recorded DWSIM `9.0.5.0`
artifact environment.

Live-model reruns additionally require the relevant API key, provider access to
a comparable model, and the same benchmark protocol. Exact bit-for-bit
reproduction of live model results is not guaranteed because providers may
update models, APIs may be nondeterministic, and transient provider failures may
require documented backfill.
