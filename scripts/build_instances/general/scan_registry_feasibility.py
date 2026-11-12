#!/usr/bin/env python3
"""Scan curated DWSIM sources for executor-backed v0.1.5 repair pairs."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from collections import Counter
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from builder_common import graphic_tags, read_dwxmz_xml, read_inner_dwsim_from_curated_zip, text_of, write_json  # noqa: E402
from repair_registry import REGISTRY, entry_supports_unit_type, pair_from_target_and_entry, required_state_mismatches  # noqa: E402


DEFAULT_MANIFEST = Path("curated_data/dwsim_headless_successes/manifest.csv")
DEFAULT_OUTPUT_DIR = Path(".tmp/native_unit_feasibility")


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


def ensure_output_dir(path: Path, overwrite: bool) -> None:
    if not path.exists():
        path.mkdir(parents=True, exist_ok=True)
        return
    tmp_root = (repo_root() / ".tmp").resolve()
    if not overwrite and not is_relative_to(path, tmp_root):
        raise ValueError(f"output directory already exists outside .tmp; pass --overwrite to replace it: {path}")
    shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def source_id_from_path(path: Path) -> str:
    return path.stem.lower().replace("-", "_")


def manifest_sources(manifest: Path, category: str) -> list[dict[str, Any]]:
    sources: list[dict[str, Any]] = []
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
            sources.append(
                {
                    "source_path": base / curated_path,
                    "source_id": source_id_from_path(Path(curated_path)),
                    "source_name": row.get("original_zip_name") or Path(curated_path).name,
                    "source_category": row_category,
                }
            )
    return sources


def feed_stage_supported(obj: Any) -> bool:
    material_streams = obj.find("MaterialStreams")
    if material_streams is None:
        return False
    feed_streams = [stream for stream in material_streams if text_of(stream, "StreamBehavior") == "Feed"]
    return len(feed_streams) == 1


def supported_pairs(flowsheet: Path) -> list[dict[str, Any]]:
    tree, _xml_entry, _entries = read_dwxmz_xml(flowsheet)
    root = tree.getroot()
    tags = graphic_tags(root)
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        return []
    pairs: list[dict[str, Any]] = []
    for obj in simulation_objects:
        unit_type = text_of(obj, "Type")
        guid = text_of(obj, "Name")
        if not guid:
            continue
        target = {
            "kind": "unit_operation",
            "guid": guid,
            "tag": tags.get(guid, ""),
            "type": unit_type,
        }
        for entry in REGISTRY:
            if not entry_supports_unit_type(entry, unit_type):
                continue
            if required_state_mismatches(entry, lambda name: text_of(obj, name)):
                continue
            if entry["key"] == "column_configuration/feed_stage" and not feed_stage_supported(obj):
                continue
            pairs.append(pair_from_target_and_entry(target, entry))
    return pairs


def scan(args: argparse.Namespace) -> dict[str, Any]:
    args.manifest = resolve_repo_path(args.manifest)
    args.output_dir = resolve_repo_path(args.output_dir)
    ensure_output_dir(args.output_dir, args.overwrite)
    work_dir = args.output_dir / "_work"
    work_dir.mkdir(parents=True, exist_ok=True)

    sources = manifest_sources(args.manifest, args.category)
    if args.limit is not None:
        sources = sources[: args.limit]

    rows: list[dict[str, Any]] = []
    errors: list[dict[str, Any]] = []
    parameter_counts: Counter[str] = Counter()
    unit_type_counts: Counter[str] = Counter()
    source_category_counts: Counter[str] = Counter()

    for source in sources:
        try:
            extracted = work_dir / f"{source['source_id']}.dwxmz"
            read_inner_dwsim_from_curated_zip(source["source_path"], extracted)
            pairs = supported_pairs(extracted)
            for pair in pairs:
                parameter = f"{pair['parameter']['namespace']}/{pair['parameter']['name']}"
                unit_type = pair["target"].get("type") or "unknown"
                row = {
                    "source_path": str(source["source_path"]),
                    "source_id": source["source_id"],
                    "source_name": source["source_name"],
                    "source_category": source["source_category"],
                    "target_guid": pair["target"]["guid"],
                    "target_tag": pair["target"].get("tag"),
                    "unit_type": unit_type,
                    "parameter": parameter,
                    "support_level": pair.get("support_level"),
                }
                rows.append(row)
                parameter_counts[parameter] += 1
                unit_type_counts[str(unit_type)] += 1
                source_category_counts[source["source_category"]] += 1
        except Exception as exc:  # noqa: BLE001
            errors.append(
                {
                    "source_path": str(source["source_path"]),
                    "source_id": source["source_id"],
                    "source_name": source["source_name"],
                    "source_category": source["source_category"],
                    "error": str(exc),
                }
            )

    report = {
        "source_count": len(sources),
        "source_error_count": len(errors),
        "repair_pair_count": len(rows),
        "source_with_pairs_count": len({row["source_id"] for row in rows}),
        "parameter_counts": dict(parameter_counts),
        "unit_type_counts": dict(unit_type_counts),
        "source_category_counts": dict(source_category_counts),
        "rows": rows,
        "errors": errors,
    }
    write_json(args.output_dir / "feasibility_report.json", report)
    return report


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", default=DEFAULT_MANIFEST, type=Path)
    parser.add_argument("--category", default="all", help="manifest category to scan, or 'all'")
    parser.add_argument("--output-dir", default=DEFAULT_OUTPUT_DIR, type=Path)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()
    try:
        report = scan(args)
    except Exception as exc:  # noqa: BLE001
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1
    print(
        "Feasibility scan complete: "
        f"sources={report['source_count']} source_with_pairs={report['source_with_pairs_count']} "
        f"pairs={report['repair_pair_count']}"
    )
    print(f"Wrote feasibility report to {args.output_dir / 'feasibility_report.json'}")
    return 0 if report["repair_pair_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
