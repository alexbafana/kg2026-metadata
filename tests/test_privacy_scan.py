from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "privacy_scan", ROOT / "evaluation" / "scripts" / "privacy_scan.py"
)
privacy_scan = importlib.util.module_from_spec(SPEC)
assert SPEC.loader
SPEC.loader.exec_module(privacy_scan)


class PrivacyScanTest(unittest.TestCase):
    def test_machine_numbers_are_removed_from_phone_scan(self) -> None:
        for value in ("score 0.3095238095", "http://127.0.0.1:11434/api/chat", "host 127.0.0.1"):
            self.assertIsNone(
                privacy_scan.PATTERNS["phone"].search(privacy_scan.scan_text(value, "phone"))
            )

    def test_phone_candidate_remains_visible(self) -> None:
        value = "".join(("Call +372", " 5555", " 1234"))
        self.assertIsNotNone(
            privacy_scan.PATTERNS["phone"].search(privacy_scan.scan_text(value, "phone"))
        )


if __name__ == "__main__":
    unittest.main()
