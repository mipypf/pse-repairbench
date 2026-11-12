from __future__ import annotations

import subprocess
import shutil
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
sys.path.insert(0, str(ROOT / "scripts" / "evaluate"))
sys.path.insert(0, str(ROOT / "scripts" / "build_instances"))
sys.path.insert(0, str(ROOT / "scripts" / "llm"))

from builder_common import sanitize_artifact_paths  # noqa: E402
from dwsim_run_contract import is_successful_dwsim_run  # noqa: E402
import evaluate_repair_output as evaluator  # noqa: E402
from run_gemini_pilot_batch import failure_type  # noqa: E402


def workspace_test_dir(name: str) -> Path:
    root = ROOT / ".tmp" / "unit_tests" / name
    if root.exists():
        shutil.rmtree(root)
    root.mkdir(parents=True)
    return root


class EvaluationContractTest(unittest.TestCase):
    def test_dwsim_run_success_requires_solver_success_and_no_exceptions(self) -> None:
        self.assertTrue(
            is_successful_dwsim_run(
                {"status": "success", "success": True, "solved_after": True, "exception_count": 0}
            )
        )
        self.assertFalse(
            is_successful_dwsim_run(
                {"status": "calculation_failed", "success": True, "solved_after": True, "exception_count": 0}
            )
        )
        self.assertFalse(
            is_successful_dwsim_run(
                {"status": "success", "success": False, "solved_after": True, "exception_count": 0}
            )
        )
        self.assertFalse(
            is_successful_dwsim_run(
                {"status": "success", "success": True, "solved_after": False, "exception_count": 0}
            )
        )
        self.assertFalse(
            is_successful_dwsim_run(
                {"status": "success", "success": True, "solved_after": True, "exception_count": 1}
            )
        )

    def test_timeout_failure_types_are_preserved(self) -> None:
        self.assertEqual(failure_type({"error_stage": "executor_timeout"}), "executor_timeout")
        self.assertEqual(failure_type({"error_stage": "dwsim_timeout"}), "dwsim_timeout")

    def test_sanitize_artifact_paths_removes_workspace_prefix(self) -> None:
        raw = str(ROOT / "curated_data" / "dwsim_headless_successes" / "example.zip")
        data = {"source": {"curated_archive": raw}}
        self.assertEqual(
            sanitize_artifact_paths(data),
            {"source": {"curated_archive": "curated_data/dwsim_headless_successes/example.zip"}},
        )

    def test_executor_does_not_accept_stale_repaired_flowsheet(self) -> None:
        work = workspace_test_dir("stale_executor")
        try:
            repaired = work / "repaired.dwxmz"
            repaired.write_text("stale", encoding="utf-8")
            completed = subprocess.CompletedProcess(args=["mock"], returncode=0, stdout="", stderr="")

            with mock.patch.object(evaluator, "run_command", return_value=completed):
                result = evaluator.apply_repair_action(
                    work / "faulty.dwxmz",
                    repaired,
                    work / "repair_output.json",
                    timeout_sec=1,
                )

            self.assertFalse(repaired.exists())
            self.assertFalse(result["success"])
        finally:
            shutil.rmtree(work, ignore_errors=True)

    def test_dwsim_metrics_does_not_accept_stale_run_json(self) -> None:
        work = workspace_test_dir("stale_metrics")
        try:
            repaired_run = work / "repaired_run.json"
            calculated = work / "repaired_calculated.dwxmz"
            repaired_run.write_text(
                '{"status":"success","success":true,"solved_after":true,"exception_count":0}',
                encoding="utf-8",
            )
            calculated.write_text("stale", encoding="utf-8")
            completed = subprocess.CompletedProcess(args=["mock"], returncode=1, stdout="", stderr="")

            with mock.patch.object(evaluator, "run_command", return_value=completed):
                result = evaluator.run_repaired_metrics(
                    work / "repaired.dwxmz",
                    repaired_run,
                    calculated,
                    "unit-guid",
                    timeout_sec=1,
                )

            self.assertFalse(repaired_run.exists())
            self.assertFalse(calculated.exists())
            self.assertFalse(result["success"])
        finally:
            shutil.rmtree(work, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
