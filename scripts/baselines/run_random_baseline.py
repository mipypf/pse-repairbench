#!/usr/bin/env python3
"""Generate frozen one-shot random repairs, then evaluate the saved proposals."""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import platform
import random
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "llm"))
sys.path.insert(0, str(ROOT / "scripts" / "evaluate"))

from evaluate_repair_output import evaluate, load_json, write_json  # noqa: E402
from evaluate_release_set import aggregate, row_from_report, write_csv  # noqa: E402
from generate_llm_input import (  # noqa: E402
    allowed_repair_actions_from_parameters,
    observed_candidate_units_from_parameters,
)
from repair_registry import parameter_key_text  # noqa: E402

DEFAULT_CONFIG = Path(__file__).with_name("random_baseline_final_v0_1_5.json")


def git_commit() -> str | None:
    """Record the checkout revision when available, including ZIP-only runs."""
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=ROOT, text=True,
            stderr=subprocess.DEVNULL,
        ).strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def relative_path(path: Path) -> str:
    return path.resolve().relative_to(ROOT).as_posix()


def pair_key(pair: dict[str, Any]) -> tuple[str, str, str, str]:
    return (
        pair["target"]["kind"], pair["target"]["guid"],
        pair["parameter"]["namespace"], pair["parameter"]["name"],
    )


def task_seed(protocol_id: str, seed: int, instance_id: str) -> int:
    identity = f"{protocol_id}\n{seed}\n{instance_id}".encode("utf-8")
    return int.from_bytes(hashlib.sha256(identity).digest(), "big")


def pair_domain(pair: dict[str, Any], unit: dict[str, Any], config: dict[str, Any]) -> tuple[int | float, dict[str, Any]]:
    key = parameter_key_text(pair["parameter"])
    if key == "pressure_specification/outlet_pressure":
        fields = {
            "DWSIM.UnitOperations.UnitOperations.Valve": "outlet_pressure",
            "DWSIM.UnitOperations.UnitOperations.Pump": "pout",
            "DWSIM.UnitOperations.UnitOperations.Compressor": "p_out",
        }
        field = fields.get(unit.get("type"))
    else:
        field = {
            "thermal_specification/outlet_temperature": "outlet_temperature",
            "separator_specification/temperature": "flash_temperature",
            "separator_specification/pressure": "flash_pressure",
            "column_specification/reflux_ratio": "reflux_ratio",
            "column_configuration/feed_stage": "feed_stage",
        }.get(key)
    current = unit.get(field) if field else None
    if isinstance(current, bool) or not isinstance(current, (int, float)) or not math.isfinite(current) or current <= 0:
        raise ValueError(f"missing or invalid current value for {pair_key(pair)}")
    if key == "column_configuration/feed_stage":
        count = unit.get("number_of_stages")
        if isinstance(count, bool) or not isinstance(count, int) or count < 2 or not isinstance(current, int) or current > count:
            raise ValueError(f"invalid feed-stage candidate range for {pair_key(pair)}")
        return current, {"distribution": "discrete_uniform", "values": [stage for stage in range(1, count + 1) if stage != current]}
    if key in {"thermal_specification/outlet_temperature", "separator_specification/temperature"}:
        offset = config["temperature_offset_k"]
        lower, upper = max(0.0, current - offset), current + offset
        distribution = "continuous_uniform_positive"
    else:
        multipliers = config["reflux_multipliers"] if key == "column_specification/reflux_ratio" else config["pressure_multipliers"]
        lower, upper = current * multipliers[0], current * multipliers[1]
        distribution = "log_uniform"
    if not math.isfinite(lower) or not math.isfinite(upper) or upper <= lower or (distribution == "log_uniform" and lower <= 0):
        raise ValueError(f"invalid sampling bounds for {pair_key(pair)}")
    return current, {"distribution": distribution, "lower": lower, "upper": upper}


def preflight_parameters(parameters: dict[str, Any], config: dict[str, Any]) -> list[tuple[dict[str, Any], int | float, dict[str, Any]]]:
    raw_pairs = parameters.get("allowed_repair_actions")
    raw_units = parameters.get("observed_candidate_units")
    if not isinstance(raw_pairs, list) or len(raw_pairs) < 2 or not all(isinstance(pair, dict) for pair in raw_pairs):
        raise ValueError("explicit public allowed_repair_actions with at least two pairs required; no gold fallback")
    if not isinstance(raw_units, list) or not raw_units or not all(isinstance(unit, dict) and isinstance(unit.get("guid"), str) for unit in raw_units):
        raise ValueError("explicit public observed_candidate_units required; no target-unit fallback")
    pairs = allowed_repair_actions_from_parameters({}, parameters)
    if len({pair_key(pair) for pair in pairs}) != len(pairs):
        raise ValueError("duplicate allowed target-parameter pair")
    units = observed_candidate_units_from_parameters(parameters, pairs)
    by_guid = {unit["guid"]: unit for unit in units}
    if len(by_guid) != len(units):
        raise ValueError("duplicate observed candidate GUID")
    for raw_pair, pair in zip(raw_pairs, pairs):
        if raw_pair.get("unit") != pair["unit"] or pair["target"]["kind"] != "unit_operation":
            raise ValueError("invalid public allowed action unit or target kind")
    return [(pair, *pair_domain(pair, by_guid[pair["target"]["guid"]], config)) for pair in sorted(pairs, key=pair_key)]


