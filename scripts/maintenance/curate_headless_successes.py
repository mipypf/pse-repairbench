#!/usr/bin/env python3
"""Curate headless-successful DWSIM source archives for redistribution."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path
from zipfile import ZipFile


DEFAULT_SUCCESS_CSV = Path("metadata/dwsim_sources/dwsim_headless_successes.csv")
DEFAULT_CATALOG_CSV = Path("metadata/dwsim_sources/raw_data_catalog.csv")
DEFAULT_RAW_DIR = Path("raw_data/DWSIM_data")
DEFAULT_OUT_DIR = Path("curated_data/dwsim_headless_successes")


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def slugify(text: str, max_len: int = 88) -> str:
    stem = Path(text).stem.lower()
    stem = re.sub(r"[^a-z0-9]+", "_", stem)
    stem = re.sub(r"_+", "_", stem).strip("_")
    if not stem:
        stem = "flowsheet"
    return stem[:max_len].strip("_")


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8-sig") as handle:
        return list(csv.DictReader(handle))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def clean_output_dir(path: Path) -> None:
    resolved = path.resolve()
    cwd = Path.cwd().resolve()
    if cwd not in resolved.parents and resolved != cwd:
        raise ValueError(f"refusing to clean outside workspace: {resolved}")
    if path.exists():
        shutil.rmtree(path)
    path.mkdir(parents=True, exist_ok=True)


def copy_archive_without_pdfs(source: Path, destination: Path) -> int:
    """Copy a ZIP archive while excluding PDF documents.

    The FOSSEE source archives pair DWSIM flowsheets with abstract PDFs. The
    tracked curated set needs the flowsheets for benchmark reproduction but
    intentionally excludes the PDFs and their embedded logos/graphics.
    """
    removed_pdf_count = 0
    with (
        ZipFile(source) as source_archive,
        ZipFile(destination, "w") as curated_archive,
    ):
        curated_archive.comment = source_archive.comment
        for info in source_archive.infolist():
            if not info.is_dir() and Path(info.filename).suffix.lower() == ".pdf":
                removed_pdf_count += 1
                continue
            curated_archive.writestr(info, source_archive.read(info.filename))
    shutil.copystat(source, destination)
    return removed_pdf_count


def copy_successes(
    success_csv: Path,
    catalog_csv: Path,
    raw_dir: Path,
    out_dir: Path,
    clean: bool,
) -> tuple[list[dict[str, object]], dict[str, object]]:
    if clean:
        clean_output_dir(out_dir)
    else:
        out_dir.mkdir(parents=True, exist_ok=True)

    successes = read_csv(success_csv)
    catalog = {row["zip_name"]: row for row in read_csv(catalog_csv)}
    by_category_index: dict[str, int] = defaultdict(int)
    used_names: set[str] = set()
    manifest_rows: list[dict[str, object]] = []

    for row in sorted(successes, key=lambda item: (item["estimated_category"], item["zip_name"])):
        original_name = row["zip_name"]
        catalog_row = catalog.get(original_name, {})
        category = row["estimated_category"] or "uncategorized"
        by_category_index[category] += 1

        source_path = raw_dir / original_name
        if not source_path.exists():
            raise FileNotFoundError(f"missing raw archive: {source_path}")

        category_dir = out_dir / category
        category_dir.mkdir(parents=True, exist_ok=True)

        base_name = f"{by_category_index[category]:03d}_{slugify(original_name)}.zip"
        destination = category_dir / base_name
        while str(destination.relative_to(out_dir)) in used_names:
            by_category_index[category] += 1
            base_name = f"{by_category_index[category]:03d}_{slugify(original_name)}.zip"
            destination = category_dir / base_name
        used_names.add(str(destination.relative_to(out_dir)))

        source_hash = sha256(source_path)
        catalog_hash = catalog_row.get("zip_sha256", "")
        if catalog_hash and source_hash.lower() != catalog_hash.lower():
            raise ValueError(f"checksum mismatch for {original_name}")
        removed_pdf_count = copy_archive_without_pdfs(source_path, destination)
        curated_hash = sha256(destination)

        manifest_rows.append(
            {
                "curated_path": destination.relative_to(out_dir).as_posix(),
                "category": category,
                "original_zip_name": original_name,
                "source_zip_sha256": source_hash,
                "zip_sha256": curated_hash,
                "zip_size": destination.stat().st_size,
                "excluded_pdf_count": removed_pdf_count,
                "dwsim_file_name": row.get("dwsim_file_name", ""),
                "dwsim_file_sha256": catalog_row.get("dwsim_file_sha256", ""),
                "dwsim_file_size": catalog_row.get("dwsim_file_size", ""),
                "dwsim_storage_format": catalog_row.get("dwsim_storage_format", ""),
                "source_scope_status": row.get("scope_status", ""),
                "category_confidence": row.get("category_confidence", ""),
                "loaded_objects": row.get("loaded_objects", ""),
                "duration_sec": row.get("duration_sec", ""),
                "screen_result_status": row.get("result_status", ""),
                "screen_success": row.get("success", ""),
            }
        )

    counts = Counter(row["category"] for row in manifest_rows)
    total_size = sum(int(row["zip_size"]) for row in manifest_rows)
    summary = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "source_success_csv": str(success_csv),
        "source_catalog_csv": str(catalog_csv),
        "source_raw_dir": str(raw_dir),
        "success_definition": "DWSIM.Automation.Automation3.CalculateFlowsheet4 returned solved_after=true with zero exceptions",
        "total_archives": len(manifest_rows),
        "total_size_bytes": total_size,
        "total_size_mb": round(total_size / (1024 * 1024), 2),
        "excluded_pdf_files": sum(int(row["excluded_pdf_count"]) for row in manifest_rows),
        "by_category": dict(sorted(counts.items())),
    }
    return manifest_rows, summary


def write_readme(out_dir: Path, summary: dict[str, object]) -> None:
    lines = [
        "# DWSIM Headless Success Archives",
        "",
        "This directory contains curated FOSSEE/DWSIM flowsheet archives that",
        "passed the headless DWSIM Automation3 smoke screen.",
        "",
        "Success means `CalculateFlowsheet4` completed with `Solved=True` and zero",
        "returned exceptions under the local DWSIM runner used for screening.",
        "",
        f"- Total archives: {summary['total_archives']}",
        f"- Total size: {summary['total_size_mb']} MB",
        f"- Excluded source PDF files: {summary['excluded_pdf_files']}",
        "",
        "Category counts:",
    ]
    for category, count in summary["by_category"].items():
        lines.append(f"- `{category}`: {count}")
    lines.extend(
        [
            "",
            "The DWSIM flowsheet entries are curated from `raw_data/DWSIM_data`.",
            "Source abstract PDFs are intentionally excluded because they contain",
            "third-party logos and graphics that are not needed for benchmark",
            "reproduction. `manifest.csv` preserves the original archive name,",
            "source checksum, curated checksum, and excluded-PDF count.",
            "",
            "To re-run a single archive:",
            "",
            "```powershell",
            "powershell -ExecutionPolicy Bypass -File scripts\\dwsim\\run_dwsim_headless.ps1 -InputPath curated_data\\dwsim_headless_successes\\distillation\\001_example.zip",
            "```",
            "",
        ]
    )
    (out_dir / "README.md").write_text("\n".join(lines), encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--successes", type=Path, default=DEFAULT_SUCCESS_CSV)
    parser.add_argument("--catalog", type=Path, default=DEFAULT_CATALOG_CSV)
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--out-dir", type=Path, default=DEFAULT_OUT_DIR)
    parser.add_argument("--clean", action="store_true")
    args = parser.parse_args()

    manifest_rows, summary = copy_successes(
        success_csv=args.successes,
        catalog_csv=args.catalog,
        raw_dir=args.raw_dir,
        out_dir=args.out_dir,
        clean=args.clean,
    )

    fieldnames = [
        "curated_path",
        "category",
        "original_zip_name",
        "source_zip_sha256",
        "zip_sha256",
        "zip_size",
        "excluded_pdf_count",
        "dwsim_file_name",
        "dwsim_file_sha256",
        "dwsim_file_size",
        "dwsim_storage_format",
        "source_scope_status",
        "category_confidence",
        "loaded_objects",
        "duration_sec",
        "screen_result_status",
        "screen_success",
    ]
    write_csv(args.out_dir / "manifest.csv", manifest_rows, fieldnames)
    (args.out_dir / "summary.json").write_text(json.dumps(summary, indent=2) + "\n", encoding="utf-8")
    write_readme(args.out_dir, summary)

    print(f"Copied {summary['total_archives']} archives to {args.out_dir}")
    print(f"Total size: {summary['total_size_mb']} MB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
