# Terminal Native Units 40 Hidden-Mock Eval Note

Date: 2026-06-03

Command:

```powershell
.\.venv\Scripts\python.exe scripts\evaluate\evaluate_release_set.py --instances .tmp\generated_terminal_native_units_40 --mode hidden-mock --work-dir .tmp\terminal_native_units_40_hidden_mock_eval --require-success
```

Result:

- 40 instances evaluated.
- 38 executable successes.
- 2 failures.
- `aggregate.json` and `aggregate.csv` were written under `.tmp\terminal_native_units_40_hidden_mock_eval`.

Clean 40 generation provenance:

- bulk discovery aggregate: selected=40, attempted=41, built=40, build_error_count=1.

Observation:

Build success does not guarantee evaluator success. The builder can create the instance package, but the evaluator re-applies the hidden mock repair to the faulty flowsheet, reruns DWSIM metrics, and checks the success criterion.

Failure types seen in this run:

- `003_dehydration_of_reservoir_fluid_using_methanol_c_02_outlet_temperature_001`: repair action matched the gold action exactly and DWSIM ran successfully, but the target temperature missed the max threshold (`331.104 > 326.734`). This suggests a reproducibility or threshold-margin issue after rebuild/re-evaluation.
- `041_production_of_sulfur_trioxide_from_sulfur_dioxide_heater_a_outlet_temperature_013`: repair action application succeeded, but DWSIM metrics failed (`error_stage=dwsim_metrics`, return code `3221226505`).

Research note:

This supports a two-stage validation design: discovery/build finds plausible repair instances, then hidden-mock evaluation filters out instances that are not reproducibly repairable under the final evaluator path.
