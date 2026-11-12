# OpenAI Provider Notes v0.1.5

## Summary

This note records the first OpenAI provider integration target for the
v0.1.5 pilot benchmark. It is implementation guidance, not a frozen final
measurement protocol.

## API

- Provider id: `openai`
- API key env var: `OPENAI_API_KEY`
- Endpoint: `POST https://api.openai.com/v1/responses`
- Structured output: Responses API `text.format.type=json_schema`,
  `text.format.strict=true`
- Temperature/reasoning controls: omitted for v0.1.5, recorded as provider
  default

The adapter converts the benchmark repair-output JSON Schema into the strict
schema shape expected by OpenAI Structured Outputs. The benchmark still
validates the returned payload with the local `repair_output` and
`repair_action` schemas before executor/evaluator work begins.

OpenAI strict Structured Outputs require object schemas to list all properties
as required and reject additional properties. As a result, provider-facing
OpenAI schemas may require fields such as `target.tag` and action-level
`rationale` that are optional in the canonical benchmark schema. This is
recorded as a provider schema condition; evaluator scoring remains based on the
local canonical schemas, executor behavior, executable success, and gold
proximity diagnostics.

## Initial Model Set

Use these three tiers for the first OpenAI comparison against the balanced
terminal-native-unit pilot:

- `gpt-5.5`: frontier/high-accuracy tier.
- `gpt-5.4-mini`: balanced cost/performance tier.
- `gpt-5.4-nano`: low-cost/high-throughput tier.

The first live run should start with `gpt-5.4-mini` as a smoke test, then run
the full three-model set if schema, executor, and evaluator stages are stable.

## Example Commands

```powershell
.\.venv\Scripts\python.exe scripts\llm\run_llm_pilot_batch.py `
  --provider openai `
  --model gpt-5.4-mini `
  --instances .tmp\generated_terminal_native_units_balanced `
  --prompt-mode parameter-selection `
  --work-dir .tmp\live_runs\openai_terminal_native_units_balanced_gpt_5_4_mini `
  --dry-run-sanitize
```

```powershell
.\.venv\Scripts\python.exe scripts\llm\run_llm_pilot_batch.py `
  --provider openai `
  --model gpt-5.4-mini `
  --instances .tmp\generated_terminal_native_units_balanced `
  --prompt-mode parameter-selection `
  --work-dir .tmp\live_runs\openai_terminal_native_units_balanced_gpt_5_4_mini
```
