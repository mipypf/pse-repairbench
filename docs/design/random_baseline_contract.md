# One-Shot Random Baseline

The `random-one-shot-v1` baseline selects uniformly from all allowed
target-parameter pairs in the same public candidate summaries used by the
`parameter-selection` LLM packet. It produces exactly one action per task and
evaluates it with `scripts/evaluate/evaluate_repair_output.py`. It uses no
simulator feedback, search, resampling after failures, or best-of-five selection.
Historical random and rule baselines are separate protocols and results.

## Inputs And Sampling

Generation reads only the instance id and public observation path from the
manifest, and the explicit `allowed_repair_actions` and
`observed_candidate_units` in `public/parameters.json`. Gold actions, hidden
files, instance-specific fault direction or magnitude, and other public files
are not proposal inputs. Missing current values, duplicate pairs or candidate
GUIDs, and invalid sampling ranges stop preflight for the entire run. No pair
is silently removed, and the old gold/target-unit fallback is rejected.

After choosing a pair uniformly, sample its value as follows:

| Parameter | Value distribution |
| --- | --- |
| Outlet or separator temperature | Continuous uniform on the positive portion of current value ±30 K |
| Outlet or separator pressure | Current value × a log-uniform multiplier in [2/3, 2] |
| Reflux ratio | Current value × a log-uniform multiplier in [2/3, 10] |
| Feed stage | Discrete uniform on integers 1 through `number_of_stages`, excluding the current stage |

These ranges use the common fault-generation specification in
`scripts/repair_registry.py` and
`scripts/build_instances/general/discover_fault_specs.py`: temperature offsets
span ±30 K, pressure fault multipliers span [0.5, 1.5], and reflux fault
multipliers span [0.1, 1.5]. The pressure and reflux repair multiplier ranges
are their reciprocals. No individual test fault spec is read.

The existing LLM packets expose `feed_stage` and `number_of_stages`, but not an
explicit list of valid stage numbers. This protocol assumes the candidate
numbers are 1 through that observed count. It does not recover an actual stage
list from XML or hidden data. The existing executor resolves a selected number
against a `StageN` or `Stage_N` name; a missing stage fails ordinary evaluation.
There is no special exclusion of end stages.

## Reproducibility And Execution

The checked-in JSON config fixes test membership, five seeds (0, 1, 2, 3, 4),
sampling bounds, and the existing executor/DWSIM timeouts of 60/180 seconds.
Each seed covers all 100 test tasks once. Sort task ids and pairs by target
kind, GUID, parameter namespace, and parameter name. Derive each task's RNG seed
from SHA256 of `protocol_id + "\n" + seed + "\n" + instance_id`, interpreted as
a big-endian integer, and use Python `random.Random`. RNG state is independent
of task order and output paths. Record the Python version.

Commit the generator and config before formal generation. The generate phase
saves all 500 proposals before evaluation can begin, with the generating Git
commit, generator hash, copied config and its hash, split hash, public input
hashes, proposal hashes, derived seeds, selected current values, and sampling
domains in `generation_manifest.json`. Use a fresh run directory; it is not
overwritten. The evaluate phase verifies the complete saved set before calling
DWSIM and does not redraw values. Existing evaluation reports prevent a second
evaluation of that run. There is no automatic retry or resume mechanism.

Git is optional when running an extracted ZIP. If Git or repository metadata is
unavailable, generation and evaluation record their Git commit as JSON `null`.
The generator, config, split, public-input and proposal hash checks still apply.

```powershell
$RunDir = "results\final_v0_1_5\test\random-one-shot-v1\parameter-selection\run_YYYYMMDD_01"
.\.venv\Scripts\python.exe scripts\baselines\run_random_baseline.py --phase generate --run-dir $RunDir
.\.venv\Scripts\python.exe scripts\baselines\run_random_baseline.py --phase evaluate --run-dir $RunDir
```

Before the formal run, exercise generation and evaluator connection on one dev
task (five seeds, five evaluations) in a temporary directory:

```powershell
$SmokeDir = ".tmp\random_baseline_dev_smoke_YYYYMMDD_01"
.\.venv\Scripts\python.exe scripts\baselines\run_random_baseline.py --phase generate --split-file instances\final_v0_1_5\splits\dev.txt --limit 1 --run-dir $SmokeDir
.\.venv\Scripts\python.exe scripts\baselines\run_random_baseline.py --phase evaluate --run-dir $SmokeDir
```

No API key or LLM provider call is needed. Generation requires no DWSIM;
evaluation requires the benchmark's comparable DWSIM environment. Each seed
writes the existing basic evaluator `aggregate.json`/`aggregate.csv` and
per-instance reports under `seed_<seed>/instance_<hash>/`. Seed aggregates
record both the generating and evaluating Git commits and the evaluation Python
version. Report unsuccessful repairs and execution failures without resampling.
Compute the mean and sample
standard deviation of the five seed success rates; never choose the best seed
or the best repair for an individual task. Manuscript analysis and plots stay
under Git-ignored `.tmp/`; formal run artifacts live under `results/`, whose
existing ignore policy keeps detailed work local unless explicitly curated.

## Recorded Run

The recorded `run_20261008_01` used commit
`fb25281a4e5233b65254eac3ac92fba2a12e833e` for both generation and evaluation.
The five seed success rates have mean **8.6%** and sample standard deviation
**1.14 percentage points**.

| Seed aggregate | Successful repairs | Test tasks |
| --- | --- | --- |
| [Seed 0](../../results/final_v0_1_5/test/random-one-shot-v1/parameter-selection/run_20261008_01/seed_0/aggregate.json) | 8 | 100 |
| [Seed 1](../../results/final_v0_1_5/test/random-one-shot-v1/parameter-selection/run_20261008_01/seed_1/aggregate.json) | 9 | 100 |
| [Seed 2](../../results/final_v0_1_5/test/random-one-shot-v1/parameter-selection/run_20261008_01/seed_2/aggregate.json) | 10 | 100 |
| [Seed 3](../../results/final_v0_1_5/test/random-one-shot-v1/parameter-selection/run_20261008_01/seed_3/aggregate.json) | 9 | 100 |
| [Seed 4](../../results/final_v0_1_5/test/random-one-shot-v1/parameter-selection/run_20261008_01/seed_4/aggregate.json) | 7 | 100 |

Detailed per-instance evaluation reports and simulator flowsheets remain local.
Paths stored inside the published aggregates are repository-relative. References
to the detailed reports and simulator work files identify unpublished local
artifacts; those files are not included in the repository.
