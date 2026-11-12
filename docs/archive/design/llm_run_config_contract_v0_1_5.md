# LLM Run Config Contract v0.1.5

## Summary

This contract records the minimal model-run metadata needed to interpret pilot
benchmark results. It does not freeze provider-specific sampling or reasoning
controls yet. Unspecified generation controls mean provider default.

The goal is reproducibility of benchmark interpretation, not full byte-level
reproduction of stochastic model outputs.

## Minimal Shape

```json
{
  "provider": "gemini",
  "model": "gemini-3.1-pro-preview",
  "prompt_mode": "parameter-selection",
  "api_retry_max": 0,
  "model_output_retry": false,
  "simulator_retry": false,
  "structured_output_mode": "response_mime_type=application/json + response_json_schema",
  "provider_schema_variant": "canonical",
  "temperature": 0.0,
  "thinking": "provider_default",
  "structured_output": true,
  "generation_settings": {
    "temperature": {
      "configurable": true,
      "requested": 0.0,
      "effective": 0.0,
      "availability": "configured",
      "provider_default": false
    }
  },
  "provider_capabilities": {}
}
```

## Field Semantics

- `provider`: model provider family, such as `gemini`, `openai`, or
  `anthropic`.
- `model`: exact model id passed to the provider API. Do not use mutable
  `latest` aliases for recorded benchmark results.
- `prompt_mode`: benchmark prompt condition. v0.1.5 uses
  `parameter-selection` for target+parameter pair selection.
- `temperature`: final primary benchmark requests `0.0` for deterministic
  provider behavior where supported.
- `thinking`: `provider_default` means PSE-RepairBench did not override
  provider reasoning/thinking controls.
- `structured_output`: `true` means the provider was asked to return a JSON
  object matching the benchmark repair-output shape.
- `generation_settings`: provider-control records. `requested=null` means the
  benchmark did not set the option; `provider_default=true` means provider
  default behavior governed it.
- `provider_capabilities`: static capability inventory for the adapter used in
  the run. See `provider_capabilities_v0_1_5.md`.
- `api_retry_max`: provider-call retry limit. v0.1.5 records `0`.
- `model_output_retry`: `false` means malformed or poor model outputs are not
  regenerated.
- `simulator_retry`: `false` means each repair output is applied and rerun once.
- `structured_output_mode`: provider-specific structured output mechanism.
- `provider_schema_variant`: provider-facing schema transformation. Canonical
  local validation is still applied after provider output.
- `provider_call_failure`: API/network/provider request failures are tracked as
  infrastructure failures, separately from model-output and executable-repair
  failures.
- `provider_config_failure`: missing API keys or local provider setup errors are
  tracked before the API call starts.
- `validation_status`: per-instance `llm_metadata.json` records whether the
  provider payload was `valid`, `schema_invalid`, `pending`, `not_reached`, or
  `dry_run`.

## v0.1.5 Gemini Runs

The final primary benchmark runner sets the model id, structured output schema,
and `temperature=0.0`. It does not set `top_p` or thinking/reasoning controls,
so those remain provider defaults.

Recorded v0.1.5 Gemini comparison runs use:

- `gemini-3.1-flash-lite`
- `gemini-3.5-flash`
- `gemini-3.1-pro-preview`

## Future Provider Expansion

OpenAI, Anthropic, and other providers use the same conceptual fields in their
aggregate run metadata. Provider-specific fields may be added under a nested
`provider_options` object, but primary comparison tables should keep the common
fields above.

## v0.1.5 OpenAI Provider

OpenAI runs use the Responses API with Structured Outputs. The provider adapter
reads `OPENAI_API_KEY`, sends the benchmark prompt to `/v1/responses`, and asks
for the same canonical repair-output object with `text.format.type=json_schema`
and `strict=true`.

Candidate OpenAI model tiers for the first comparison are:

- `gpt-5.5`: frontier/high-accuracy tier for the strongest executable repair
  baseline.
- `gpt-5.4-mini`: balanced tier for cost-sensitive but still capable runs.
- `gpt-5.4-nano`: low-cost/high-throughput tier to test whether the benchmark
  separates smaller extraction-oriented models from stronger reasoning models.

The adapter requests `temperature=0.0`, omits `top_p`, and leaves reasoning
controls provider-default.

## v0.1.5 Anthropic Provider

Anthropic runs use the Claude Messages API with Structured Outputs. The provider
adapter reads `CLAUDE_API_KEY`, sends the benchmark prompt to `/v1/messages`,
and asks for the same canonical repair-output object with
`output_config.format.type=json_schema`.

Candidate Anthropic model tiers for comparison are:

- `claude-opus-4-8`: strongest current Claude tier in the official model table.
- `claude-sonnet-4-6`: balanced tier.
- `claude-haiku-4-5-20251001`: fastest / lowest-cost tier.

Claude temperature support is model-dependent. The adapter requests
`temperature=0.0` for models that support it, and otherwise omits temperature
while recording `generation_settings.temperature.availability =
"unsupported_by_model"`.

Claude effort is left provider-default. Current official docs identify Opus 4.8
API default effort as `high`; this is recorded as provider-default behavior, not
as a PSE-RepairBench requested setting.
