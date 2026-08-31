from __future__ import annotations

import importlib.util
import hashlib
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "evaluation" / "harness" / "score_employment.py"
SPEC = importlib.util.spec_from_file_location("score_employment", MODULE_PATH)
assert SPEC and SPEC.loader
SCORER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(SCORER)


class EmploymentScorerTest(unittest.TestCase):
    def setUp(self) -> None:
        self.predictions = {
            "a": {"event_type": "job_gain", "job_count": 25, "evidence_span_ids": {"a:1"}},
            "b": {"event_type": "no_event", "job_count": None, "evidence_span_ids": set()},
        }
        self.references = {
            "a": {
                "review_status": "final",
                "event_type": "job_gain",
                "job_count_scorable": True,
                "job_count": 25,
                "evidence_span_ids": {"a:1"},
            },
            "b": {
                "review_status": "preliminary",
                "event_type": "job_loss",
                "job_count_scorable": False,
                "job_count": None,
                "evidence_span_ids": set(),
            },
        }

    def test_metrics_and_provisional_status(self) -> None:
        result = SCORER.score(
            self.predictions,
            self.references,
            {"sample_id": "test", "schema_version": "controlled-reference-projection-v1"},
        )
        self.assertEqual(result["result_status"], "provisional")
        self.assertEqual(result["event_type"]["exact_agreement"]["rate"], 0.5)
        self.assertAlmostEqual(result["event_type"]["macro_f1"], 0.5)
        self.assertEqual(result["job_count_exact_agreement"]["scored"], 1)
        self.assertEqual(result["job_count_exact_agreement"]["rate"], 1.0)
        self.assertEqual(result["evidence_grounding"]["rate"], 1.0)

    def test_final_only_when_every_reference_is_final(self) -> None:
        self.references["b"]["review_status"] = "final"
        result = SCORER.score(
            self.predictions,
            self.references,
            {"sample_id": "test", "schema_version": "controlled-reference-projection-v1"},
        )
        self.assertEqual(result["result_status"], "final")

    def test_record_mismatch_fails(self) -> None:
        del self.predictions["b"]
        with self.assertRaises(SCORER.InputError):
            SCORER.score(
                self.predictions,
                self.references,
                {"sample_id": "test", "schema_version": "controlled-reference-projection-v1"},
            )

    def test_article_text_field_is_rejected(self) -> None:
        document = {
            "schema_version": "controlled-reference-projection-v1",
            "sample_id": "test",
            "records": [
                {
                    "record_id": "a",
                    "review_status": "preliminary",
                    "event_type": "job_gain",
                    "job_count": {"scorable": True, "value": 1},
                    "evidence_span_ids": [],
                    "article_text": "must remain controlled",
                }
            ],
        }
        with self.assertRaises(SCORER.InputError):
            SCORER.parse_references(document)

    def test_controlled_evidence_text_is_reduced_to_hash(self) -> None:
        evidence = "loob 25 töökohta"
        parsed = SCORER.parse_predictions(
            {
                "a": {
                    "employment": {
                        "event_type": "job_gain",
                        "job_count": 25,
                        "evidence_text": evidence,
                    }
                }
            }
        )
        expected = "sha256:" + hashlib.sha256(evidence.encode("utf-8")).hexdigest()
        self.assertEqual(parsed["a"]["evidence_span_ids"], {expected})


if __name__ == "__main__":
    unittest.main()
