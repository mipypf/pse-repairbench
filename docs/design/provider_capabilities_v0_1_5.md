# Provider Capabilities v0.1.5

## Summary

This note records which provider controls and metadata are available to the
v0.1.5 live-model runner. It is an interpretation aid for model-comparison
results, not a request to normalize every provider setting.

This is the only current provider-specific design note. Older provider-specific
pilot notes are archived for provenance and should not override this document.

The final primary benchmark requests structured JSON output and
`temperature=0.0` for every provider. `top_p` and reasoning/thinking controls
remain unspecified provider defaults.

## Provider Naming

Persisted provider ids are canonical and must use these exact lowercase values:

```text
gemini
openai
anthropic
```

Persisted model ids are the provider model ids used for the run, for example
`gemini-3.1-pro-preview`, `gpt-5.5`, or `claude-opus-4-8`.

Result tables should label live model methods as:

```text
<provider>/<model>
```

For example, `anthropic/claude-opus-4-8` means the stored provider id is
`anthropic` and the stored model id is `claude-opus-4-8`. Narrative text may
refer to "Claude" as the model family or product name, but persisted run
metadata must keep `provider: anthropic`.

Official references:

- OpenAI Responses API: https://platform.openai.com/docs/api-reference/responses/create
- OpenAI Structured Outputs: https://platform.openai.com/docs/guides/structured-outputs
- Gemini GenerateContent API: https://ai.google.dev/api/generate-content
- Gemini Structured Outputs: https://ai.google.dev/gemini-api/docs/structured-output
- Claude Messages API: https://platform.claude.com/docs/en/api/messages
- Claude Structured Outputs: https://platform.claude.com/docs/en/build-with-claude/structured-outputs
- Claude Models Overview: https://platform.claude.com/docs/en/about-claude/models/overview

## Capability Matrix

| Capability | Gemini adapter | OpenAI adapter | Anthropic adapter |
| --- | --- | --- | --- |
| `temperature` | Supported by API; final primary benchmark requests `0.0`. | Model-dependent. Requests `0.0` where supported, otherwise records `unsupported_by_model` and omits it. | Model-dependent. Requests `0.0` where supported, otherwise records `unsupported_by_model` and omits it. |
| `top_p` | Supported by API as `topP`; v0.1.5 does not request it. | Supported by Responses API as `top_p`; v0.1.5 does not request it. | Supported by API as `top_p` on compatible models; v0.1.5 does not request it. |
| `max_output_tokens` | Supported by API as `maxOutputTokens`; v0.1.5 does not request it. | Supported by Responses API as `max_output_tokens`; v0.1.5 does not request it. | Required by Messages API as `max_tokens`; v0.1.5 requests `4096`. |
| reasoning/thinking controls | Supported as `thinkingConfig`; v0.1.5 leaves it provider default. | Supported as `reasoning`; v0.1.5 leaves it provider default. | Effort control is provider/model specific; v0.1.5 leaves it provider default. Opus 4.8 default effort is documented as `high`. |
| structured output mode | `response_mime_type=application/json` with `response_json_schema`. | Responses API `text.format.type=json_schema` with `strict=true`. | Messages API `output_config.format.type=json_schema`. |
| response schema strictness | Gemini structured output uses a supported JSON Schema subset; no separate strict flag is set. | `strict=true`; OpenAI supports a subset of JSON Schema under strict mode. | Schema is compiled into a constrained grammar; local canonical validation still runs. |
| retries | Benchmark-controlled; current adapter retry max is `0`. | Benchmark-controlled; current adapter retry max is `0`. | Benchmark-controlled; current adapter retry max is `0`. |
| request id | Not exposed by current Gemini SDK adapter. | Best-effort from response headers such as `x-request-id`. | Best-effort from response headers such as `request-id`. |
| response id | Best-effort from `response_id` / `responseId`. | Response object `id`. | Message object `id`. |
| finish reason | Candidate `finish_reason` / `finishReason` when exposed. | Responses API status and `incomplete_details`; no Chat Completions-style `finish_reason` is assumed. | `stop_reason`. |
| token usage | `usage_metadata` / `usageMetadata` when exposed. | Response `usage`. | Response `usage.input_tokens` / `usage.output_tokens`. |
| latency | Measured by the benchmark adapter. | Measured by the benchmark adapter. | Measured by the benchmark adapter. |
| raw metadata | Partial SDK response metadata is preserved. | Response body fields plus selected transport headers are preserved. | Response body fields plus selected transport headers are preserved. |

## Recording Rules

- `requested=null` means PSE-RepairBench did not set that option.
- `provider_default=true` means the API/provider default governed the value.
- `effective=null` with `availability=not_exposed` means the adapter cannot
  observe the effective value and does not guess it.
- `model_output_retry=false` and `simulator_retry=false` are recorded because
  v0.1.5 measures one provider call and one DWSIM rerun per submitted output.
- `api_retry_max=0` means provider calls are not retried by the benchmark runner.
- With `api_retry_max=0`, transient provider/API/network failures remain in the
  run record as `provider_call_failure`. They are not counted as model semantic
  repair failures.
- Missing API keys or invalid provider setup are recorded as
  `provider_config_failure`, before any provider call is attempted.
- If a provider returns a response but the payload fails benchmark schema
  validation, the provider metadata is still saved before validation and the row
  is classified as `schema_failure`.

## Provider Schema Notes

OpenAI strict Structured Outputs require a stricter schema shape than the
benchmark's canonical JSON Schema. The adapter converts object schemas to
`additionalProperties=false` and marks object properties as required so the
request is accepted by OpenAI strict mode. The canonical evaluator still
validates the resulting JSON against `schemas/repair_output.schema.json` and
`schemas/repair_action.schema.json`.

Claude structured outputs compile the JSON schema into a constrained grammar.
The first request for a new schema may have extra latency while the schema is
compiled and cached by the provider. If a provider-facing schema is too complex,
the row should surface as `provider_call_failure` or `provider_response` while
local canonical validation remains the final judge of accepted repair JSON.
The v0.1.5 Anthropic adapter removes unsupported array `maxItems` from the
provider-facing schema and relaxes `oneOf` allowed-pair enumeration to a broader
single-action schema only; the canonical local validator still requires a single
repair action and the selected target+parameter pair to match the original
allowed-pair schema. Aggregate rows record
`provider_schema_variant=anthropic_relaxed_no_maxItems_no_oneOf`.

## v0.1.5 Measurement Implication

Model comparisons should be interpreted as provider-default generation under a
common structured-output constraint with `temperature=0.0`. If a future result
fixes `top_p`, thinking budget, reasoning effort, or max output tokens, it
should use a new run-config protocol version or explicitly record the setting
change.