def sample_proposal(candidates: list[tuple[dict[str, Any], int | float, dict[str, Any]]], protocol_id: str, seed: int, instance_id: str) -> tuple[dict[str, Any], dict[str, Any]]:
    derived_seed = task_seed(protocol_id, seed, instance_id)
    rng = random.Random(derived_seed)
    pair, current, domain = candidates[rng.randrange(len(candidates))]
    if domain["distribution"] == "discrete_uniform":
        value = rng.choice(domain["values"])
    elif domain["distribution"] == "log_uniform":
        value = math.exp(math.log(domain["lower"]) + rng.random() * (math.log(domain["upper"]) - math.log(domain["lower"])))
        value = min(domain["upper"], max(domain["lower"], value))
    else:
        value = domain["lower"] + rng.random() * (domain["upper"] - domain["lower"])
        if value <= 0:
            value = math.nextafter(0.0, domain["upper"])
    target = {key: pair["target"][key] for key in ("kind", "guid", "tag") if key in pair["target"]}
    payload = {
        "diagnosis": "One-shot random baseline from public candidate parameters.",
        "repair_actions": [{"type": "set_unit_parameter", "target": target, "parameter": pair["parameter"], "value": value, "unit": pair["unit"]}],
        "rationale": "Uniform target-parameter pair selection and a frozen random value; no simulator feedback.",
    }
    return payload, {"task_seed": str(derived_seed), "candidate_pair_count": len(candidates), "current_value": current, "sampling_domain": domain}


def generate(args: argparse.Namespace) -> None:
    config = load_json(args.config)
    if config["seeds"] != [0, 1, 2, 3, 4]:
        raise ValueError("this protocol requires the five fixed seeds 0 through 4")
    if args.split_file is not None and args.split_file.stem != "dev":
        raise ValueError("--split-file overrides are only supported for dev checks")
    split_file = args.split_file or ROOT / config["split_file"]
    ids = sorted(line.strip() for line in split_file.read_text(encoding="utf-8").splitlines() if line.strip())
    if not ids or len(set(ids)) != len(ids):
        raise ValueError("split must contain unique nonempty instance ids")
    if args.split_file is None and len(ids) != config["expected_instance_count"]:
        raise ValueError("official split instance count does not match config")
    if args.limit is not None:
        if split_file.stem != "dev" or args.limit < 1:
            raise ValueError("--limit is only supported for positive-size dev smoke checks")
        ids = ids[:args.limit]
    # Check every pair in every task before writing any proposals. Never drop a pair.
    tasks = []
    for instance_id in ids:
        instance_path = ROOT / config["instance_root"] / instance_id / "instance.json"
        instance = load_json(instance_path)
        if instance.get("id") != instance_id:
            raise ValueError(f"split id does not match instance id: {instance_id}")
        parameters_path = instance_path.parent / instance["observations"]["parameters"]
        if not parameters_path.resolve().is_relative_to((instance_path.parent / "public").resolve()):
            raise ValueError("parameters must come from this instance's public directory")
        parameters = load_json(parameters_path)
        candidates = preflight_parameters(parameters, config)
        tasks.append((instance_id, instance_path, parameters_path, candidates))
    if args.run_dir.exists():
        raise ValueError("run directory already exists; use a fresh directory")
    args.run_dir.mkdir(parents=True)
    (args.run_dir / "config.json").write_bytes(args.config.read_bytes())
    manifest = {
        "protocol_id": config["protocol_id"],
        "dataset_split_id": config["dataset_split_id"] if args.split_file is None else f"final_v0_1_5_{split_file.stem}",
        "config_sha256": sha256(args.config), "split_file": relative_path(split_file), "split_sha256": sha256(split_file),
        "git_commit": git_commit(),
        "generator_sha256": sha256(Path(__file__)), "python_version": platform.python_version(),
        "seeds": config["seeds"], "instance_count": len(tasks), "proposals": [],
    }
    for seed in config["seeds"]:
        for instance_id, instance_path, parameters_path, candidates in tasks:
            short_id = hashlib.sha256(instance_id.encode("utf-8")).hexdigest()[:12]
            proposal_path = args.run_dir / f"seed_{seed}" / f"instance_{short_id}" / "repair_output.json"
            payload, metadata = sample_proposal(candidates, config["protocol_id"], seed, instance_id)
            write_json(proposal_path, payload)
            manifest["proposals"].append({
                "seed": seed, "instance_id": instance_id, "instance_path": relative_path(instance_path),
                "parameters_path": relative_path(parameters_path), "input_sha256": sha256(parameters_path),
                "proposal_path": proposal_path.relative_to(args.run_dir).as_posix(), "proposal_sha256": sha256(proposal_path),
                **metadata,
            })
    write_json(args.run_dir / "generation_manifest.json", manifest)
    print(f"Saved {len(manifest['proposals'])} proposals without DWSIM: {args.run_dir}")


