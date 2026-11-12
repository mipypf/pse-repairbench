# v0.1 Localized Oracle-Parameter Baseline

Date: 2026-05-29

This baseline records a live Gemini run on the localized/oracle-parameter
prompt condition. In this condition, each prompt tells the model which
parameter family to adjust, and the Gemini response schema fixes that
parameter.

## Run Configuration

- Model: `gemini-2.5-flash`
- Prompt mode: localized/oracle-parameter
- Dataset: 2 generated v0.1 pilot instances under `.tmp/generated_pilot_instances`
- Output location: raw model outputs and evaluator reports were written under
  `.tmp/live_runs/gemini_pilot` and are intentionally untracked
- API mode: live network/API run

## Aggregate Result

- Instance count: 2
- Pipeline success: 2/2
- Executable target success: 1/2
- Failure counts: `target_failure=1`

## Instance Notes

- `002_air_liquefaction_using_linde_single_column_system_dc_01_feed_stage_002`
  reached executable target success. Gemini selected
  `column_configuration/feed_stage = 4`; the hidden gold value is `3`, so gold
  value proximity was imperfect but the repaired run met the target.
- `002_air_liquefaction_using_linde_single_column_system_dc_01_reflux_ratio_001`
  completed schema validation, execution, and DWSIM rerun, but missed the
  target. Gemini selected `column_specification/reflux_ratio = 1.5`, far from
  the hidden gold value.

This result is a small baseline, not a final measurement. It establishes that
the end-to-end localized/oracle-parameter pipeline is operational and that the
first live Gemini smoke run achieved executable success on 1 of 2 generated
pilot instances.
