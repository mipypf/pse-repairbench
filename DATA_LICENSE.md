# Data And Instance License

PSE-RepairBench is a mixed-license repository. This file defines the license for
benchmark data and source-derived artifacts; it does not replace the repository's
software license.

## License

Except where an individual file or its recorded source metadata states
otherwise, the benchmark data and source-derived artifacts described below are
distributed under the
[Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/)
(CC BY-SA 4.0).

The current `final_v0_1_5` artifact was built from flowsheets published through
the [FOSSEE DWSIM Flowsheeting Project](https://dwsim.fossee.in/flowsheeting-project/completed-flowsheet).
All 123 current candidate instances record the source flowsheet license as
`Creative Commons Attribution-ShareAlike 4.0 International License` in their
`instance.json` `source` object.

## Path Scope

The data license applies to redistributable benchmark and source-derived files
under these paths:

- `curated_data/`
- `instances/`
- `metadata/dwsim_sources/`
- `results/`
- `examples/manuscript_cases/*.json` (copies of recorded model outputs)

This scope includes generated benchmark instances, source-derived DWSIM
flowsheets, source-screening metadata, simulator run artifacts, and tracked
benchmark evaluation data. If a file carries a more specific license or
third-party notice, that notice controls for that file.

The tracked archives under `curated_data/dwsim_headless_successes/` contain the
DWSIM flowsheet entries needed for benchmark reproduction. Source abstract PDFs
and their embedded logos/graphics are intentionally excluded. The ignored local
`raw_data/` directory is not part of the repository distribution or the license
grant in this file.

Project-authored source code, schemas, tests, documentation, and configuration
files are licensed under the Apache License, Version 2.0. See [LICENSE](LICENSE).

## Attribution And ShareAlike Requirements

When redistributing the data or adaptations:

1. Preserve each generated instance's `source` object and the structured
   [source attribution manifest](metadata/dwsim_sources/source_attribution_manifest.json)
   shipped with the release.
2. Credit the FOSSEE DWSIM Flowsheeting Project and the flowsheet contributor
   and source title recorded in that manifest.
3. Link to the source collection and to the
   [CC BY-SA 4.0 license](https://creativecommons.org/licenses/by-sa/4.0/).
4. State that PSE-RepairBench modified the source materials as described below.
5. Distribute adaptations under CC BY-SA 4.0 or another license permitted by
   the CC BY-SA 4.0 terms.

See [docs/source_attribution.md](docs/source_attribution.md) for the attribution
record and release wording.

## Modifications Made By PSE-RepairBench

PSE-RepairBench screened and selected source flowsheets, reorganized and renamed
archives, extracted simulator metadata, changed process parameters, injected
faults, generated repair tasks and benchmark splits, reran simulations, and
generated evaluation artifacts. These changes are not endorsed by FOSSEE, the
individual flowsheet contributors, or the DWSIM developers.

## Third-Party Software

[DWSIM](https://dwsim.org/) is third-party software distributed under the GNU
General Public License v3. DWSIM binaries and source code are not included in
this repository or licensed by this file. DWSIM must be installed separately for
simulator-backed workflows.
