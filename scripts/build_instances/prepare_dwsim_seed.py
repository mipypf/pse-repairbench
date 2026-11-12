#!/usr/bin/env python3
"""Prepare the first DWSIM seed manifest and observation stubs."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import shutil
import zipfile
from datetime import date
from pathlib import Path
from xml.etree import ElementTree as ET


SOURCE_URL = "https://dwsim.fossee.org/flowsheeting-project/dwsim-flowsheet-run/26"
DOWNLOAD_URL = "https://dwsim.fossee.org/flowsheeting-project/full-download/project/26"
LICENSE = "Creative Commons Attribution-ShareAlike 4.0 International License"
SOURCE_NAME = "FOSSEE DWSIM Flowsheeting Project: Benzene Toluene Fractionation Unit"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def relative_ref(instance_path: Path, artifact_path: Path) -> str:
    return artifact_path.resolve().relative_to(instance_path.parent.resolve()).as_posix()


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(element: ET.Element | None) -> str | None:
    if element is None or element.text is None:
        return None
    text = element.text.strip()
    return text or None


def find_first_child(element: ET.Element, name: str) -> ET.Element | None:
    for child in element:
        if local_name(child.tag) == name:
            return child
    return None


def child_names(element: ET.Element | None) -> list[str]:
    if element is None:
        return []
    return [local_name(child.tag) for child in element]


def extract_dwsim_file(download: Path, output: Path) -> Path:
    if download.suffix.lower() in {".dwxmz", ".dwxml"}:
        shutil.copyfile(download, output / download.name)
        return output / download.name

    with zipfile.ZipFile(download) as archive:
        candidates = [
            name
            for name in archive.namelist()
            if Path(name).suffix.lower() in {".dwxmz", ".dwxml"} and not name.endswith("/")
        ]
        if not candidates:
            raise ValueError(f"no .dwxmz or .dwxml file found in {download}")
        selected = sorted(candidates)[0]
        target = output / Path(selected).name
        with archive.open(selected) as src, target.open("wb") as dst:
            shutil.copyfileobj(src, dst)
        return target


def read_dwsim_xml(path: Path) -> tuple[ET.Element, dict[str, object]]:
    metadata: dict[str, object] = {
        "source_format": path.suffix.lower().lstrip("."),
        "internal_archive_entries": [],
        "contains_database": False,
    }

    if path.suffix.lower() == ".dwxmz":
        with zipfile.ZipFile(path) as archive:
            entries = archive.namelist()
            metadata["internal_archive_entries"] = entries
            metadata["contains_database"] = any(Path(name).suffix.lower() == ".db" for name in entries)
            xml_entries = [name for name in entries if Path(name).suffix.lower() == ".xml"]
            if not xml_entries:
                raise ValueError(f"no XML entry found in DWSIM archive {path}")
            with archive.open(sorted(xml_entries)[0]) as handle:
                root = ET.parse(handle).getroot()
    else:
        root = ET.parse(path).getroot()

    metadata["root_element"] = local_name(root.tag)
    metadata["sections"] = child_names(root)
    return root, metadata


def summarize_object(element: ET.Element) -> dict[str, object]:
    fields = {
        "guid": text_of(find_first_child(element, "Name")) or element.attrib.get("Name"),
        "name": text_of(find_first_child(element, "GraphicObjectName")) or text_of(find_first_child(element, "Tag")),
        "tag": text_of(find_first_child(element, "Tag")),
        "type": text_of(find_first_child(element, "Type")) or element.attrib.get("Type"),
        "object_class": text_of(find_first_child(element, "ObjectClass")),
        "component_description": text_of(find_first_child(element, "ComponentDescription")),
    }
    return {key: value for key, value in fields.items() if value}


def summarize_connectors(graphic_object: ET.Element) -> dict[str, object]:
    summary: dict[str, object] = {
        "name": text_of(find_first_child(graphic_object, "Name")) or graphic_object.attrib.get("Name"),
        "tag": text_of(find_first_child(graphic_object, "Tag")),
        "type": text_of(find_first_child(graphic_object, "ObjectType")) or graphic_object.attrib.get("Type"),
        "input_connectors": [],
        "output_connectors": [],
    }
    for section_name, output_key in (("InputConnectors", "input_connectors"), ("OutputConnectors", "output_connectors")):
        section = find_first_child(graphic_object, section_name)
        connectors: list[dict[str, object]] = []
        if section is not None:
            for connector in section:
                connector_summary = {
                    "tag": local_name(connector.tag),
                    "attributes": dict(connector.attrib),
                    "children": child_names(connector),
                }
                connectors.append(connector_summary)
        summary[output_key] = connectors
    return summary


def write_observations(root: ET.Element, metadata: dict[str, object], public_dir: Path) -> dict[str, object]:
    simulation_objects = find_first_child(root, "SimulationObjects")
    graphic_objects = find_first_child(root, "GraphicObjects")
    settings = find_first_child(root, "Settings")
    property_packages = find_first_child(root, "PropertyPackages")
    compounds = find_first_child(root, "Compounds")
    messages = find_first_child(root, "MessagesLog")

    objects = [summarize_object(child) for child in simulation_objects] if simulation_objects is not None else []
    graphics = [summarize_connectors(child) for child in graphic_objects] if graphic_objects is not None else []

    unsupported_sections = [
        section
        for section in metadata.get("sections", [])
        if section
        not in {
            "GeneralInfo",
            "SimulationObjects",
            "Settings",
            "GraphicObjects",
            "PropertyPackages",
            "Compounds",
            "ReactionSets",
            "Reactions",
            "Spreadsheet",
            "MessagesLog",
        }
    ]

    topology = {
        "schema_version": "draft-0",
        "extraction_note": "Topology combines SimulationObjects with GraphicObjects connector summaries.",
        "simulation_object_count": len(objects),
        "graphic_object_count": len(graphics),
        "objects": objects,
        "graphic_objects": graphics,
        "unresolved_connector_references": [],
    }
    parameters = {
        "schema_version": "draft-0",
        "extraction_note": "Unit parameters are semi-structured until category-specific schemas are induced.",
        "settings_sections": child_names(settings),
        "property_package_count": len(property_packages) if property_packages is not None else 0,
        "compound_count": len(compounds) if compounds is not None else 0,
        "unit_operation_summaries": objects,
        "unsupported_sections": unsupported_sections,
    }

    (public_dir / "topology.json").write_text(json.dumps(topology, indent=2, sort_keys=True) + "\n")
    (public_dir / "parameters.json").write_text(json.dumps(parameters, indent=2, sort_keys=True) + "\n")
    (public_dir / "log.txt").write_text((ET.tostring(messages, encoding="unicode") if messages is not None else "") + "\n")

    with (public_dir / "streams.csv").open("w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=["name", "tag", "type", "object_class", "component_description"])
        writer.writeheader()
        for obj in objects:
            if "MaterialStream" in str(obj.get("type", "")) or "MaterialStream" in str(obj.get("object_class", "")):
                writer.writerow({key: obj.get(key, "") for key in writer.fieldnames or []})

    metadata["object_count"] = len(objects)
    metadata["unsupported_sections"] = unsupported_sections
    return metadata


def update_manifest(instance_path: Path, base_path: Path, faulty_path: Path, metadata: dict[str, object]) -> None:
    instance = json.loads(instance_path.read_text())
    public_dir = faulty_path.parent
    instance["base_flowsheet"] = relative_ref(instance_path, base_path)
    instance["faulty_flowsheet"] = relative_ref(instance_path, faulty_path)
    instance["observations"] = {
        "topology": relative_ref(instance_path, public_dir / "topology.json"),
        "parameters": relative_ref(instance_path, public_dir / "parameters.json"),
        "simulator_log": relative_ref(instance_path, public_dir / "log.txt"),
        "stream_table": relative_ref(instance_path, public_dir / "streams.csv"),
    }
    flags = set(instance.get("leakage_flags", []))
    flags.add("unfaulted_placeholder_until_fault_injection")
    instance["leakage_flags"] = sorted(flags)
    instance["source"] = {
        "source_format": metadata["source_format"],
        "source_name": SOURCE_NAME,
        "source_url": SOURCE_URL,
        "license": LICENSE,
        "retrieved_at": date.today().isoformat(),
        "dwsim_build_version": "DWSIM v4.2",
        "internal_archive_entries": metadata.get("internal_archive_entries", []),
        "contains_database": metadata.get("contains_database", False),
        "root_element": metadata.get("root_element"),
        "sections": metadata.get("sections", []),
        "object_count": metadata.get("object_count", 0),
        "unsupported_sections": metadata.get("unsupported_sections", []),
    }
    base_hash = sha256(base_path)
    faulty_hash = sha256(faulty_path)
    instance["reproducibility"] = {
        "base_flowsheet_sha256": base_hash,
        "faulty_flowsheet_sha256": faulty_hash,
        "fault_injector_version": "seed-unfaulted-copy",
        "observation_extractor_version": "prepare_dwsim_seed.py:0",
        "executor_version": "deferred-next-phase",
        "dwsim_runner_version": "deferred-next-phase",
        "evaluator_version": "deferred-next-phase",
    }
    instance_path.write_text(json.dumps(instance, indent=2, sort_keys=True) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("download", type=Path)
    parser.add_argument(
        "--instance",
        type=Path,
        default=Path("instances/legacy/distillation_001_feed_stage_single/instance.json"),
    )
    parser.add_argument("--hidden-dir", type=Path, default=Path("instances/legacy/distillation_001_feed_stage_single/hidden"))
    parser.add_argument("--public-dir", type=Path, default=Path("instances/legacy/distillation_001_feed_stage_single/public"))
    args = parser.parse_args()

    args.hidden_dir.mkdir(parents=True, exist_ok=True)
    args.public_dir.mkdir(parents=True, exist_ok=True)

    extracted = extract_dwsim_file(args.download, args.hidden_dir)
    base_path = args.hidden_dir / f"base{extracted.suffix.lower()}"
    if extracted != base_path:
        extracted.replace(base_path)

    faulty_path = args.public_dir / f"fault_feed_stage{base_path.suffix.lower()}"
    shutil.copyfile(base_path, faulty_path)

    root, metadata = read_dwsim_xml(base_path)
    metadata = write_observations(root, metadata, args.public_dir)
    update_manifest(args.instance, base_path, faulty_path, metadata)

    print(f"Prepared DWSIM seed from {args.download}")
    print(f"Base flowsheet: {base_path}")
    print(f"Observation directory: {args.public_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
