from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "evaluation" / "stages" / "classify_employment.py"
SPEC = importlib.util.spec_from_file_location("classify_employment", MODULE_PATH)
assert SPEC and SPEC.loader
CLASSIFIER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(CLASSIFIER)


class ClassifierValidationTest(unittest.TestCase):
    def test_ground_evidence_rejects_nonobject_and_noninteger_count(self) -> None:
        with self.assertRaisesRegex(ValueError, "JSON object"):
            CLASSIFIER.ground_evidence([], "luuakse üks töökoht")
        with self.assertRaisesRegex(ValueError, "job_count"):
            CLASSIFIER.ground_evidence(
                {
                    "event_type": "job_gain",
                    "job_count": [],
                    "organization": None,
                    "confidence": 0.5,
                    "evidence_text": "",
                },
                "luuakse üks töökoht",
            )

    def test_number_words_require_token_boundaries(self) -> None:
        self.assertFalse(
            CLASSIFIER.evidence_supports_count(
                "Ettevõtte sadamas luuakse uusi töökohti.", 100
            )
        )
        self.assertTrue(
            CLASSIFIER.evidence_supports_count(
                "Ettevõttes luuakse sada uut töökohta.", 100
            )
        )

    def test_prompt_requires_exactly_one_placeholder(self) -> None:
        with self.assertRaisesRegex(ValueError, "exactly one"):
            CLASSIFIER.render_prompt("no input", "{}")
        with self.assertRaisesRegex(ValueError, "exactly one"):
            CLASSIFIER.render_prompt("{{article_json}} {{article_json}}", "{}")
        self.assertEqual(CLASSIFIER.render_prompt("x={{article_json}}", "{}"), "x={}")

    def test_outputs_must_be_distinct_and_outside_raw_directory(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            with self.assertRaisesRegex(ValueError, "distinct"):
                CLASSIFIER.require_distinct_outputs(root / "same", root / "same", root / "raw")
            with self.assertRaisesRegex(ValueError, "inside raw-dir"):
                CLASSIFIER.require_distinct_outputs(
                    root / "raw" / "predictions.json",
                    root / "manifest.json",
                    root / "raw",
                )


class ClassifierResumeTest(unittest.TestCase):
    def make_inputs(self, root: Path) -> tuple[list[str], str]:
        controlled = root / "controlled"
        controlled.mkdir()
        dataset = root / "articles.csv"
        dataset.write_text(
            "id,title,body,date,source\n"
            'a,A,"No employment change.",2024-01-01,https://example.test/a\n'
            'b,B,"No employment change either.",2024-01-02,https://example.test/b\n',
            encoding="utf-8",
        )
        prompt = root / "prompt.txt"
        prompt.write_text("Classify INPUT_JSON={{article_json}}", encoding="utf-8")
        schema = root / "schema.json"
        schema.write_text(json.dumps({"type": "object"}), encoding="utf-8")
        layer_digest = "a" * 64
        model_manifest = root / "model-manifest.json"
        model_manifest.write_text(
            json.dumps(
                {
                    "config": {"digest": "sha256:" + "b" * 64},
                    "layers": [{"digest": "sha256:" + layer_digest}],
                }
            ),
            encoding="utf-8",
        )
        argv = [
            "classify_employment.py",
            "--dataset",
            str(dataset),
            "--prompt",
            str(prompt),
            "--schema",
            str(schema),
            "--output",
            str(controlled / "predictions.json"),
            "--raw-dir",
            str(controlled / "raw"),
            "--run-manifest",
            str(controlled / "run-manifest.json"),
            "--run-id",
            "test-run",
            "--controlled-root",
            str(controlled),
            "--model",
            "test-model:latest",
            "--model-layer-sha256",
            layer_digest,
            "--model-manifest",
            str(model_manifest),
            "--max-attempts",
            "2",
        ]
        return argv, hashlib.sha256(model_manifest.read_bytes()).hexdigest()

    def test_resume_reuses_valid_checkpoint_after_interruption(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            argv, model_manifest_sha = self.make_inputs(root)
            chat_calls = []
            interrupt_second = True

            def fake_post(url: str, payload: dict, timeout: int) -> dict:
                nonlocal interrupt_second
                if url.endswith("/api/show"):
                    return {"details": {"family": "test"}, "model_info": {"x": 1}}
                chat_calls.append(payload)
                if len(chat_calls) == 2 and interrupt_second:
                    interrupt_second = False
                    raise KeyboardInterrupt("simulated power loss")
                return {
                    "model": "test-model:latest",
                    "done": True,
                    "message": {
                        "content": json.dumps(
                            {
                                "event_type": "no_event",
                                "job_count": None,
                                "organization": None,
                                "confidence": 0.8,
                                "evidence_text": "",
                            }
                        )
                    },
                }

            completed = subprocess.CompletedProcess(
                ["ollama", "--version"], 0, stdout="ollama version test\n", stderr=""
            )
            with mock.patch.object(CLASSIFIER, "post_json", side_effect=fake_post), mock.patch.object(
                CLASSIFIER.subprocess, "run", return_value=completed
            ), mock.patch.object(CLASSIFIER.platform, "platform", return_value="test-platform"), mock.patch.object(
                sys, "argv", argv
            ):
                with self.assertRaises(KeyboardInterrupt):
                    CLASSIFIER.main()

            raw = root / "controlled" / "raw"
            first = json.loads((raw / "a.json").read_text(encoding="utf-8"))
            second = json.loads((raw / "b.json").read_text(encoding="utf-8"))
            self.assertEqual(first["final_status"], "valid")
            self.assertEqual(second["final_status"], "in_progress")

            with mock.patch.object(CLASSIFIER, "post_json", side_effect=fake_post), mock.patch.object(
                CLASSIFIER.subprocess, "run", return_value=completed
            ), mock.patch.object(CLASSIFIER.platform, "platform", return_value="test-platform"), mock.patch.object(
                sys, "argv", [*argv, "--resume"]
            ):
                self.assertEqual(CLASSIFIER.main(), 0)

            self.assertEqual(len(chat_calls), 3, "the completed first record must not run again")
            predictions = json.loads(
                (root / "controlled" / "predictions.json").read_text(encoding="utf-8")
            )
            self.assertEqual(set(predictions), {"a", "b"})
            run_manifest = json.loads(
                (root / "controlled" / "run-manifest.json").read_text(encoding="utf-8")
            )
            self.assertEqual(run_manifest["model_manifest_sha256"], model_manifest_sha)
            self.assertTrue((raw / "_environment" / "model-manifest.json").is_file())
            self.assertTrue((raw / "_environment" / "ollama-show.json").is_file())


if __name__ == "__main__":
    unittest.main()
