# DWSIM Headless Screening

This note records the reproducible screen used to identify raw DWSIM archives
that can be executed outside the GUI.

## Runner

The runner uses `DWSIM.Automation.Automation3` from the local DWSIM
installation. Each flowsheet is executed in an isolated PowerShell worker so
that a crash, stack overflow, timeout, or assembly-loading failure does not
poison the rest of the screen.

Success is defined as:

- the flowsheet loads successfully
- `CalculateFlowsheet4` returns zero exceptions
- `IFlowsheet.Solved` is `true`

The default timeout is 90 seconds for the scripts, while the initial full raw
data screen used 45 seconds per archive.

## Commands

Run one archive:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\dwsim\run_dwsim_headless.ps1 `
  -InputPath curated_data\dwsim_headless_successes\distillation\001_acetonitrile_water_distillation_combining_preconcentration_and_entrainer_column.zip
```

Screen raw data from the catalog:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\maintenance\screen_dwsim_headless.ps1 `
  -RawDir raw_data\DWSIM_data `
  -CatalogPath metadata\dwsim_sources\raw_data_catalog.csv `
  -OutDir .tmp\raw_data_dwsim_screen `
  -TimeoutSeconds 45
```

Regenerate the curated success archive set:

```powershell
.\.venv\Scripts\python.exe scripts\maintenance\curate_headless_successes.py --clean
```

## Outputs

The full screen produced:

- `metadata/dwsim_sources/dwsim_headless_screen_results.csv`
- `metadata/dwsim_sources/dwsim_headless_successes.csv`
- `metadata/dwsim_sources/dwsim_headless_failures.csv`
- `metadata/dwsim_sources/dwsim_headless_screen_summary.json`

The git-tracked curated archive set is:

- `curated_data/dwsim_headless_successes/`

It contains 161 source archives, curated from `raw_data/DWSIM_data` and grouped
by estimated category. Source abstract PDFs are excluded from the tracked
archives because they are not needed for benchmark reproduction. The archive
filenames are normalized for readability;
`curated_data/dwsim_headless_successes/manifest.csv` preserves the original
archive names, source and curated checksums, and excluded-PDF counts.
