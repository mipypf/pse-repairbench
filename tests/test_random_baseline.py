from __future__ import annotations

import argparse
import copy
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "baselines"))

import run_random_baseline as baseline  # noqa: E402
from evaluate_repair_output import repair_output_validator  # noqa: E402


def public_parameters() -> dict:
    return {
        "allowed_repair_actions": [
            {"target": {"kind": "unit_operation", "guid": "heater"}, "parameter": {"namespace": "thermal_specification", "name": "outlet_temperature"}, "unit": "K"},
            {"target": {"kind": "unit_operation", "guid": "column"}, "parameter": {"namespace": "column_configuration", "name": "feed_stage"}, "unit": None},
        ],
        "observed_candidate_units": [
            {"guid": "heater", "type": "DWSIM.UnitOperations.UnitOperations.Heater", "outlet_temperature": 10.0},
            {"guid": "column", "type": "DWSIM.UnitOperations.UnitOperations.DistillationColumn", "feed_stage": 1, "number_of_stages": 2},
        ],
    }


class RandomBaselineTest(unittest.TestCase):
    def setUp(self) -> None:
        self.config = baseline.load_json(baseline.DEFAULT_CONFIG)

    def test_public_preflight_rejects_missing_values_duplicates_and_fallbacks(self) -> None:
        for mutation in ("missing_current", "duplicate_pair", "duplicate_unit", "missing_allowed", "missing_candidates"):
            with self.subTest(mutation=mutation):
                parameters = public_parameters()
                if mutation == "missing_current":
                    del parameters["observed_candidate_units"][0]["outlet_temperature"]
                elif mutation == "duplicate_pair":
                    parameters["allowed_repair_actions"].append(copy.deepcopy(parameters["allowed_repair_actions"][0]))
                elif mutation == "duplicate_unit":
                    parameters["observed_candidate_units"].append(copy.deepcopy(parameters["observed_candidate_units"][0]))
                elif mutation == "missing_allowed":
                    del parameters["allowed_repair_actions"]
                else:
                    del parameters["observed_candidate_units"]
                with self.assertRaises(ValueError):
                    baseline.preflight_parameters(parameters, self.config)

    def test_candidate_order_and_unrelated_gold_fields_do_not_change_proposals(self) -> None:
        original = public_parameters()
        changed = copy.deepcopy(original)
        changed["allowed_repair_actions"].reverse()
        changed["observed_candidate_units"].reverse()
        changed["gold_repair_actions"] = [{"value": 999999}]
        changed["fault_direction"] = "increase"
        candidates = baseline.preflight_parameters(original, self.config)
        reordered = baseline.preflight_parameters(changed, self.config)
        for seed in range(5):
            self.assertEqual(
                baseline.sample_proposal(candidates, self.config["protocol_id"], seed, "task"),
                baseline.sample_proposal(reordered, self.config["protocol_id"], seed, "task"),
            )

    def test_temperature_positive_boundary_and_feed_stage_exclusion(self) -> None:
        candidates = baseline.preflight_parameters(public_parameters(), self.config)
        feed = next(candidate for candidate in candidates if candidate[0]["parameter"]["name"] == "feed_stage")
        self.assertEqual(feed[2]["values"], [2])
        thermal = next(candidate for candidate in candidates if candidate[0]["parameter"]["name"] == "outlet_temperature")
        self.assertEqual((thermal[2]["lower"], thermal[2]["upper"]), (0.0, 40.0))
        with mock.patch.object(baseline.random, "Random") as random_class:
            random_class.return_value.randrange.return_value = 0
            random_class.return_value.random.return_value = 0.0
            payload, _metadata = baseline.sample_proposal([thermal], "v1", 0, "task")
        self.assertGreater(payload["repair_actions"][0]["value"], 0)
        self.assertFalse(list(repair_output_validator(ROOT).iter_errors(payload)))

    def test_pressure_and_reflux_log_bounds(self) -> None:
        for key, field, unit_type, upper_multiplier in (
            ("pressure_specification/outlet_pressure", "pout", "Pump", 2),
            ("separator_specification/pressure", "flash_pressure", "Vessel", 2),
            ("column_specification/reflux_ratio", "reflux_ratio", "DistillationColumn", 10),
        ):
            with self.subTest(key=key):
                namespace, name = key.split("/")
                pair = {"target": {"kind": "unit_operation", "guid": "unit"}, "parameter": {"namespace": namespace, "name": name}, "unit": None if name == "reflux_ratio" else "Pa"}
                current, domain = baseline.pair_domain(pair, {"type": f"DWSIM.UnitOperations.UnitOperations.{unit_type}", field: 3.0}, self.config)
                self.assertEqual((domain["lower"], domain["upper"]), (2.0, 3.0 * upper_multiplier))
                with mock.patch.object(baseline.random, "Random") as random_class:
                    random_class.return_value.randrange.return_value = 0
                    for quantile in (0.0, 0.5, 1.0):
                        random_class.return_value.random.return_value = quantile
                        payload, _metadata = baseline.sample_proposal([(pair, current, domain)], "v1", 0, "task")
                        value = payload["repair_actions"][0]["value"]
                        self.assertGreaterEqual(value, domain["lower"])
                        self.assertLessEqual(value, domain["upper"])
                        if quantile == 0.5:
                            self.assertAlmostEqual(value, (domain["lower"] * domain["upper"]) ** 0.5)

    def test_frozen_generation_is_path_independent_and_detects_tampering_before_evaluation(self) -> None:
        (ROOT / ".tmp").mkdir(exist_ok=True)
        with tempfile.TemporaryDirectory(prefix="random_baseline_test_", dir=ROOT / ".tmp") as directory:
            work = Path(directory)
            fixture = work / "instances" / "task"
            (fixture / "public").mkdir(parents=True)
            baseline.write_json(fixture / "public" / "parameters.json", public_parameters())
            instance = {"id": "task", "observations": {"parameters": "public/parameters.json"}, "gold_repair_actions": [{"value": 1}]}
            baseline.write_json(fixture / "instance.json", instance)
            config = {**self.config, "instance_root": baseline.relative_path(work / "instances")}
            baseline.write_json(work / "config.json", config)
            (work / "dev.txt").write_text("task\n", encoding="utf-8")
            for name, gold_value, git_error in (
                ("first", 1, baseline.subprocess.CalledProcessError(128, ["git", "rev-parse", "HEAD"])),
                ("second", 9000, FileNotFoundError("git is not installed")),
            ):
                instance["gold_repair_actions"][0]["value"] = gold_value
                baseline.write_json(fixture / "instance.json", instance)
                with mock.patch.object(baseline.subprocess, "check_output", side_effect=git_error):
                    baseline.generate(argparse.Namespace(config=work / "config.json", split_file=work / "dev.txt", limit=None, run_dir=work / name))
            first, _config = baseline.verify_saved_run(work / "first")
            second, _config = baseline.verify_saved_run(work / "second")
            self.assertEqual([row["proposal_sha256"] for row in first["proposals"]], [row["proposal_sha256"] for row in second["proposals"]])
            self.assertEqual(len(first["proposals"]), 5)
            self.assertIsNone(first["git_commit"])
            self.assertIsNone(second["git_commit"])
            with (
                mock.patch.object(baseline.subprocess, "check_output", side_effect=FileNotFoundError("git is not installed")),
                mock.patch.object(baseline, "evaluate", return_value=({"executable_success": False}, 1)) as evaluator,
                mock.patch.object(baseline, "row_from_report", return_value={"executable_success": False}),
            ):
                baseline.evaluate_saved(argparse.Namespace(run_dir=work / "second"))
                self.assertEqual(evaluator.call_count, 5)
            for seed in range(5):
                summary = baseline.load_json(work / "second" / f"seed_{seed}" / "aggregate.json")
                self.assertIsNone(summary["generation_git_commit"])
                self.assertIsNone(summary["evaluation_git_commit"])
                self.assertEqual(summary["instance_count"], 1)
            proposal_path = work / "first" / first["proposals"][0]["proposal_path"]
            payload = json.loads(proposal_path.read_text(encoding="utf-8"))
            payload["repair_actions"][0]["value"] = 0
            baseline.write_json(proposal_path, payload)
            with mock.patch.object(baseline, "evaluate") as evaluator:
                with self.assertRaisesRegex(ValueError, "proposal or public input changed"):
                    baseline.evaluate_saved(argparse.Namespace(run_dir=work / "first"))
                evaluator.assert_not_called()


if __name__ == "__main__":
    unittest.main()
