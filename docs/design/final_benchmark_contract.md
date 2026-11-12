# Final Benchmark Contract

This document is the canonical contract for the `final_v0_1_5` artifact.

## Artifact Identity

- Version: `v0.1.5`
- Dataset root: `instances/final_v0_1_5`
- Candidate pool: `instances/final_v0_1_5/candidate_pool`
- Split directory: `instances/final_v0_1_5/splits`
- Candidate pool size: 123 instances
- Dev split size: 23 instances
- Test split size: 100 instances

The candidate pool is the generated population. Dev and test are views over
that population, defined by `splits/dev.txt`, `splits/test.txt`, and
`splits/split_manifest.json`.

## Non-Current Fixtures

`instances/seed/` and `instances/legacy/` are not part of the current
`final_v0_1_5` benchmark artifact. They remain tracked for smoke tests,
reference checks, examples, and historical provenance.

- `instances/seed/` contains the two original v0.1 vertical-slice fixtures.
  The reference builders under `scripts/build_instances/reference/` can still
  regenerate those fixtures directly.
- `instances/legacy/` contains the historical `distillation_001` placeholder.
  It is retained only as legacy provenance and is validated with the seed
  profile, not as a current release candidate.

Current benchmark runs, model comparisons, result notes, and split membership
must use `instances/final_v0_1_5/candidate_pool` plus the files under
`instances/final_v0_1_5/splits`, unless a workflow explicitly says it is
testing historical fixtures.

## Instance Shape

Each instance lives in:

```text
instances/final_v0_1_5/candidate_pool/<instance_id>/
  instance.json
  public/
  hidden/
  _builder_work/
```

`instance.json` is the manifest. Paths inside the manifest are relative to the
instance directory.

`public/` contains model-visible artifacts only:

- `faulty.dwxmz`
- `problem.md`
- `llm_input.md`
- `parameters.json`
- `streams.csv`
- `topology.json`
- simulator log artifacts

`hidden/` contains artifacts that must not be shown to models during evaluation:

- base flowsheet
- repaired gold flowsheet
- base, faulty, and gold repaired runs
- metrics report
- deterministic hidden mock output
- gold repair actions and oracle metadata

`_builder_work/` contains tracked build provenance and audit artifacts produced
while materializing the instance:

- calculated base, faulty, and repaired flowsheets from the builder runs
- `llm_input_context.json`, the intermediate context used to render the public
  LLM input packet

`_builder_work/` is not a public artifact and must not be shown to models. It
is also not part of the normal evaluator, live LLM, or baseline runner input
contract; those workflows resolve paths through `instance.json`, `public/`,
and `hidden/`. The directory is retained to make the checked-in artifact easier
to audit and compare against regeneration outputs.

## Repair Task

The task is one-shot executable semantic repair of a DWSIM flowsheet. The model
receives a faulty case and must produce a canonical structured repair output.
The evaluator applies that repair, reruns DWSIM, and checks whether the target
metric is recovered.

The model does not edit DWSIM XML directly. It emits a JSON repair action:

```json
{
  "type": "set_unit_parameter",
  "target": {
    "kind": "unit_operation",
    "guid": "...",
    "tag": "..."
  },
  "parameter": {
    "namespace": "...",
    "name": "..."
  },
  "value": 123.0,
  "unit": null,
  "rationale": "optional action-level rationale"
}
```

## Supported Parameter Families

`final_v0_1_5` contains these scalar repair parameters:

```text
column_configuration/feed_stage:          5
column_specification/reflux_ratio:        6
pressure_specification/outlet_pressure:  33
separator_specification/pressure:        16
separator_specification/temperature:     13
thermal_specification/outlet_temperature:50
```

All targets are existing process objects. The benchmark does not ask models to
add or delete units, reconnect streams, choose property packages, or rewrite
flowsheet files.

## Target Families

The executable success check uses terminal stream target metrics:

```text
terminal_temperature:  54
terminal_flow:         27
terminal_pressure:     21
terminal_composition:  21
```

The evaluator records `target_metric`, `success_criteria`, and
`executable_success` for every run.

## Primary Metric

The primary benchmark metric is executable target success:

```text
executable_success = schema valid
                  and repair action executable
                  and DWSIM rerun completed without fatal error
                  and target metric satisfies the threshold
```

Gold action proximity is diagnostic, not the primary success condition. A model
can succeed with a different action from the hidden gold repair if the repaired
flowsheet satisfies the target.

## Failure Taxonomy

Live LLM runs should distinguish model, executor, simulator, and target
failures:

- `provider_config_failure`
- `provider_call_failure`
- `model_output_failure`
- `schema_failure`
- `executor_failure`
- `executor_timeout`
- `dwsim_failure`
- `dwsim_timeout`
- `wrong_target`
- `wrong_parameter`
- `wrong_action_pair`
- `right_parameter_wrong_value`
- `target_failure`

`dwsim_timeout` is a valid simulator-grounded failure subtype. It usually means
the model produced a syntactically valid but poor repair action whose repaired
flowsheet becomes slow or non-convergent under DWSIM. It should be recorded,
not converted into a missing aggregate or external watchdog failure.

## Validation Contract

The candidate pool must pass file-required validation:

```powershell
.\.venv\Scripts\python.exe scripts\validate\validate_instances.py `
  instances\final_v0_1_5\candidate_pool `
  --profile pilot `
  --require-files
```

The promoted pool passed hidden-mock evaluation with:

```text
pipeline_success:   123/123
executable_success: 123/123
```

Hidden-mock success proves the instance artifacts and evaluator path are
executable with the gold repair. It does not imply that live LLM runs should
match gold exactly.

## Scope Boundaries

In scope for `v0.1.5`:

- DWSIM flowsheets
- one faulty case per instance
- one-shot structured repair
- scalar process-object parameters
- simulator-grounded target recovery

Out of scope for `v0.1.5`:

- multi-step agents
- retries after simulator feedback
- direct XML editing
- topology addition or deletion
- property-package selection
- manual GUI interaction
- claiming general multi-simulator support
