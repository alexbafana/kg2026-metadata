#!/usr/bin/env python3
"""Build a controlled CSV dataset from author-supplied article PDF captures.

The generated dataset and extraction manifest contain article text and belong in
restricted storage. They must never be committed to the public repository.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import os
import re
import subprocess
import tempfile
from datetime import datetime, timezone
from pathlib import Path


SAFE_RECORD_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def file_sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def text_sha256(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def require_distinct_paths(*paths: Path) -> None:
    resolved = [path.resolve(strict=False) for path in paths]
    if len(resolved) != len(set(resolved)):
        raise ValueError("manifest, dataset output, and extraction-manifest paths must be distinct")


def validate_record_ids(sources: object) -> list[dict]:
    if not isinstance(sources, list) or not sources:
        raise ValueError("manifest.records must be a non-empty array")
    identifiers = []
    filename_keys: dict[str, str] = {}
    for index, source in enumerate(sources):
        if not isinstance(source, dict):
            raise ValueError(f"manifest.records[{index}] must be an object")
        record_id = source.get("record_id")
        if not isinstance(record_id, str) or not SAFE_RECORD_ID.fullmatch(record_id):
            raise ValueError(f"unsafe record_id at manifest.records[{index}]: {record_id!r}")
        if record_id in identifiers:
            raise ValueError(f"duplicate record IDs: {[record_id]}")
        identifiers.append(record_id)
        filename_key = f"{record_id}.pdf".casefold()
        if filename_key in filename_keys:
            raise ValueError(
                "record IDs collide as PDF filenames: "
                f"{filename_keys[filename_key]!r} and {record_id!r}"
            )
        filename_keys[filename_key] = record_id
    return sources


def resolve_pdf_path(pdf_dir: Path, record_id: str) -> Path:
    root = pdf_dir.resolve(strict=True)
    if not root.is_dir():
        raise NotADirectoryError(root)
    candidate = (root / f"{record_id}.pdf").resolve(strict=True)
    if root not in candidate.parents:
        raise ValueError(f"PDF path escapes declared source directory for {record_id}")
    if not candidate.is_file():
        raise FileNotFoundError(candidate)
    return candidate


def render_csv(records: list[dict]) -> bytes:
    stream = io.StringIO(newline="")
    writer = csv.DictWriter(stream, fieldnames=("id", "title", "body", "date", "source"))
    writer.writeheader()
    writer.writerows(records)
    return stream.getvalue().encode("utf-8")


def atomic_write_files(files: list[tuple[Path, bytes]]) -> None:
    """Replace each target atomically after every complete temporary file exists."""

    temporary_paths: list[tuple[Path, Path]] = []
    try:
        for target, content in files:
            target.parent.mkdir(parents=True, exist_ok=True)
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=target.parent,
                prefix=f".{target.name}.",
                suffix=".tmp",
                delete=False,
            ) as stream:
                stream.write(content)
                stream.flush()
                os.fsync(stream.fileno())
                temporary_paths.append((Path(stream.name), target))
        for temporary, target in temporary_paths:
            temporary.replace(target)
    finally:
        for temporary, _target in temporary_paths:
            temporary.unlink(missing_ok=True)


def extract_pdf_text(pdf_path: Path) -> str:
    result = subprocess.run(
        ["pdftotext", "-layout", str(pdf_path), "-"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return result.stdout.replace("\r\n", "\n").replace("\r", "\n")


def normalize_article(raw_text: str, title: str, published_at: str) -> str:
    compact_full = " ".join(raw_text.replace("\f", "\n").split())
    if " ".join(title.split()) not in compact_full:
        raise ValueError(f"PDF does not contain expected title: {title}")

    timestamp = datetime.fromisoformat(published_at)
    marker = timestamp.strftime("%d.%m.%Y %H:%M")
    lines = raw_text.replace("\f", "\n").splitlines()
    marker_indexes = [index for index, line in enumerate(lines) if marker in line]
    if not marker_indexes:
        raise ValueError(f"publication marker {marker!r} not found for {title}")
    body_lines = lines[marker_indexes[0] + 1 :]
    editor_index = next(
        (index for index, line in enumerate(body_lines) if line.strip().startswith("Toimetaja:")),
        len(body_lines),
    )
    body = " ".join("\n".join(body_lines[:editor_index]).split())
    if len(body) < 80:
        raise ValueError(f"extracted article body is unexpectedly short for {title}")
    return body


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--pdf-dir", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--extraction-manifest", required=True, type=Path)
    parser.add_argument("--overwrite", action="store_true")
    args = parser.parse_args()

    require_distinct_paths(args.manifest, args.output, args.extraction_manifest)

    for output in (args.output, args.extraction_manifest):
        if output.exists() and not args.overwrite:
            raise FileExistsError(f"refusing to overwrite: {output}")

    manifest = json.loads(args.manifest.read_text(encoding="utf-8"))
    if not isinstance(manifest, dict):
        raise ValueError("manifest must be a JSON object")
    sources = validate_record_ids(manifest.get("records"))
    records = []
    provenance = []
    for source in sources:
        record_id = source["record_id"]
        pdf_path = resolve_pdf_path(args.pdf_dir, record_id)
        if pdf_path in {
            args.manifest.resolve(strict=True),
            args.output.resolve(strict=False),
            args.extraction_manifest.resolve(strict=False),
        }:
            raise ValueError(f"PDF input aliases a manifest or output path: {pdf_path}")
        actual_pdf_sha = file_sha256(pdf_path)
        if actual_pdf_sha != source["source_content_sha256"]:
            raise ValueError(f"PDF hash mismatch for {record_id}")
        raw_text = extract_pdf_text(pdf_path)
        body = normalize_article(raw_text, source["title"], source["published_at"])
        records.append(
            {
                "id": record_id,
                "title": source["title"],
                "body": body,
                "date": source["published_at"],
                "source": source["canonical_url"],
            }
        )
        provenance.append(
            {
                "record_id": record_id,
                "pdf_path": str(pdf_path),
                "pdf_sha256": actual_pdf_sha,
                "normalized_text_sha256": text_sha256(body),
                "normalized_text_characters": len(body),
                "publication_marker": datetime.fromisoformat(source["published_at"]).strftime("%d.%m.%Y %H:%M"),
            }
        )

    dataset_bytes = render_csv(records)
    dataset_sha256 = hashlib.sha256(dataset_bytes).hexdigest()

    pdftotext_version = subprocess.run(
        ["pdftotext", "-v"], capture_output=True, text=True, check=True
    ).stderr.strip().splitlines()[0]
    extraction = {
        "schema_version": "1.0",
        "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "source_manifest_sha256": file_sha256(args.manifest),
        "dataset_sha256": dataset_sha256,
        "extraction_tool": pdftotext_version,
        "normalization": "start after printed publication timestamp; stop before first Toimetaja line; collapse whitespace",
        "record_count": len(records),
        "records": provenance,
    }
    extraction_bytes = (
        json.dumps(extraction, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    ).encode("utf-8")
    atomic_write_files(
        [
            (args.output, dataset_bytes),
            (args.extraction_manifest, extraction_bytes),
        ]
    )
    print(json.dumps({"records": len(records), "dataset_sha256": extraction["dataset_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
