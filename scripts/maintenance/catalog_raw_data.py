#!/usr/bin/env python3
"""Catalog raw FOSSEE/DWSIM source archives for benchmark triage."""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


DWSIM_SUFFIXES = {".dwxmz", ".dwxml"}
PDF_SUFFIX = ".pdf"

CSV_FIELDS = [
    "zip_name",
    "zip_sha256",
    "zip_size",
    "dwsim_file_count",
    "dwsim_file_name",
    "dwsim_file_suffix",
    "dwsim_file_sha256",
    "dwsim_file_size",
    "dwsim_storage_format",
    "dwsim_xml_entry_name",
    "dwsim_archive_entries",
    "contains_database",
    "pdf_count",
    "pdf_name",
    "pdf_sha256",
    "pdf_size",
    "read_status",
    "scope_status",
    "estimated_category",
    "category_confidence",
    "category_signals",
    "xml_root",
    "xml_sections",
    "object_count",
    "parse_error",
]


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def child_names(element: ET.Element | None) -> list[str]:
    if element is None:
        return []
    return [local_name(child.tag) for child in element]


def find_first_child(element: ET.Element, name: str) -> ET.Element | None:
    for child in element:
        if local_name(child.tag) == name:
            return child
    return None


def text_of(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    text = element.text.strip()
    return text or None


def csv_value(value: object) -> object:
    if isinstance(value, list):
        return "; ".join(str(item) for item in value)
    if isinstance(value, bool):
        return str(value).lower()
    if value is None:
        return ""
    return value


def object_summary_text(root: ET.Element) -> str:
    simulation_objects = find_first_child(root, "SimulationObjects")
    if simulation_objects is None:
        return ""

    parts: list[str] = []
    for obj in simulation_objects:
        for child_name in ("Type", "ObjectClass", "ComponentDescription", "Tag", "GraphicObjectName"):
            value = text_of(find_first_child(obj, child_name))
            if value:
                parts.append(value)
        parts.extend(str(value) for value in obj.attrib.values())
    return " ".join(parts).lower()


def add_signal(signals: list[str], signal: str) -> None:
    if signal not in signals:
        signals.append(signal)


def estimate_category(zip_name: str, root: ET.Element | None) -> tuple[str, str, str, str]:
    filename = zip_name.lower()
    object_text = object_summary_text(root) if root is not None else ""
    signals: list[str] = []
    scores = {
        "flash_separator": 0,
        "distillation": 0,
        "reaction_recycle": 0,
        "other_candidate": 0,
    }

    filename_rules = [
        ("distillation", "distillation", 3),
        ("distillation", "column", 1),
        ("distillation", "fractionation", 3),
        ("flash_separator", "flash", 3),
        ("flash_separator", "separator", 2),
        ("flash_separator", "separation", 1),
        ("reaction_recycle", "reaction", 2),
        ("reaction_recycle", "reactor", 3),
        ("reaction_recycle", "recycle", 2),
        ("reaction_recycle", "synthesis", 2),
        ("reaction_recycle", "hydrogenation", 2),
        ("reaction_recycle", "dehydrogenation", 2),
        ("reaction_recycle", "esterification", 2),
        ("reaction_recycle", "reforming", 2),
        ("other_candidate", "refrigeration", 3),
        ("other_candidate", "refrigerant", 3),
        ("other_candidate", "heat_pump", 3),
        ("other_candidate", "rankine", 3),
        ("other_candidate", "brayton", 3),
        ("other_candidate", "turbine", 3),
        ("other_candidate", "power_plant", 3),
        ("other_candidate", "liquefaction", 2),
    ]
    object_rules = [
        ("distillation", "distillationcolumn", 4),
        ("distillation", "distillation column", 4),
        ("distillation", "column", 2),
        ("flash_separator", "separator", 3),
        ("flash_separator", "flash", 3),
        ("reaction_recycle", "reactor", 4),
        ("reaction_recycle", "conversionreactor", 4),
        ("reaction_recycle", "equilibriumreactor", 4),
        ("reaction_recycle", "gibbsreactor", 4),
        ("reaction_recycle", "recycle", 3),
        ("other_candidate", "compressor", 1),
        ("other_candidate", "expander", 1),
        ("other_candidate", "turbine", 2),
        ("other_candidate", "heat exchanger", 2),
        ("other_candidate", "heatexchanger", 2),
    ]

    normalized_filename = filename.replace("-", "_").replace(" ", "_")
    for category, token, weight in filename_rules:
        if token in normalized_filename:
            scores[category] += weight
            add_signal(signals, f"filename:{token}")

    for category, token, weight in object_rules:
        if token in object_text:
            scores[category] += weight
            add_signal(signals, f"object:{token}")

    ranked = sorted(scores.items(), key=lambda item: (-item[1], item[0]))
    category, score = ranked[0]
    if score == 0:
        category = "other_candidate"
        confidence = "low"
        scope_status = "needs_review"
        add_signal(signals, "no_strong_signal")
    elif score >= 4:
        confidence = "high"
        scope_status = "out_of_scope_candidate" if category == "other_candidate" else "in_initial_scope_candidate"
    elif score >= 2:
        confidence = "medium"
        scope_status = "out_of_scope_candidate" if category == "other_candidate" else "in_initial_scope_candidate"
    else:
        confidence = "low"
        scope_status = "needs_review"

    return category, confidence, "; ".join(signals), scope_status


def parse_dwsim_xml(name: str, data: bytes) -> tuple[ET.Element, dict[str, object]]:
    suffix = Path(name).suffix.lower()
    metadata: dict[str, object] = {
        "contains_database": False,
        "dwsim_archive_entries": [],
        "dwsim_storage_format": "dwxml_plain_xml" if suffix == ".dwxml" else "dwxmz_zip_xml",
        "dwsim_xml_entry_name": "",
        "read_status": "readable",
    }

    if suffix == ".dwxmz":
        try:
            with zipfile.ZipFile(io.BytesIO(data)) as archive:
                entries = archive.namelist()
                metadata["dwsim_archive_entries"] = entries
                metadata["contains_database"] = any(Path(entry).suffix.lower() == ".db" for entry in entries)
                xml_entries = [entry for entry in entries if Path(entry).suffix.lower() == ".xml"]
                if not xml_entries:
                    raise ValueError("no XML entry found in DWSIM archive")
                selected = sorted(xml_entries)[0]
                metadata["dwsim_xml_entry_name"] = selected
                with archive.open(selected) as handle:
                    root = ET.parse(handle).getroot()
                return root, metadata
        except zipfile.BadZipFile:
            metadata["dwsim_storage_format"] = "dwxmz_plain_xml_fallback"
            metadata["read_status"] = "readable_with_xml_fallback"

    root = ET.fromstring(data)
    return root, metadata


def catalog_archive(path: Path) -> dict[str, object]:
    record: dict[str, object] = {field: "" for field in CSV_FIELDS}
    record["zip_name"] = path.name
    record["zip_sha256"] = sha256_file(path)
    record["zip_size"] = path.stat().st_size
    record["read_status"] = "unreadable"
    record["scope_status"] = "needs_review"
    record["estimated_category"] = "other_candidate"
    record["category_confidence"] = "low"

    try:
        with zipfile.ZipFile(path) as archive:
            names = sorted(name for name in archive.namelist() if not name.endswith("/"))
            dwsim_files = [name for name in names if Path(name).suffix.lower() in DWSIM_SUFFIXES]
            pdf_files = [name for name in names if Path(name).suffix.lower() == PDF_SUFFIX]
            record["dwsim_file_count"] = len(dwsim_files)
            record["pdf_count"] = len(pdf_files)

            if pdf_files:
                pdf_name = pdf_files[0]
                pdf_data = archive.read(pdf_name)
                record["pdf_name"] = pdf_name
                record["pdf_sha256"] = sha256_bytes(pdf_data)
                record["pdf_size"] = len(pdf_data)

            if len(dwsim_files) != 1:
                record["parse_error"] = f"expected exactly 1 DWSIM file, found {len(dwsim_files)}"
                return record

            dwsim_name = dwsim_files[0]
            dwsim_data = archive.read(dwsim_name)
            record["dwsim_file_name"] = dwsim_name
            record["dwsim_file_suffix"] = Path(dwsim_name).suffix.lower().lstrip(".")
            record["dwsim_file_sha256"] = sha256_bytes(dwsim_data)
            record["dwsim_file_size"] = len(dwsim_data)

            root, metadata = parse_dwsim_xml(dwsim_name, dwsim_data)
            sections = child_names(root)
            simulation_objects = find_first_child(root, "SimulationObjects")
            category, confidence, signals, scope_status = estimate_category(path.name, root)

            record.update(
                {
                    "read_status": metadata["read_status"],
                    "scope_status": scope_status,
                    "estimated_category": category,
                    "category_confidence": confidence,
                    "category_signals": signals,
                    "dwsim_storage_format": metadata["dwsim_storage_format"],
                    "dwsim_xml_entry_name": metadata["dwsim_xml_entry_name"],
                    "dwsim_archive_entries": metadata["dwsim_archive_entries"],
                    "contains_database": metadata["contains_database"],
                    "xml_root": local_name(root.tag),
                    "xml_sections": sections,
                    "object_count": len(simulation_objects) if simulation_objects is not None else 0,
                    "parse_error": "",
                }
            )
    except Exception as exc:  # noqa: BLE001 - catalog should retain per-file failures.
        record["parse_error"] = f"{type(exc).__name__}: {exc}"

    return record


def write_catalog(records: list[dict[str, object]], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    csv_path = out_dir / "raw_data_catalog.csv"
    jsonl_path = out_dir / "raw_data_catalog.jsonl"

    with csv_path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS, lineterminator="\n")
        writer.writeheader()
        for record in records:
            writer.writerow({field: csv_value(record.get(field, "")) for field in CSV_FIELDS})

    with jsonl_path.open("w", encoding="utf-8", newline="\n") as handle:
        for record in records:
            ordered = {field: record.get(field, "") for field in CSV_FIELDS}
            handle.write(json.dumps(ordered, ensure_ascii=False, sort_keys=False) + "\n")


def print_summary(records: list[dict[str, object]]) -> None:
    def count(field: str, value: object) -> int:
        return sum(1 for record in records if record.get(field) == value)

    fallback = [record["zip_name"] for record in records if record.get("read_status") == "readable_with_xml_fallback"]
    print(f"Cataloged {len(records)} raw archive(s)")
    print(f"PDF metadata present: {sum(1 for record in records if record.get('pdf_count') == 1)}")
    print(f"DWSIM files exactly one: {sum(1 for record in records if record.get('dwsim_file_count') == 1)}")
    print(f"read_status=readable: {count('read_status', 'readable')}")
    print(f"read_status=readable_with_xml_fallback: {count('read_status', 'readable_with_xml_fallback')}")
    print(f"read_status=unreadable: {count('read_status', 'unreadable')}")
    if fallback:
        print(f"Fallback archive(s): {', '.join(fallback)}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=Path("raw_data/DWSIM_data"))
    parser.add_argument("--out-dir", type=Path, default=Path("metadata/dwsim_sources"))
    args = parser.parse_args()

    archives = sorted(args.raw_dir.glob("*.zip"), key=lambda item: item.name.lower())
    if not archives:
        print(f"ERROR: no .zip archives found in {args.raw_dir}")
        return 1

    records = [catalog_archive(path) for path in archives]
    write_catalog(records, args.out_dir)
    print_summary(records)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