def verify_saved_run(run_dir: Path) -> tuple[dict[str, Any], dict[str, Any]]:
    manifest = load_json(run_dir / "generation_manifest.json")
    config = load_json(run_dir / "config.json")
    if sha256(run_dir / "config.json") != manifest["config_sha256"] or sha256(Path(__file__)) != manifest["generator_sha256"]:
        raise ValueError("saved config or generator hash mismatch")
    if sha256(ROOT / manifest["split_file"]) != manifest["split_sha256"]:
        raise ValueError("split changed since generation")
    identities = {(row["seed"], row["instance_id"]) for row in manifest["proposals"]}
    if len(identities) != len(manifest["proposals"]) or len(identities) != len(manifest["seeds"]) * manifest["instance_count"]:
        raise ValueError("incomplete or duplicate saved proposal set")
    for row in manifest["proposals"]:
        proposal = (run_dir / row["proposal_path"]).resolve()
        if not proposal.is_relative_to(run_dir.resolve()):
            raise ValueError("saved proposal path is outside run directory")
        if sha256(proposal) != row["proposal_sha256"] or sha256(ROOT / row["parameters_path"]) != row["input_sha256"]:
            raise ValueError(f"saved proposal or public input changed: {row['instance_id']}")
        if (proposal.parent / "evaluation_report.json").exists():
            raise ValueError("evaluation report already exists; saved proposals are evaluated only once")
    return manifest, config


def evaluate_saved(args: argparse.Namespace) -> None:
    # Verify the complete frozen proposal set before the first simulator invocation.
    manifest, config = verify_saved_run(args.run_dir)
    evaluation_git_commit = git_commit()
    evaluation_python_version = platform.python_version()
    for seed in manifest["seeds"]:
        rows = []
        for proposal in manifest["proposals"]:
            if proposal["seed"] != seed:
                continue
            instance_path = ROOT / proposal["instance_path"]
            output_path = args.run_dir / proposal["proposal_path"]
            report_path = output_path.parent / "evaluation_report.json"
            single_args = argparse.Namespace(
                instance=instance_path, repair_output_json=output_path,
                work_dir=output_path.parent / "evaluation_work", require_success=False,
                executor_timeout_sec=config["executor_timeout_sec"], dwsim_timeout_sec=config["dwsim_timeout_sec"],
            )
            report, _exit_code = evaluate(single_args, report_path)
            write_json(report_path, report)
            rows.append(row_from_report(instance_path, load_json(instance_path), output_path, report_path, report))
            print(f"seed={seed} {proposal['instance_id']}: executable_success={report.get('executable_success')} error_stage={report.get('error_stage')}")
        summary = aggregate(manifest["protocol_id"], rows)
        summary.update({"seed": seed, "dataset_split_id": manifest["dataset_split_id"], "generation_git_commit": manifest["git_commit"], "evaluation_git_commit": evaluation_git_commit, "evaluation_python_version": evaluation_python_version, "generation_manifest_sha256": sha256(args.run_dir / "generation_manifest.json")})
        write_json(args.run_dir / f"seed_{seed}" / "aggregate.json", summary)
        write_csv(args.run_dir / f"seed_{seed}" / "aggregate.csv", rows)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--phase", required=True, choices=["generate", "evaluate"])
    parser.add_argument("--run-dir", required=True, type=Path)
    parser.add_argument("--config", default=DEFAULT_CONFIG, type=Path)
    parser.add_argument("--split-file", type=Path, help="override only for dev checks; official test uses config")
    parser.add_argument("--limit", type=int, help="limit dev smoke-check tasks")
    args = parser.parse_args()
    try:
        if args.phase == "generate":
            generate(args)
        else:
            if args.split_file is not None or args.limit is not None:
                raise ValueError("evaluation uses the saved generation manifest, not new task selection")
            evaluate_saved(args)
    except (ValueError, KeyError, OSError, subprocess.CalledProcessError) as exc:
        print(f"Random baseline stopped: {exc}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
