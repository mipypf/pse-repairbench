# Split Contract

This document defines the `final_v0_1_5` dev/test split.

## Files

```text
instances/final_v0_1_5/
  candidate_pool/
  splits/
    split_manifest.json
    dev.txt
    test.txt
```

`dev.txt` and `test.txt` contain instance directory names, one per line. Each
entry is resolved relative to `instances/final_v0_1_5/candidate_pool`.

## Rule

The split is source-level stratified:

- Candidate pool size: 123
- Dev instances: 23
- Test instances: 100
- Dev sources: 14
- Test sources: 36
- Source overlap between dev and test: not allowed
- Split id: `final_v0_1_5_source_stratified_v1`

The split was selected by deterministic beam search over source groups. The
stratification targets were:

- parameter family
- target family
- source category

The split is a view over the candidate pool. Do not copy or mutate instances to
construct a split.

## Manifest Provenance

`splits/split_manifest.json` records `local_generation_artifacts/...` paths for
the discovery, promotion, and hidden-mock evaluation artifacts used when the
candidate pool was selected. These are historical local-generation workspace
references retained as provenance labels. They are not repository-relative
tracked artifacts and are not expected to exist in a fresh checkout.

The tracked release artifact is the resulting candidate pool, split files, and
split manifest. The manifest's `hidden_mock_eval_success_count` records the
promotion check result.

## Dev Distribution

Parameter distribution:

```text
column_configuration/feed_stage:          1
column_specification/reflux_ratio:        1
pressure_specification/outlet_pressure:   6
separator_specification/pressure:         3
separator_specification/temperature:      3
thermal_specification/outlet_temperature: 9
```

Target family distribution:

```text
terminal_composition:  4
terminal_flow:         5
terminal_pressure:     4
terminal_temperature: 10
```

Source category distribution:

```text
distillation:       2
flash_separator:    6
other_candidate:    4
reaction_recycle:  11
```

## Test Distribution

Parameter distribution:

```text
column_configuration/feed_stage:           4
column_specification/reflux_ratio:         5
pressure_specification/outlet_pressure:   27
separator_specification/pressure:         13
separator_specification/temperature:      10
thermal_specification/outlet_temperature: 41
```

Target family distribution:

```text
terminal_composition: 17
terminal_flow:        22
terminal_pressure:    17
terminal_temperature: 44
```

Source category distribution:

```text
distillation:       7
flash_separator:   25
other_candidate:   19
reaction_recycle:  49
```

## Reconstruct Instance Paths

PowerShell:

```powershell
$ids = Get-Content instances\final_v0_1_5\splits\dev.txt | Where-Object { $_ }
$paths = foreach ($id in $ids) {
  Join-Path instances\final_v0_1_5\candidate_pool $id
}
```

Use `$paths` as the `--instances` argument for live LLM dev runs.

## Operational Rule

Use the dev split for prompt, evaluator, and reporting development. Do not run
unfinalized exploratory model comparisons on the test split. Test results should
be generated only after the evaluator contract, run config, and result table
format are frozen.
