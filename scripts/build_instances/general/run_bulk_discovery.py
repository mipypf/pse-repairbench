#!/usr/bin/env python3
"""Run sensitivity discovery across curated DWSIM sources for v0.1 pilot generation."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parent))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from build_from_fault_spec import build_instance  # noqa: E402
from builder_common import load_json, write_json  # noqa: E402
from discover_fault_specs import discover  # noqa: E402


DEFAULT_MANIFEST = Path("curated_data/dwsim_headless_successes/manifest.csv")
DEFAULT_OUTPUT_ROOT = Path(".tmp/pilot_discovery")
DEFAULT_GENERATED_OUTPUT_ROOT = Path(".tmp/generated_pilot_native_units")
SOURCE_CATEGORY_ORDER = ("distillation", "flash_separator", "reaction_recycle", "other_candidate")
TARGET_FAMILY_ORDER = (
    "terminal_composition",
    "terminal_flow",
    "terminal_temperature",
    "terminal_pressure",
    "product_purity",
    "impurity_max",
    "product_flow",
    "stream_pressure",
    "unknown",
)


def repo_root() -> Path:
    return Path.cwd()


def resolve_repo_path(path: Path) -> Path:
    return path if path.is_absolute() else repo_root() / path


def is_relative_to(path: Path, parent: Path) -> bool:
    try:
        path.resolve().is_relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def ensure_output_root(path: Path, overwrite: bool) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return
    tmp_root = (repo_root() / ".tmp").resolve()
    if not overwrite and not is_relative_to(path, tmp_root):
        raise ValueError(f"output root already exists outside .tmp; pass --overwrite to replace it: {path}")
    shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def source_id_from_path(path: Path) -> str:
    return path.stem.lower().replace("-", "_")


def manifest_sources(manifest: Path, category: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    base = manifest.parent
    with manifest.open(newline="", encoding="utf-8-sig") as handle:
        for row in csv.DictReader(handle):
            row_category = row.get("category") or "other_candidate"
            if category != "all" and row_category != category:
                continue
            if str(row.get("screen_success")).lower() not in {"true", "1", "yes"}:
                continue
            curated_path = row.get("curated_path")
            if not curated_path:
                continue
            source_path = base / curated_path
            rows.append(
                {
                    "source_path": source_path,
                    "source_id": source_id_from_path(Path(curated_path)),
                    "source_name": row.get("original_zip_name") or Path(curated_path).name,
                    "category": row_category,
                    "loaded_objects": row.get("loaded_objects"),
                    "duration_sec": row.get("duration_sec"),
                }
            )
    return rows


def explicit_sources(paths: list[Path]) -> list[dict[str, Any]]:
    return [
        {
            "source_path": path,
            "source_id": source_id_from_path(path),
            "source_name": path.name,
            "category": "other_candidate",
        }
        for path in paths
    ]


def feasible_balanced_sources(feasibility_report: Path, category: str) -> list[dict[str, Any]]:
    report = load_json(feasibility_report)
    rows = report.get("rows") if isinstance(report, dict) else None
    if not isinstance(rows, list):
        raise ValueError(f"feasibility report has no rows array: {feasibility_report}")

    sources: dict[str, dict[str, Any]] = {}
    pair_counts: Counter[str] = Counter()
    for row in rows:
        if not isinstance(row, dict):
            continue
        row_category = row.get("source_category") or "other_candidate"
        if category != "all" and row_category != category:
            continue
        source_id = row.get("source_id")
        source_path = row.get("source_path")
        if not isinstance(source_id, str) or not isinstance(source_path, str):
            continue
        parameter = row.get("parameter") or "unknown"
        target_guid = row.get("target_guid") or "unknown_target"
        pair_counts[source_id] += 1
        sources.setdefault(
            source_id,
            {
                "source_path": resolve_repo_path(Path(source_path)),
                "source_id": source_id,
                "source_name": row.get("source_name") or Path(source_path).name,
                "category": row_category,
                "feasible_pair_count": 0,
                "_pairs": set(),
            },
        )["_pairs"].add(f"{target_guid}::{parameter}")

    grouped: dict[str, list[dict[str, Any]]] = {}
    for source in sources.values():
        source["feasible_pair_count"] = len(source["_pairs"])
        if source["feasible_pair_count"] < 2:
            continue
        source.pop("_pairs", None)
        grouped.setdefault(str(source.get("category") or "other_candidate"), []).append(source)

    for values in grouped.values():
        values.sort(key=lambda item: (-int(item.get("feasible_pair_count") or 0), item["source_id"]))

    categories = [category for category in SOURCE_CATEGORY_ORDER if category in grouped]
    categories.extend(sorted(category for category in grouped if category not in categories))
    balanced: list[dict[str, Any]] = []
    while categories:
        next_categories: list[str] = []
        for category_name in categories:
            values = grouped[category_name]
            if values:
                balanced.append(values.pop(0))
            if values:
                next_categories.append(category_name)
        categories = next_categories
    return balanced


def collect_sources(args: argparse.Namespace) -> list[dict[str, Any]]:
    if args.sources:
        sources = explicit_sources(args.sources)
    elif args.source_selection == "feasible-balanced":
        if args.feasibility_report is None:
            raise ValueError("--source-selection feasible-balanced requires --feasibility-report")
        sources = feasible_balanced_sources(args.feasibility_report, args.category)
    else:
        sources = manifest_sources(args.manifest, args.category)
    if args.start_index:
        sources = sources[args.start_index :]
    if args.limit is not None:
        sources = sources[: args.limit]
    return sources


def parameter_key(candidate: dict[str, Any]) -> str:
    parameter = candidate.get("parameter") if isinstance(candidate.get("parameter"), dict) else {}
    return f"{parameter.get('namespace')}/{parameter.get('name')}"


def target_family(candidate: dict[str, Any]) -> str:
    metric = candidate.get("selected_target_metric")
    if not isinstance(metric, dict):
        return "unknown"
    family = metric.get("family")
    return str(family) if family else "unknown"


def accepted_candidates(report: dict[str, Any], source: dict[str, Any]) -> list[dict[str, Any]]:
    accepted: list[dict[str, Any]] = []
    for candidate in report.get("candidates", []):
        if not isinstance(candidate, dict) or candidate.get("accepted") is not True:
            continue
        spec = candidate.get("fault_spec")
        if not isinstance(spec, dict):
            continue
        fault = spec.get("fault") if isinstance(spec.get("fault"), dict) else {}
        target = fault.get("target") if isinstance(fault.get("target"), dict) else {}
        target_guid = target.get("guid") if isinstance(target.get("guid"), str) else "unknown_target"
        parameter = parameter_key(candidate)
        accepted.append(
            {
                "source_id": source["source_id"],
                "source_category": source.get("category"),
                "source_path": str(source["source_path"]),
                "candidate": candidate,
                "fault_spec": spec,
                "score": candidate.get("score", 0.0),
                "parameter": parameter,
                "target_family": target_family(candidate),
                "target_guid": target_guid,
                "target_pair": f"{source['source_id']}::{target_guid}::{parameter}",
            }
        )
    return accepted


def select_balanced_candidates(
    candidates: list[dict[str, Any]],
    max_instances: int,
    max_per_source: int,
    max_per_parameter: int,
    max_per_target_family: int,
    max_per_target_pair: int,
) -> list[dict[str, Any]]:
    selected: list[dict[str, Any]] = []
    source_counts: Counter[str] = Counter()
    parameter_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    target_pair_counts: Counter[str] = Counter()
    for item in sorted(candidates, key=lambda row: float(row.get("score") or 0.0), reverse=True):
        if len(selected) >= max_instances:
            break
        if source_counts[item["source_id"]] >= max_per_source:
            continue
        if parameter_counts[item["parameter"]] >= max_per_parameter:
            continue
        if family_counts[item["target_family"]] >= max_per_target_family:
            continue
        if target_pair_counts[item["target_pair"]] >= max_per_target_pair:
            continue
        selected.append(item)
        source_counts[item["source_id"]] += 1
        parameter_counts[item["parameter"]] += 1
        family_counts[item["target_family"]] += 1
        target_pair_counts[item["target_pair"]] += 1
    return selected


def sorted_target_families(candidates: list[dict[str, Any]]) -> list[str]:
    present = {str(item.get("target_family") or "unknown") for item in candidates}
    families = [family for family in TARGET_FAMILY_ORDER if family in present]
    families.extend(sorted(present - set(families)))
    return families


def candidate_allowed(
    item: dict[str, Any],
    source_counts: Counter[str],
    parameter_counts: Counter[str],
    family_counts: Counter[str],
    target_pair_counts: Counter[str],
    max_per_source: int,
    max_per_parameter: int,
    max_per_target_family: int,
    max_per_target_pair: int,
) -> bool:
    return (
        source_counts[item["source_id"]] < max_per_source
        and parameter_counts[item["parameter"]] < max_per_parameter
        and family_counts[item["target_family"]] < max_per_target_family
        and target_pair_counts[item["target_pair"]] < max_per_target_pair
    )


def select_target_family_balanced_candidates(
    candidates: list[dict[str, Any]],
    max_instances: int,
    max_per_source: int,
    max_per_parameter: int,
    max_per_target_family: int,
    max_per_target_pair: int,
) -> list[dict[str, Any]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in candidates:
        grouped.setdefault(str(item.get("target_family") or "unknown"), []).append(item)
    for values in grouped.values():
        values.sort(key=lambda row: float(row.get("score") or 0.0), reverse=True)

    families = sorted_target_families(candidates)
    selected: list[dict[str, Any]] = []
    selected_ids: set[int] = set()
    source_counts: Counter[str] = Counter()
    parameter_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    target_pair_counts: Counter[str] = Counter()

    while len(selected) < max_instances:
        progressed = False
        for family in families:
            if len(selected) >= max_instances:
                break
            for item in grouped.get(family, []):
                if id(item) in selected_ids:
                    continue
                if not candidate_allowed(
                    item,
                    source_counts,
                    parameter_counts,
                    family_counts,
                    target_pair_counts,
                    max_per_source,
                    max_per_parameter,
                    max_per_target_family,
                    max_per_target_pair,
                ):
                    continue
                selected.append(item)
                selected_ids.add(id(item))
                source_counts[item["source_id"]] += 1
                parameter_counts[item["parameter"]] += 1
                family_counts[item["target_family"]] += 1
                target_pair_counts[item["target_pair"]] += 1
                progressed = True
                break
        if not progressed:
            break
    return selected


def select_candidates(args: argparse.Namespace, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if args.selection_strategy == "target-family-balanced":
        return select_target_family_balanced_candidates(
            candidates,
            args.max_instances,
            args.max_per_source,
            args.max_per_parameter,
            args.max_per_target_family,
            args.max_per_target_pair,
        )
    return select_balanced_candidates(
        candidates,
        args.max_instances,
        args.max_per_source,
        args.max_per_parameter,
        args.max_per_target_family,
        args.max_per_target_pair,
    )


def candidate_row(item: dict[str, Any]) -> dict[str, Any]:
    spec = item["fault_spec"]
    return {
        "instance_id": spec.get("instance_id"),
        "source_id": item["source_id"],
        "source_category": item.get("source_category"),
        "source_path": item["source_path"],
        "parameter": item["parameter"],
        "target_guid": item["target_guid"],
        "target_pair": item["target_pair"],
        "target_family": item["target_family"],
        "score": item["score"],
        "built": False,
        "instance_path": None,
        "error": None,
    }


def candidate_groups(candidates: list[dict[str, Any]]) -> tuple[dict[str, list[dict[str, Any]]], list[str]]:
    grouped: dict[str, list[dict[str, Any]]] = {}
    for item in candidates:
        grouped.setdefault(str(item.get("target_family") or "unknown"), []).append(item)
    for values in grouped.values():
        values.sort(key=lambda row: float(row.get("score") or 0.0), reverse=True)
    return grouped, sorted_target_families(candidates)


def pick_next_score_candidate(
    candidates: list[dict[str, Any]],
    attempted_ids: set[int],
    source_counts: Counter[str],
    parameter_counts: Counter[str],
    family_counts: Counter[str],
    target_pair_counts: Counter[str],
    args: argparse.Namespace,
) -> dict[str, Any] | None:
    for item in sorted(candidates, key=lambda row: float(row.get("score") or 0.0), reverse=True):
        if id(item) in attempted_ids:
            continue
        if candidate_allowed(
            item,
            source_counts,
            parameter_counts,
            family_counts,
            target_pair_counts,
            args.max_per_source,
            args.max_per_parameter,
            args.max_per_target_family,
            args.max_per_target_pair,
        ):
            return item
    return None


def pick_next_family_candidate(
    grouped: dict[str, list[dict[str, Any]]],
    families: list[str],
    family_index: int,
    attempted_ids: set[int],
    source_counts: Counter[str],
    parameter_counts: Counter[str],
    family_counts: Counter[str],
    target_pair_counts: Counter[str],
    args: argparse.Namespace,
) -> tuple[dict[str, Any] | None, int]:
    if not families:
        return None, family_index
    for offset in range(len(families)):
        index = (family_index + offset) % len(families)
        family = families[index]
        for item in grouped.get(family, []):
            if id(item) in attempted_ids:
                continue
            if not candidate_allowed(
                item,
                source_counts,
                parameter_counts,
                family_counts,
                target_pair_counts,
                args.max_per_source,
                args.max_per_parameter,
                args.max_per_target_family,
                args.max_per_target_pair,
            ):
                continue
            return item, (index + 1) % len(families)
    return None, family_index


def increment_selection_counts(
    item: dict[str, Any],
    source_counts: Counter[str],
    parameter_counts: Counter[str],
    family_counts: Counter[str],
    target_pair_counts: Counter[str],
) -> None:
    source_counts[item["source_id"]] += 1
    parameter_counts[item["parameter"]] += 1
    family_counts[item["target_family"]] += 1
    target_pair_counts[item["target_pair"]] += 1


def build_selected_with_backfill(args: argparse.Namespace, candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    selected_rows: list[dict[str, Any]] = []
    attempted_ids: set[int] = set()
    source_counts: Counter[str] = Counter()
    parameter_counts: Counter[str] = Counter()
    family_counts: Counter[str] = Counter()
    target_pair_counts: Counter[str] = Counter()
    grouped, families = candidate_groups(candidates)
    family_index = 0
    built_count = 0

    while built_count < args.max_instances:
        if args.selection_strategy == "target-family-balanced":
            item, family_index = pick_next_family_candidate(
                grouped,
                families,
                family_index,
                attempted_ids,
                source_counts,
                parameter_counts,
                family_counts,
                target_pair_counts,
                args,
            )
        else:
            item = pick_next_score_candidate(
                candidates,
                attempted_ids,
                source_counts,
                parameter_counts,
                family_counts,
                target_pair_counts,
                args,
            )
        if item is None:
            break
        attempted_ids.add(id(item))
        row = candidate_row(item)
        try:
            instance_path = build_instance(item["fault_spec"], args.generated_output_root, overwrite=True)
            row["built"] = True
            row["instance_path"] = str(instance_path)
            increment_selection_counts(item, source_counts, parameter_counts, family_counts, target_pair_counts)
            built_count += 1
        except Exception as exc:  # noqa: BLE001
            row["error"] = str(exc)
        selected_rows.append(row)
    return selected_rows


def reused_discovery_reports(reuse_root: Path) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    if not reuse_root.exists():
        raise FileNotFoundError(f"reuse discovery root does not exist: {reuse_root}")

    source_reports: list[dict[str, Any]] = []
    all_accepted: list[dict[str, Any]] = []
    source_errors: list[dict[str, Any]] = []
    successful_source_ids: set[str] = set()
    aggregate_path = reuse_root / "bulk_discovery_aggregate.json"
    if aggregate_path.exists():
        aggregate = load_json(aggregate_path)
        if isinstance(aggregate, dict) and isinstance(aggregate.get("source_errors"), list):
            source_errors = [item for item in aggregate["source_errors"] if isinstance(item, dict)]

    for report_path in sorted(reuse_root.rglob("sensitivity_report.json")):
        report = load_json(report_path)
        if not isinstance(report, dict):
            continue
        source_id = str(report.get("source_id") or report_path.parent.name)
        successful_source_ids.add(source_id)
        source_path = report.get("source_flowsheet") or report.get("source_path") or ""
        source = {
            "source_id": source_id,
            "source_category": report.get("source_category"),
            "category": report.get("source_category"),
            "source_path": source_path,
        }
        source_reports.append(
            {
                "source_id": source_id,
                "source_category": report.get("source_category"),
                "source_path": str(source_path),
                "report_path": str(report_path),
                "candidate_count": report.get("candidate_count"),
                "accepted_count": report.get("accepted_count"),
                "built_count": len(report.get("built_instances", [])),
            }
        )
        all_accepted.extend(accepted_candidates(report, source))
    if successful_source_ids:
        source_errors = [
            item
            for item in source_errors
            if str(item.get("source_id") or "") not in successful_source_ids
        ]
    return source_reports, all_accepted, source_errors


def write_csv(path: Path, rows: list[dict[str, Any]]) -> None:
    fields = [
        "instance_id",
        "source_id",
        "source_category",
        "source_path",
        "parameter",
        "target_guid",
        "target_pair",
        "target_family",
        "score",
        "built",
        "instance_path",
        "error",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


def row_distribution(rows: list[dict[str, Any]]) -> dict[str, dict[str, int]]:
    return {
        "parameter": dict(Counter(row["parameter"] for row in rows)),
        "target_family": dict(Counter(row["target_family"] for row in rows)),
        "source": dict(Counter(row["source_id"] for row in rows)),
        "source_category": dict(Counter(str(row.get("source_category") or "unknown") for row in rows)),
        "target_pair": dict(Counter(row["target_pair"] for row in rows)),
    }


def run_source_discovery(args: argparse.Namespace, source: dict[str, Any]) -> dict[str, Any]:
    output_dir = args.output_root / source["source_id"]
    discovery_args = argparse.Namespace(
        source_flowsheet=source["source_path"],
        output_dir=output_dir,
        source_id=source["source_id"],
        source_name=source["source_name"],
        source_category=source.get("category"),
        write_specs=True,
        build_top_k=0,
        overwrite=args.overwrite,
    )
    report, _specs = discover(discovery_args)
    return report


def run_bulk(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    if args.min_selected < 0:
        raise ValueError("--min-selected must be non-negative")
    exclude_instance_ids = {str(value) for value in getattr(args, "exclude_instance_id", [])}
    args.manifest = resolve_repo_path(args.manifest)
    if args.feasibility_report is not None:
        args.feasibility_report = resolve_repo_path(args.feasibility_report)
    if args.reuse_discovery_root is not None:
        args.reuse_discovery_root = resolve_repo_path(args.reuse_discovery_root)
    args.output_root = resolve_repo_path(args.output_root)
    args.generated_output_root = resolve_repo_path(args.generated_output_root)
    args.sources = [resolve_repo_path(path) for path in args.sources]

    if args.reuse_discovery_root is not None and args.output_root.resolve() == args.reuse_discovery_root.resolve():
        args.output_root.mkdir(parents=True, exist_ok=True)
    else:
        ensure_output_root(args.output_root, args.overwrite)
    if args.build_selected:
        ensure_output_root(args.generated_output_root, args.overwrite)

    source_reports: list[dict[str, Any]] = []
    all_accepted: list[dict[str, Any]] = []
    source_errors: list[dict[str, Any]] = []

    if args.reuse_discovery_root is not None:
        source_reports, all_accepted, source_errors = reused_discovery_reports(args.reuse_discovery_root)
        sources = source_reports
    else:
        sources = collect_sources(args)
        for source in sources:
            try:
                report = run_source_discovery(args, source)
                source_reports.append(
                    {
                        "source_id": source["source_id"],
                        "source_category": source.get("category"),
                        "source_path": str(source["source_path"]),
                        "report_path": str(args.output_root / source["source_id"] / "sensitivity_report.json"),
                        "candidate_count": report.get("candidate_count"),
                        "accepted_count": report.get("accepted_count"),
                        "built_count": len(report.get("built_instances", [])),
                    }
                )
                all_accepted.extend(accepted_candidates(report, source))
            except Exception as exc:  # noqa: BLE001
                source_errors.append(
                    {
                        "source_id": source["source_id"],
                        "source_category": source.get("category"),
                        "source_path": str(source["source_path"]),
                        "error": str(exc),
                    }
                )

    if exclude_instance_ids:
        all_accepted = [
            item
            for item in all_accepted
            if str(item.get("fault_spec", {}).get("instance_id")) not in exclude_instance_ids
        ]

    if args.build_selected:
        selected_rows = build_selected_with_backfill(args, all_accepted)
    else:
        selected_rows = [candidate_row(item) for item in select_candidates(args, all_accepted)]

    built_count = sum(1 for row in selected_rows if row["built"] is True)
    build_error_count = sum(1 for row in selected_rows if row["error"])
    built_rows = [row for row in selected_rows if row["built"] is True]
    distribution_rows = built_rows if args.build_selected else selected_rows
    attempted_count = len(selected_rows) if args.build_selected else None
    selected_count = built_count if args.build_selected else len(selected_rows)
    source_count = len(source_reports) + len(source_errors) if args.reuse_discovery_root is not None else len(sources)
    aggregate = {
        "source_count": source_count,
        "source_success_count": len(source_reports),
        "source_error_count": len(source_errors),
        "accepted_candidate_count": len(all_accepted),
        "selected_count": selected_count,
        "attempted_count": attempted_count,
        "built_count": built_count,
        "build_error_count": build_error_count,
        "max_instances": args.max_instances,
        "selection_limits": {
            "source_selection": args.source_selection,
            "selection_strategy": args.selection_strategy,
            "feasibility_report": str(args.feasibility_report) if args.feasibility_report else None,
            "reuse_discovery_root": str(args.reuse_discovery_root) if args.reuse_discovery_root else None,
            "min_selected": args.min_selected,
            "max_per_source": args.max_per_source,
            "max_per_parameter": args.max_per_parameter,
            "max_per_target_family": args.max_per_target_family,
            "max_per_target_pair": args.max_per_target_pair,
            "exclude_instance_ids": sorted(exclude_instance_ids),
        },
        "distribution": row_distribution(distribution_rows),
        "attempted_distribution": row_distribution(selected_rows) if args.build_selected else None,
        "sources": source_reports,
        "source_errors": source_errors,
        "selected": selected_rows,
    }
    write_json(args.output_root / "bulk_discovery_aggregate.json", aggregate)
    write_csv(args.output_root / "selected_instances.csv", selected_rows)

    exit_code = 0
    if source_errors and not args.allow_source_errors:
        exit_code = 1
    if args.build_selected:
        if built_count < args.min_selected:
            exit_code = 1
    return aggregate, exit_code


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, type=Path)
    parser.add_argument("--category", default="all", help="manifest category to scan, or 'all'")
    parser.add_argument("--sources", nargs="*", default=[], type=Path)
    parser.add_argument("--source-selection", choices=("manifest", "feasible-balanced"), default="manifest")
    parser.add_argument("--selection-strategy", choices=("score", "target-family-balanced"), default="score")
    parser.add_argument("--feasibility-report", type=Path)
    parser.add_argument("--reuse-discovery-root", type=Path)
    parser.add_argument("--start-index", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--output-root", default=DEFAULT_OUTPUT_ROOT, type=Path)
    parser.add_argument("--generated-output-root", default=DEFAULT_GENERATED_OUTPUT_ROOT, type=Path)
    parser.add_argument("--max-instances", type=int, default=30)
    parser.add_argument("--min-selected", type=int, default=1, help="minimum selected candidates required when --build-selected is used")
    parser.add_argument("--max-per-source", type=int, default=2)
    parser.add_argument("--max-per-parameter", type=int, default=15)
    parser.add_argument("--max-per-target-family", type=int, default=15)
    parser.add_argument("--max-per-target-pair", type=int, default=1)
    parser.add_argument(
        "--exclude-instance-id",
        action="append",
        default=[],
        help="accepted candidate instance_id to skip during selection; repeat to exclude multiple candidates",
    )
    parser.add_argument("--build-selected", action="store_true")
    parser.add_argument("--allow-source-errors", action="store_true")
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    try:
        aggregate, exit_code = run_bulk(args)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    attempted = aggregate.get("attempted_count")
    attempted_text = f" attempted={attempted}" if attempted is not None else ""
    print(
        "Bulk discovery complete: "
        f"sources={aggregate['source_count']} "
        f"accepted={aggregate['accepted_candidate_count']} "
        f"selected={aggregate['selected_count']}{attempted_text} built={aggregate['built_count']}"
    )
    print(f"Wrote aggregate to {args.output_root / 'bulk_discovery_aggregate.json'}")
    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
