from __future__ import annotations

import hashlib
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "evaluation" / "stages" / "build_controlled_dataset.py"
SPEC = importlib.util.spec_from_file_location("build_controlled_dataset", MODULE_PATH)
assert SPEC and SPEC.loader
BUILDER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BUILDER)


class ControlledDatasetBuilderTest(unittest.TestCase):
    def test_normalization_extracts_body_and_excludes_editor_footer(self) -> None:
        raw = (
            "Example title\r\n"
            "01.02.2024 03:04\r\n"
            " First paragraph with enough content to make the normalized article body "
            "longer than eighty characters.\r\nSecond paragraph.\r\n"
            "Toimetaja: Example Editor\r\nIgnored footer\f"
        )
        body = BUILDER.normalize_article(raw, "Example title", "2024-02-01T03:04:00+00:00")
        self.assertIn("First paragraph", body)
        self.assertIn("Second paragraph.", body)
        self.assertNotIn("Example Editor", body)
        self.assertNotIn("Ignored footer", body)
        self.assertNotIn("\n", body)

    def test_hash_helpers_are_stable(self) -> None:
        expected = hashlib.sha256(b"abc").hexdigest()
        self.assertEqual(BUILDER.text_sha256("abc"), expected)
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "source.pdf"
            path.write_bytes(b"abc")
            self.assertEqual(BUILDER.file_sha256(path), expected)

    def test_duplicate_and_unsafe_record_ids_fail(self) -> None:
        with self.assertRaisesRegex(ValueError, "duplicate record IDs"):
            BUILDER.validate_record_ids([{"record_id": "same"}, {"record_id": "same"}])
        for unsafe in ("../escape", "nested/item", "", "item pdf"):
            with self.subTest(unsafe=unsafe), self.assertRaisesRegex(ValueError, "unsafe record_id"):
                BUILDER.validate_record_ids([{"record_id": unsafe}])

    def test_case_variant_record_ids_cannot_collide_as_filenames(self) -> None:
        with self.assertRaisesRegex(ValueError, "collide as PDF filenames"):
            BUILDER.validate_record_ids([{"record_id": "Record"}, {"record_id": "record"}])

    def test_symlink_escape_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_dir = base / "sources"
            outside = base / "outside.pdf"
            source_dir.mkdir()
            outside.write_bytes(b"outside")
            (source_dir / "record.pdf").symlink_to(outside)
            with self.assertRaisesRegex(ValueError, "escapes declared source directory"):
                BUILDER.resolve_pdf_path(source_dir, "record")

    def test_output_paths_must_be_distinct(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "same"
            with self.assertRaisesRegex(ValueError, "must be distinct"):
                BUILDER.require_distinct_paths(path, path, Path(temporary) / "other")

    def test_main_writes_complete_csv_and_manifest_atomically(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            base = Path(temporary)
            source_dir = base / "sources"
            source_dir.mkdir()
            pdf_path = source_dir / "item-1.pdf"
            pdf_path.write_bytes(b"synthetic PDF bytes")
            manifest_path = base / "manifest.json"
            manifest_path.write_text(
                json.dumps(
                    {
                        "records": [
                            {
                                "record_id": "item-1",
                                "source_content_sha256": hashlib.sha256(pdf_path.read_bytes()).hexdigest(),
                                "title": "Example title",
                                "published_at": "2024-02-01T03:04:00+00:00",
                                "canonical_url": "https://example.invalid/item-1",
                            }
                        ]
                    }
                ),
                encoding="utf-8",
            )
            output = base / "generated" / "dataset.csv"
            extraction = base / "generated" / "extraction.json"
            raw_text = (
                "Example title\n01.02.2024 03:04\n"
                "Synthetic body content long enough for normalization and integration testing "
                "without containing any controlled evidence or source material.\n"
                "Toimetaja: Test\n"
            )
            completed = mock.Mock(stderr="pdftotext version synthetic\n")
            argv = [
                str(MODULE_PATH),
                "--manifest", str(manifest_path),
                "--pdf-dir", str(source_dir),
                "--output", str(output),
                "--extraction-manifest", str(extraction),
            ]
            with mock.patch.object(sys, "argv", argv), mock.patch.object(
                BUILDER, "extract_pdf_text", return_value=raw_text
            ), mock.patch.object(BUILDER.subprocess, "run", return_value=completed):
                self.assertEqual(BUILDER.main(), 0)

            self.assertTrue(output.is_file())
            self.assertTrue(extraction.is_file())
            metadata = json.loads(extraction.read_text(encoding="utf-8"))
            self.assertEqual(metadata["dataset_sha256"], hashlib.sha256(output.read_bytes()).hexdigest())
            self.assertEqual(metadata["record_count"], 1)
            self.assertFalse(list(output.parent.glob(".*.tmp")))


if __name__ == "__main__":
    unittest.main()
