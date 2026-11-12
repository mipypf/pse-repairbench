#!/usr/bin/env python3
"""Merge provider-call backfill rows into a final aggregate.

This script only replaces rows whose base failure_type is
``provider_call_failure``. It does not retry or alter model-output,
schema, executor, DWSIM, or target failures.
"""

from __future__ import annotations

import argparse
import csv
import json
import statistics
from pathlib import Path
from typing import Any


def load_json(path: Path) -> Any:
    with path.open("r", encoding="utf-8") as handle:
        return json.load(handle)


def write_json(path: Path, payload: Any) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames: list[str] = []
    for row in rows:
        for key in row:
            if key not in fieldnames:
                fieldnames.append(key)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fieldnames})


def count_by(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    values = sorted({row.get(key) for row in rows if row.get(key)})
    return {str(value): sum(1 for row in rows if row.get(key) == value) for value in values}


def failure_counts(rows: list[dict[str, Any]]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        failure = row.get("failure_type")
        if isinstance(failure, str) and failure and failure != "dry_run_sanitize":
            counts[failure] = counts.get(failure, 0) + 1
    return counts


def usage_summary(rows: list[dict[str, Any]]) -> dict[str, Any]:
    latencies = [row.get("provider_latency_sec") for row in rows]
    numeric_latencies = [value for value in latencies if isinstance(value, int | float)]
    summary: dict[str, Any] = {
        "provider_latency_sec_count": len(numeric_latencies),
        "provider_latency_sec_sum": sum(numeric_latencies) if numeric_latencies else None,
        "provider_latency_sec_mean": statistics.mean(numeric_latencies) if numeric_latencies else None,
        "provider_latency_sec_median": statistics.median(numeric_latencies) if numeric_latencies else None,
        "provider_usage_input_tokens_total": sum(row.get("provider_usage_input_tokens") or 0 for row in rows),
        "provider_usage_output_tokens_total": sum(row.get("provider_usage_output_tokens") or 0 for row in rows),
        "provider_usage_total_tokens_total": sum(row.get("provider_usage_total_tokens") or 0 for row in rows),
        "provider_usage_total_tokens_missing_count": sum(
            1 for row in rows if row.get("provider_usage_total_tokens") in (None, "")
        ),
    }
    if numeric_latencies:
        ordered = sorted(numeric_latencies)
        p95_index = min(len(ordered) - 1, int(0.95 * (len(ordered) - 1)))
        summary["provider_latency_sec_p95"] = ordered[p95_index]
    else:
        summary["provider_latency_sec_p95"] = None
    return summary


def aggregate_like(base: dict[str, Any], rows: list[dict[str, Any]], backfill_meta: dict[str, Any]) -> dict[str, Any]:
    summary = dict(base)
    summary["rows"] = rows
    summary["instance_count"] = len(rows)
    summary["pipeline_success_count"] = sum(1 for row in rows if row.get("pipeline_success") is True)
    summary["executable_success_count"] = sum(1 for row in rows if row.get("executable_success") is True)
    summary["exec_success_with_gold_mismatch_count"] = sum(
        1
        for row in rows
        if row.get("executable_success") is True and row.get("gold_proximity_type") not in {None, "gold_exact"}
    )
    summary["wrong_parameter_success_count"] = sum(
        1 for row in rows if row.get("gold_mismatch_success_type") == "wrong_parameter_success"
    )
    summary["failure_counts"] = failure_counts(rows)
    summary["preflight_counts"] = count_by(rows, "preflight_failure")
    summary["gold_proximity_type_counts"] = count_by(rows, "gold_proximity_type")
    summary["gold_mismatch_success_type_counts"] = count_by(rows, "gold_mismatch_success_type")
    summary["selected_action_pair_counts"] = count_by(rows, "selected_action_pair")
    summary["target_family_counts"] = count_by(rows, "target_family")
    summary["source_category_counts"] = count_by(rows, "source_category")
    summary["usage_summary"] = usage_summary(rows)
    summary["provider_call_backfill"] = backfill_meta
    return summary


def compatible(base: dict[str, Any], backfill: dict[str, Any]) -> bool:
    keys = ["provider", "model", "prompt_mode", "dataset_split_id"]
    return all(base.get(key) == backfill.get(key) for key in keys)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-aggregate", required=True, type=Path)
    parser.add_argument("--backfill-aggregate", action="append", required=True, type=Path)
    parser.add_argument("--output-json", required=True, type=Path)
    parser.add_argument("--output-csv", type=Path)
    parser.add_argument("--failure-type", default="provider_call_failure")
    parser.add_argument("--max-additional-attempts", default=2, type=int)
    parser.add_argument("--require-resolved", action="store_true")
    args = parser.parse_args()

    base = load_json(args.base_aggregate)
    base_rows = base.get("rows")
    if not isinstance(base_rows, list):
        raise SystemExit("Base aggregate does not contain a rows list")

    target_ids = {
        row.get("instance_id")
        for row in base_rows
        if row.get("failure_type") == args.failure_type and isinstance(row.get("instance_id"), str)
    }
    replacements: dict[str, tuple[dict[str, Any], Path, int]] = {}
    attempts_by_id: dict[str, int] = {str(instance_id): 0 for instance_id in target_ids}

    for aggregate_path in args.backfill_aggregate:
        backfill = load_json(aggregate_path)
        if not compatible(base, backfill):
            raise SystemExit(f"Backfill aggregate is not config-compatible with base: {aggregate_path}")
        rows = backfill.get("rows")
        if not isinstance(rows, list):
            raise SystemExit(f"Backfill aggregate does not contain a rows list: {aggregate_path}")
        for row in rows:
            instance_id = row.get("instance_id")
            if not isinstance(instance_id, str) or instance_id not in target_ids:
                continue
            attempts_by_id[instance_id] = attempts_by_id.get(instance_id, 0) + 1
            attempt = attempts_by_id[instance_id]
            if attempt > args.max_additional_attempts:
                continue
            current = replacements.get(instance_id)
            current_failure = current[0].get("failure_type") if current else args.failure_type
            if current is None or current_failure == args.failure_type:
                replacements[instance_id] = (row, aggregate_path, attempt)

    rows_out: list[dict[str, Any]] = []
    backfilled_ids: list[str] = []
    unresolved_ids: list[str] = []
    for row in base_rows:
        instance_id = row.get("instance_id")
        if instance_id in replacements:
            replacement, source, attempt = replacements[str(instance_id)]
            new_row = dict(replacement)
            new_row["provider_call_backfilled"] = True
            new_row["provider_call_backfill_attempt"] = attempt
            new_row["provider_call_backfill_source_aggregate"] = str(source)
            new_row["provider_call_backfill_replaced_failure_type"] = row.get("failure_type")
            rows_out.append(new_row)
            backfilled_ids.append(str(instance_id))
            if new_row.get("failure_type") == args.failure_type:
                unresolved_ids.append(str(instance_id))
        else:
            rows_out.append(dict(row))
            if row.get("failure_type") == args.failure_type:
                unresolved_ids.append(str(instance_id))

    if args.require_resolved and unresolved_ids:
        raise SystemExit(f"Unresolved {args.failure_type} rows: {', '.join(unresolved_ids)}")

    meta = {
        "policy": "provider_call_failure_only",
        "max_additional_attempts": args.max_additional_attempts,
        "base_aggregate": str(args.base_aggregate),
        "backfill_aggregates": [str(path) for path in args.backfill_aggregate],
        "raw_provider_call_failure_count": len(target_ids),
        "backfilled_provider_call_failure_count": len(backfilled_ids),
        "unresolved_provider_call_failure_count": len(unresolved_ids),
        "backfilled_instance_ids": sorted(backfilled_ids),
        "unresolved_instance_ids": sorted(unresolved_ids),
    }
    merged = aggregate_like(base, rows_out, meta)
    write_json(args.output_json, merged)
    write_csv(args.output_csv or args.output_json.with_suffix(".csv"), rows_out)
    print(f"Wrote merged aggregate JSON to {args.output_json}")
    print(f"Backfilled {len(backfilled_ids)} row(s); unresolved {len(unresolved_ids)} row(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
