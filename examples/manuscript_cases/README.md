# Manuscript Case Examples

These are two saved model responses discussed in the manuscript. The JSON files
are unchanged copies of the original outputs; they are selected examples, not a
complete experiment run. Values in the responses use the action units shown in
each JSON (Pa or K). The JSON copies retain the data license in
[DATA_LICENSE.md](../../DATA_LICENSE.md).

## Dehumidification: Pressure Repair Success

- Response: [GPT-5.5](dehumidification_pressure_success_gpt-5.5.json)
- Task: `003_a_simple_de_humidification_system_compressor_outlet_pressure_008`
- Original output: `results/final_v0_1_5/test/gpt-5.5/parameter-selection/run_20260609_01/instance_aae196dbe1af/openai_llm_output.json`
- Published result: [GPT-5.5 aggregate](../../results/final_v0_1_5/test/gpt-5.5/parameter-selection/run_20260609_01_backfilled_provider_520/aggregate.json), identified by the task ID in `rows`.
- Connectivity and faulty-state observations: [task data](../../instances/final_v0_1_5/candidate_pool/003_a_simple_de_humidification_system_compressor_outlet_pressure_008/public/).

The proposed compressor outlet pressure was 316249.969552 Pa. The saved target
pressure was 316249.969552 Pa against an upper threshold of
316249.96955227474 Pa; `executable_success` is `true`.

## Refrigeration: Temperature Repair Failure

- Response: [Claude Haiku 4.5](refrigeration_temperature_failure_claude-haiku-4.5.json)
- Task: `001_4_step_refrigeration_cycle_with_propylene_ethylene_methane_and_nitrogen_ht_01_outlet_temperature_001`
- Original output: `results/final_v0_1_5/test/claude-haiku-4-5-20251001/parameter-selection/run_20260609_01/instance_c2234dfd37a5/anthropic_llm_output.json`
- Published result: [Claude Haiku aggregate](../../results/final_v0_1_5/test/claude-haiku-4-5-20251001/parameter-selection/run_20260609_01/aggregate.json), identified by the task ID in `rows`.
- Connectivity and faulty-state observations: [task data](../../instances/final_v0_1_5/candidate_pool/001_4_step_refrigeration_cycle_with_propylene_ethylene_methane_and_nitrogen_ht_01_outlet_temperature_001/public/).

The response claims CL-02 is immediately upstream of M-24 and proposes 83.15 K.
The saved topology instead connects HT-01 to M-24 and CL-02 to M-1. The saved
target temperature was 48.1759999450952 K against a lower threshold of
69.17599999508403 K; `executable_success` is `false`.
