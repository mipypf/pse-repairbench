from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts" / "llm"))

import generate_llm_input as packets  # noqa: E402
import generate_llm_output as outputs  # noqa: E402
import run_gemini_pilot_batch as batch  # noqa: E402
from llm_provider import ProviderConfigError  # noqa: E402

INSTANCE = ROOT / "instances/final_v0_1_5/candidate_pool" / (
    "001_4_step_refrigeration_cycle_with_propylene_ethylene_methane_and_nitrogen_"
    "ht_01_outlet_temperature_001/instance.json"
)


class PromptLogAblationTest(unittest.TestCase):
    def setUp(self) -> None:
        test_root = ROOT / ".tmp/unit_tests"
        test_root.mkdir(parents=True, exist_ok=True)
        self.work = Path(tempfile.mkdtemp(prefix="prompt_ablation_", dir=test_root))

    def args(self, omit: bool = True, dry: bool = True) -> argparse.Namespace:
        return argparse.Namespace(
            work_dir=self.work, provider="openai", model="gpt-5.5",
            prompt_mode="parameter-selection", omit_simulator_log=omit,
            provider_call_delay_sec=0.0, dry_run_sanitize=dry,
            env_file=self.work / "absent.env", require_success=False,
            executor_timeout_sec=60, dwsim_timeout_sec=180,
            dataset_split_id="final_v0_1_5_test", git_commit="test",
        )

    def test_default_packet_snapshot_and_log_only_removal(self) -> None:
        full = self.work / "full.md"
        explicit_full = self.work / "explicit_full.md"
        omitted = self.work / "omitted.md"
        packets.generate(INSTANCE, full, "parameter-selection")
        packets.generate(INSTANCE, explicit_full, "parameter-selection", False)
        packets.generate(INSTANCE, omitted, "parameter-selection", True)
        self.assertEqual(full.read_bytes(), explicit_full.read_bytes())
        full_text = full.read_text(encoding="utf-8")
        # Snapshot from the pre-ablation generator, with universal-newline reading.
        self.assertEqual(hashlib.sha256(full_text.encode()).hexdigest(),
                         "184dc5dfe684552dfb289c780b5438d06afc8ab6abfa67626e871aa227216751")
        start = full_text.index("## Faulty Simulator Log\n")
        end = full_text.index("## Allowed Repair Actions\n", start)
        self.assertEqual(omitted.read_text(encoding="utf-8"), full_text[:start] + full_text[end:])

    def test_dry_run_records_condition_and_preserves_schema_hash(self) -> None:
        rows = []
        with mock.patch.object(outputs, "load_api_key", side_effect=AssertionError("API key read")), \
             mock.patch.object(outputs, "call_provider_with_metadata", side_effect=AssertionError("API call")), \
             mock.patch.object(batch, "evaluate_generated_output", side_effect=AssertionError("DWSIM call")):
            for omit in (False, True):
                args = self.args(omit=omit)
                args.work_dir = self.work / str(omit)
                row, code = batch.run_instance(args, INSTANCE)
                self.assertEqual(code, 0)
                self.assertEqual(row["omit_simulator_log"], omit)
                metadata = json.loads(Path(row["llm_metadata"]).read_text(encoding="utf-8"))
                self.assertEqual(metadata["omit_simulator_log"], omit)
                self.assertEqual(metadata["validation_status"], "dry_run")
                prompt = Path(row["sanitized_prompt"]).read_text(encoding="utf-8")
                self.assertEqual("## Faulty Simulator Log" in prompt, not omit)
                self.assertEqual(metadata["prompt_hash"], outputs.sha256_text(prompt))
                summary = batch.aggregate([row], args.provider, args.model, True,
                                          args.dataset_split_id, args.git_commit, 0.0, omit)
                self.assertEqual(summary["omit_simulator_log"], omit)
                self.assertEqual(summary["llm_run_config"]["omit_simulator_log"], omit)
                batch.write_csv(args.work_dir / "aggregate.csv", [row])
                self.assertIn("omit_simulator_log", (args.work_dir / "aggregate.csv").read_text(encoding="utf-8"))
                rows.append(row)
        self.assertEqual(rows[0]["schema_hash"], rows[1]["schema_hash"])
        self.assertNotEqual(rows[0]["prompt_hash"], rows[1]["prompt_hash"])

    def test_provider_failure_retains_metadata_and_condition(self) -> None:
        with mock.patch.object(outputs, "load_api_key", side_effect=ProviderConfigError("test config failure")), \
             mock.patch.object(outputs, "call_provider_with_metadata", side_effect=AssertionError("API call")), \
             mock.patch.object(batch, "evaluate_generated_output", side_effect=AssertionError("DWSIM call")):
            row, code = batch.run_instance(self.args(dry=False), INSTANCE)
        self.assertEqual(code, 1)
        self.assertTrue(row["omit_simulator_log"])
        self.assertEqual(row["failure_type"], "provider_config_failure")
        metadata = json.loads(Path(row["llm_metadata"]).read_text(encoding="utf-8"))
        self.assertTrue(metadata["omit_simulator_log"])
        self.assertEqual(metadata["provider_error"]["type"], "provider_config")
        self.assertEqual(metadata["prompt_hash"], row["prompt_hash"])

    def test_input_failure_replaces_stale_metadata(self) -> None:
        invalid = self.work / "input/instance.json"
        invalid.parent.mkdir()
        invalid.write_text(json.dumps({"id": "custom_identity", "observations": None}))
        item = batch.instance_work_dir(self.work, invalid, {"id": "custom_identity"})
        item.mkdir()
        (item / "llm_metadata.json").write_text(json.dumps({"prompt_hash": "stale"}))
        with mock.patch.object(batch, "generate_llm_output", side_effect=AssertionError("provider generation")):
            row, code = batch.run_instance(self.args(), invalid)
        self.assertEqual(code, 1)
        self.assertTrue(row["omit_simulator_log"])
        self.assertIsNone(row["prompt_hash"])
        self.assertEqual(json.loads(Path(row["llm_metadata"]).read_text()), {"omit_simulator_log": True})

    def test_cli_alias_propagates_flag_and_rejects_oracle_mode(self) -> None:
        command = [sys.executable, str(ROOT / "scripts/llm/run_llm_pilot_batch.py"),
                   "--instances", str(INSTANCE), "--work-dir", str(self.work),
                   "--provider", "openai", "--model", "gpt-5.5",
                   "--omit-simulator-log", "--dry-run-sanitize"]
        rejected = subprocess.run(command, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(rejected.returncode, 2)
        self.assertIn("requires --prompt-mode parameter-selection", rejected.stderr)
        self.assertFalse((self.work / "aggregate.json").exists())
        completed = subprocess.run(command + ["--prompt-mode", "parameter-selection"],
                                   cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(completed.returncode, 0, completed.stderr)
        summary = json.loads((self.work / "aggregate.json").read_text())
        self.assertTrue(summary["omit_simulator_log"])
        self.assertTrue(summary["rows"][0]["omit_simulator_log"])
        with self.assertRaisesRegex(ValueError, "requires --prompt-mode"):
            packets.generate(self.work / "missing.json", self.work / "bad.md", omit_simulator_log=True)


if __name__ == "__main__":
    unittest.main()
