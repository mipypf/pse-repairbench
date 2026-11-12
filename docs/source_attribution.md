# Source Attribution

This note records the source-data attribution policy for the current
`final_v0_1_5` benchmark artifact.

## Source Flowsheets

The DWSIM flowsheets used to build `final_v0_1_5` were published through the
[FOSSEE DWSIM Flowsheeting Project](https://dwsim.fossee.in/flowsheeting-project)
and selected from its
[Completed Flowsheets collection](https://dwsim.fossee.in/flowsheeting-project/completed-flowsheet).
PSE-RepairBench screened a local archive of that collection.

Relevant provenance files:

- `metadata/dwsim_sources/source_attribution_manifest.json`
- `metadata/dwsim_sources/raw_data_catalog.csv`
- `metadata/dwsim_sources/raw_data_catalog.jsonl`
- `metadata/dwsim_sources/dwsim_headless_screen_results.csv`
- `metadata/dwsim_sources/dwsim_headless_successes.csv`
- `metadata/dwsim_sources/dwsim_headless_failures.csv`
- `metadata/dwsim_sources/dwsim_headless_screen_summary.json`
- `docs/dwsim/headless_screening.md`

Each generated benchmark instance records its source metadata in
`instance.json` under the `source` object. Important fields include:

- `source_name`
- `curated_archive`
- `curated_source_entry`
- `dwsim_build_version`
- `license`
- `retrieved_at`

`curated_archive` joins to the same field in
`metadata/dwsim_sources/source_attribution_manifest.json`. The manifest records
the official title, FOSSEE `Contributor Name`, institution, completion year,
individual FOSSEE landing-page URL, original archive name, and flowsheet entry
for all 161 tracked curated archives. This includes the 50 unique source
flowsheets used by the current candidate pool. `source_name` is the shorter
per-instance source identifier, and `curated_source_entry` identifies the
flowsheet file within the curated archive.

Contributor names in the manifest reproduce the label used by FOSSEE's
Completed Flowsheets collection. PSE-RepairBench does not independently recast
that role as legal authorship.

## Legacy Fixture

`instances/legacy/distillation_001_feed_stage_single/` is derived from
"Benzene Toluene Fractionation Unit", contributed by K G Srinidhi of the
National Institute of Technology Karnataka, Surathkal, and published by the
[FOSSEE DWSIM Flowsheeting Project](https://dwsim.fossee.in/flowsheeting-project/dwsim-flowsheet-run/26).
Its recorded license is
[CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/).
PSE-RepairBench copied the flowsheet and extracted benchmark observations and
metadata. This historical fixture is outside the current `final_v0_1_5` split
and the curated-archive attribution manifest above.

## Source License

All 123 instances in the current `final_v0_1_5` candidate pool record the source
flowsheet license as:

```text
Creative Commons Attribution-ShareAlike 4.0 International License
```

The license text and conditions are available at the
[Creative Commons Attribution-ShareAlike 4.0 International license page](https://creativecommons.org/licenses/by-sa/4.0/).
The FOSSEE project also displays this license on its
[flowsheet submission guidelines](https://dwsim.fossee.org/flowsheeting-project/coding-guidelines-flowsheeting).

Treat flowsheet-containing benchmark artifacts as adaptations of those source
flowsheets unless a separate legal review says otherwise. Public releases must
preserve the per-instance source metadata and structured attribution manifest,
link to the license, and include this attribution note alongside the benchmark
artifact.

The tracked curated ZIP archives exclude all 161 source abstract PDFs. Those
PDFs contain third-party logos and graphics, are not required for benchmark
reproduction, and are not included in the repository's CC BY-SA data release.

## Modifications

PSE-RepairBench made changes to the source materials. The release pipeline:

- screened and selected source flowsheets;
- reorganized and renamed source archives;
- extracted topology, stream, parameter, and simulator metadata;
- changed process parameters and injected benchmark faults;
- generated repair tasks, public/hidden artifacts, and dev/test splits; and
- reran DWSIM and generated benchmark evaluation artifacts.

The resulting artifacts are PSE-RepairBench adaptations and are not endorsed by
FOSSEE, individual source contributors, or the DWSIM developers.

## Recommended Attribution

When redistributing a benchmark instance or an adapted flowsheet, fill in the
corresponding values from the structured source manifest and include:

> Adapted by the PSE-RepairBench contributors from "[official title]",
> contributed by [Contributor Name] and published by the FOSSEE DWSIM
> Flowsheeting Project at [individual source URL]. Licensed under CC BY-SA 4.0;
> changes were made as described in this repository.

## Repository License

The project code and documentation are licensed under Apache-2.0. See
`LICENSE` at the repository root.

The current benchmark data, generated instances, source-derived flowsheets,
source-derived metadata, and tracked evaluation data are distributed under
CC BY-SA 4.0 except where a file records a different source license. See
`DATA_LICENSE.md` at the repository root for the exact path scope.

## DWSIM Software

[DWSIM](https://dwsim.org/) is third-party software licensed under GPLv3. DWSIM
binaries and source code are not included in PSE-RepairBench and must be
installed separately. The Apache-2.0 license for project-authored repository code
does not apply to DWSIM itself.
