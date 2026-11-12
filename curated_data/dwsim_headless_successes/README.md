# DWSIM Headless Success Archives

This directory contains curated FOSSEE/DWSIM flowsheet archives that
passed the headless DWSIM Automation3 smoke screen.

Success means `CalculateFlowsheet4` completed with `Solved=True` and zero
returned exceptions under the local DWSIM runner used for screening.

- Total archives: 161
- Total size: 19.89 MB
- Excluded source PDF files: 161

Category counts:
- `distillation`: 68
- `flash_separator`: 18
- `other_candidate`: 21
- `reaction_recycle`: 54

The DWSIM flowsheet entries are curated from `raw_data/DWSIM_data`.
Source abstract PDFs are intentionally excluded because they contain
third-party logos and graphics that are not needed for benchmark
reproduction. `manifest.csv` preserves the original archive name,
source checksum, curated checksum, and excluded-PDF count.

To re-run a single archive:

```powershell
powershell -ExecutionPolicy Bypass -File scripts\dwsim\run_dwsim_headless.ps1 -InputPath curated_data\dwsim_headless_successes\distillation\001_example.zip
```
