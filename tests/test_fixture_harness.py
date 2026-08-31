from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
HARNESS = ROOT / "evaluation" / "harness"
FIXTURES = ROOT / "evaluation" / "fixtures" / "public"


class FixtureHarnessTest(unittest.TestCase):
    def run_fixture(self, config_name: str, output: Path) -> dict:
        subprocess.run(
            [
                sys.executable,
                str(HARNESS / "run_evaluation.py"),
                "--dataset",
                str(FIXTURES / "articles.csv"),
                "--predictions",
                str(FIXTURES / "predictions.json"),
                "--config",
                str(FIXTURES / config_name),
                "--output",
                str(output),
            ],
            check=True,
            capture_output=True,
            text=True,
        )
        return json.loads((output / "aggregate-results.json").read_text(encoding="utf-8"))

    def test_repeat_and_variant(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            run_0 = self.run_fixture("run-0.config.json", root / "run-0")
            run_1 = self.run_fixture("run-1.config.json", root / "run-1")
            run_var = self.run_fixture("run-var.config.json", root / "run-var")
            self.assertEqual(run_0["decisions"], {"accepted": 2, "conditional": 0, "rejected": 1})
            self.assertEqual(run_0["per_record"], run_1["per_record"])
            self.assertEqual(run_var["decisions"], {"accepted": 1, "conditional": 1, "rejected": 1})
            loss = next(item for item in run_var["per_record"] if item["record_id"] == "synthetic_loss_01")
            self.assertEqual(loss["acceptance_decision"], "conditional")


if __name__ == "__main__":
    unittest.main()
