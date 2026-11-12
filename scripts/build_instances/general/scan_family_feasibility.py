#!/usr/bin/env python3
"""Read-only feasibility scan for future v0.1 final repair families."""

from __future__ import annotations

import argparse
import csv
import shutil
import sys
from collections import Counter, defaultdict
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from builder_common import graphic_tags, read_dwxmz_xml, read_inner_dwsim_from_curated_zip, text_of, write_json  # noqa: E402
from repair_registry import required_state_value_matches  # noqa: E402


DEFAULT_MANIFEST = Path("curated_data/dwsim_headless_successes/manifest.csv")
DEFAULT_OUTPUT_DIR = Path(".tmp/final_family_feasibility")

HEATER_TYPE = "DWSIM.UnitOperations.UnitOperations.Heater"
COOLER_TYPE = "DWSIM.UnitOperations.UnitOperations.Cooler"
VESSEL_TYPE = "DWSIM.UnitOperations.UnitOperations.Vessel"
DISTILLATION_COLUMN_TYPE = "DWSIM.UnitOperations.UnitOperations.DistillationColumn"


FAMILY_SPECS: tuple[dict[str, Any], ...] = (
    {
        "family": "thermal_specification/outlet_temperature",
        "unit_types": (HEATER_TYPE, COOLER_TYPE),
        "xml_field": "OutletTemperature",
        "required_state_by_unit_type": {
            HEATER_TYPE: {"CalcMode": "OutletTemperature"},
            COOLER_TYPE: {"CalcMode": "OutletTemperature"},
        },
        "unit": "K",
        "mutation_risk": "low",
        "executor_difficulty": "low",
        "discovery_likelihood": "high",
        "notes": "Native Heater/Cooler outlet-temperature mode with direct scalar OutletTemperature field.",
    },
    {
        "family": "thermal_specification/heat_duty",
        "unit_types": (HEATER_TYPE, COOLER_TYPE),
        "xml_field": "DeltaQ",
        "required_state_by_unit_type": {
            HEATER_TYPE: {"CalcMode": "HeatAdded"},
            COOLER_TYPE: {"CalcMode": "HeatRemoved"},
        },
        "unit": "kW",
        "mutation_risk": "medium",
        "executor_difficulty": "medium",
        "discovery_likelihood": "medium",
        "notes": "Native duty mode uses DeltaQ, but sign/mode semantics differ between Heater and Cooler.",
    },
    {
        "family": "separator_specification/pressure",
        "unit_types": (VESSEL_TYPE,),
        "xml_field": "FlashPressure",
        "required_state": {"OverrideP": "true"},
        "unit": "Pa",
        "mutation_risk": "medium",
        "executor_difficulty": "medium",
        "discovery_likelihood": "medium",
        "notes": "Native Vessel flash pressure is scalar when OverrideP=true.",
    },
    {
        "family": "separator_specification/temperature",
        "unit_types": (VESSEL_TYPE,),
        "xml_field": "FlashTemperature",
        "required_state": {"OverrideT": "true"},
        "unit": "K",
        "mutation_risk": "medium",
        "executor_difficulty": "medium",
        "discovery_likelihood": "medium",
        "notes": "Native Vessel flash temperature is scalar when OverrideT=true.",
    },
    {
        "family": "column_specification/reboiler_duty",
        "unit_types": (DISTILLATION_COLUMN_TYPE,),
        "xml_field": "ReboilerDuty",
        "required_state": {},
        "unit": "kW",
        "mutation_risk": "high",
        "executor_difficulty": "medium",
        "discovery_likelihood": "low",
        "notes": "Direct scalar field, but native distillation columns are sparse in the curated corpus.",
    },
    {
        "family": "column_specification/condenser_duty",
        "unit_types": (DISTILLATION_COLUMN_TYPE,),
        "xml_field": "CondenserDuty",
        "required_state": {},
        "unit": "kW",
        "mutation_risk": "high",
        "executor_difficulty": "medium",
        "discovery_likelihood": "low",
        "notes": "Direct scalar field, but native distillation columns are sparse in the curated corpus.",
    },
    {
        "family": "column_specification/distillate_flowrate",
        "unit_types": (DISTILLATION_COLUMN_TYPE,),
        "xml_field": "DistillateFlowRate",
        "required_state": {},
        "unit": "mol/s",
        "mutation_risk": "high",
        "executor_difficulty": "medium",
        "discovery_likelihood": "low",
        "require_nonzero": True,
        "notes": "Field exists, but zero values indicate this may not be an active spec in many files.",
    },
    {
        "family": "column_specification/vapor_flowrate",
        "unit_types": (DISTILLATION_COLUMN_TYPE,),
        "xml_field": "VaporFlowRate",
        "required_state": {},
        "unit": "mol/s",
        "mutation_risk": "high",
        "executor_difficulty": "medium",
        "discovery_likelihood": "low",
        "require_nonzero": True,
        "notes": "Field exists, but zero values indicate this may not be an active spec in many files.",
    },
)

