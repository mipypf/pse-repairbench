# Contributing

Thank you for helping improve PSE-RepairBench.

## Development Setup

Use Python 3.11 or newer.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

Optional live model runs require API keys in `.env`.

```text
GEMINI_API_KEY=""
OPENAI_API_KEY=""
CLAUDE_API_KEY=""
```

## Checks

Run lightweight checks before opening a change:

```powershell
.\.venv\Scripts\python.exe -m py_compile scripts\evaluate\evaluate_repair_output.py scripts\evaluate\evaluate_release_set.py scripts\llm\run_llm_pilot_batch.py
.\.venv\Scripts\python.exe -m unittest discover -s tests
.\.venv\Scripts\python.exe scripts\maintenance\sanitize_artifact_paths.py --check instances metadata\dwsim_sources docs\dwsim
```

DWSIM-dependent generation and live LLM runs are not required for small code changes unless the changed code touches those execution paths.

## Data Hygiene

Do not commit `.env`, raw downloads, `.tmp` outputs, or local absolute paths. Benchmark instances should use manifest-relative paths and sanitized run artifacts.

## Pull Request Notes

Please mention:

- affected contract or schema, if any
- validation commands run
- whether DWSIM or live model calls were used
- any generated artifacts intentionally included
