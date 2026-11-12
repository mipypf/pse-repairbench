"""Shared DWSIM run-artifact success contract."""

from __future__ import annotations

from typing import Any


def is_successful_dwsim_run(run: Any) -> bool:
    return bool(
        isinstance(run, dict)
        and run.get("status") == "success"
        and run.get("success") is True
        and run.get("solved_after") is True
        and run.get("exception_count") == 0
    )