SUMMARY_FIELDS = [
    "family",
    "unit_types",
    "candidate_objects",
    "candidate_sources",
    "required_state_supported_objects",
    "required_state_supported_sources",
    "xml_field_found_objects",
    "baseline_value_readable_objects",
    "strong_candidate_objects",
    "strong_candidate_sources",
    "baseline_value_readable_rate",
    "strong_candidate_rate",
    "unit",
    "xml_field",
    "required_state",
    "mutation_risk",
    "executor_difficulty",
    "discovery_likelihood",
    "recommendation",
    "notes",
]

ROW_FIELDS = [
    "source_id",
    "source_path",
    "source_name",
    "source_category",
    "family",
    "target_guid",
    "target_tag",
    "unit_type",
    "object_class",
    "calc_mode",
    "xml_field",
    "baseline_value",
    "baseline_value_numeric",
    "required_state_supported",
    "required_state_failures",
    "xml_field_found",
    "baseline_value_readable",
    "baseline_value_nonzero",
    "strong_candidate",
]


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
    return f"{path.parent.name}_{path.stem}".lower().replace("-", "_")


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
            source_rel = Path(curated_path)
            sources.append(
                {
                    "source_path": base / source_rel,
                    "source_id": source_id_from_path(source_rel),
                    "source_name": row.get("original_zip_name") or source_rel.name,
                    "source_category": row_category,
                }
            )
    return sources


def parse_float(text: str | None) -> float | None:
    if text is None:
        return None
    try:
        return float(text)
    except ValueError:
        return None


def required_state_for_unit(spec: dict[str, Any], unit_type: str | None) -> dict[str, str]:
    by_type = spec.get("required_state_by_unit_type")
    if isinstance(by_type, dict):
        state = by_type.get(unit_type)
        return state if isinstance(state, dict) else {}
    state = spec.get("required_state")
    return state if isinstance(state, dict) else {}


def state_failures(obj: Any, required_state: dict[str, str]) -> list[str]:
    failures: list[str] = []
    for field, expected in required_state.items():
        actual = text_of(obj, field)
        if not required_state_value_matches(actual, expected):
            failures.append(f"{field}={actual!r} expected {expected!r}")
    return failures


def object_row(source: dict[str, Any], tags: dict[str, str], obj: Any, spec: dict[str, Any]) -> dict[str, Any]:
    guid = text_of(obj, "Name") or ""
    unit_type = text_of(obj, "Type") or ""
    xml_field = spec["xml_field"]
    baseline_text = text_of(obj, xml_field)
    baseline_number = parse_float(baseline_text)
    required_state = required_state_for_unit(spec, unit_type)
    failures = state_failures(obj, required_state)
    required_supported = not failures
    xml_found = baseline_text is not None
    readable = baseline_number is not None
    nonzero = bool(readable and abs(float(baseline_number)) > 1e-12)
    require_nonzero = spec.get("require_nonzero") is True
    strong = bool(required_supported and xml_found and readable and (nonzero or not require_nonzero))
    return {
        "source_id": source["source_id"],
        "source_path": str(source["source_path"]),
        "source_name": source["source_name"],
        "source_category": source["source_category"],
        "family": spec["family"],
        "target_guid": guid,
        "target_tag": tags.get(guid),
        "unit_type": unit_type,
        "object_class": text_of(obj, "ObjectClass"),
        "calc_mode": text_of(obj, "CalcMode"),
        "xml_field": xml_field,
        "baseline_value": baseline_text,
        "baseline_value_numeric": baseline_number,
        "required_state_supported": required_supported,
        "required_state_failures": "; ".join(failures),
        "xml_field_found": xml_found,
        "baseline_value_readable": readable,
        "baseline_value_nonzero": nonzero,
        "strong_candidate": strong,
    }


def scan_source(source: dict[str, Any], extracted: Path) -> list[dict[str, Any]]:
    tree, _xml_entry, _entries = read_dwxmz_xml(extracted)
    root = tree.getroot()
    tags = graphic_tags(root)
    simulation_objects = root.find("SimulationObjects")
    if simulation_objects is None:
        return []
    rows: list[dict[str, Any]] = []
    for obj in simulation_objects:
        unit_type = text_of(obj, "Type")
        if not unit_type:
            continue
        for spec in FAMILY_SPECS:
            if unit_type in spec["unit_types"]:
                rows.append(object_row(source, tags, obj, spec))
    return rows


def rate(numerator: int, denominator: int) -> float:
    return round(numerator / denominator, 4) if denominator else 0.0


def recommendation(strong_objects: int, strong_sources: int, readable_rate: float) -> str:
    if strong_sources >= 20 and strong_objects >= 50 and readable_rate >= 0.8:
        return "strong_candidate"
    if strong_sources >= 10 and strong_objects >= 20 and readable_rate >= 0.6:
        return "promising_with_review"
    if strong_objects > 0:
        return "weak_or_edge"
    return "reject_for_v0_1_final"


def summarize(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    summaries: list[dict[str, Any]] = []
    rows_by_family: dict[str, list[dict[str, Any]]] = defaultdict(list)
    for row in rows:
        rows_by_family[row["family"]].append(row)

    for spec in FAMILY_SPECS:
        family_rows = rows_by_family.get(spec["family"], [])
        candidate_objects = len(family_rows)
        candidate_sources = len({row["source_id"] for row in family_rows})
        required_rows = [row for row in family_rows if row["required_state_supported"]]
        field_rows = [row for row in required_rows if row["xml_field_found"]]
        readable_rows = [row for row in field_rows if row["baseline_value_readable"]]
        strong_rows = [row for row in family_rows if row["strong_candidate"]]
        readable_rate = rate(len(readable_rows), candidate_objects)
        strong_rate = rate(len(strong_rows), candidate_objects)
        required_state = spec.get("required_state") or spec.get("required_state_by_unit_type") or {}
        summaries.append(
            {
                "family": spec["family"],
                "unit_types": "; ".join(spec["unit_types"]),
                "candidate_objects": candidate_objects,
                "candidate_sources": candidate_sources,
                "required_state_supported_objects": len(required_rows),
                "required_state_supported_sources": len({row["source_id"] for row in required_rows}),
                "xml_field_found_objects": len(field_rows),
                "baseline_value_readable_objects": len(readable_rows),
                "strong_candidate_objects": len(strong_rows),
                "strong_candidate_sources": len({row["source_id"] for row in strong_rows}),
                "baseline_value_readable_rate": readable_rate,
                "strong_candidate_rate": strong_rate,
                "unit": spec["unit"],
                "xml_field": spec["xml_field"],
                "required_state": str(required_state),
                "mutation_risk": spec["mutation_risk"],
                "executor_difficulty": spec["executor_difficulty"],
                "discovery_likelihood": spec["discovery_likelihood"],
                "recommendation": recommendation(len(strong_rows), len({row["source_id"] for row in strong_rows}), readable_rate),
                "notes": spec["notes"],
            }
        )
    return summaries


def counter_dict(rows: list[dict[str, Any]], field: str) -> dict[str, int]:
    return dict(Counter(str(row.get(field)) for row in rows if row.get(field) is not None))


def write_csv(path: Path, rows: list[dict[str, Any]], fields: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field) for field in fields})


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
    for source in sources:
        try:
            extracted = work_dir / f"{source['source_id']}.dwxmz"
            read_inner_dwsim_from_curated_zip(source["source_path"], extracted)
            rows.extend(scan_source(source, extracted))
        except Exception as exc:  # noqa: BLE001
            errors.append(
                {
                    "source_id": source["source_id"],
                    "source_path": str(source["source_path"]),
                    "source_name": source["source_name"],
                    "source_category": source["source_category"],
                    "error": str(exc),
                }
            )

    summaries = summarize(rows)
    report = {
        "source_count": len(sources),
        "source_error_count": len(errors),
        "family_count": len(FAMILY_SPECS),
        "candidate_object_count": len(rows),
        "strong_candidate_object_count": sum(1 for row in rows if row["strong_candidate"]),
        "source_category_counts": counter_dict(rows, "source_category"),
        "family_summary": summaries,
        "rows": rows,
        "errors": errors,
    }
    write_json(args.output_dir / "family_feasibility_report.json", report)
    write_csv(args.output_dir / "family_feasibility_summary.csv", summaries, SUMMARY_FIELDS)
    write_csv(args.output_dir / "family_feasibility_rows.csv", rows, ROW_FIELDS)
    return report


def print_summary(report: dict[str, Any], output_dir: Path) -> None:
    print(
        "Family feasibility scan complete: "
        f"sources={report['source_count']} errors={report['source_error_count']} "
        f"families={report['family_count']} strong_objects={report['strong_candidate_object_count']}"
    )
    for item in report["family_summary"]:
        print(
            f"{item['family']}: "
            f"strong_objects={item['strong_candidate_objects']} "
            f"strong_sources={item['strong_candidate_sources']} "
            f"recommendation={item['recommendation']}"
        )
    print(f"Wrote report to {output_dir / 'family_feasibility_report.json'}")
    print(f"Wrote summary CSV to {output_dir / 'family_feasibility_summary.csv'}")


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
    print_summary(report, args.output_dir)
    return 0 if report["strong_candidate_object_count"] > 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
