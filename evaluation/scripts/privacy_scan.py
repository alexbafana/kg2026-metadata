#!/usr/bin/env python3
"""Flag common personal-data patterns in candidate release files.

This is a triage aid, not a GDPR, confidentiality, copyright, or licensing
determination. A human reviewer must assess every flagged file and source.
"""

from __future__ import annotations

import argparse
import re
from pathlib import Path


PATTERNS = {
    "email": re.compile(r"\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b", re.I),
    "phone": re.compile(
        r"(?<!\w)(?!\d{4}-\d{2}-\d{2}(?!\d))(?:\+?\d[\d .()-]{6,}\d)(?!\w)"
    ),
    "Estonian personal ID candidate": re.compile(r"(?<!\d)\d{11}(?!\d)"),
}

EXCLUDED_DIRECTORY_NAMES = {".git", ".venv", "__pycache__", "node_modules"}


def scan_text(line: str, label: str) -> str:
    """Remove machine-number forms that otherwise resemble phone numbers."""
    if label != "phone":
        return line
    return re.sub(
        r"https?://\S+|\b(?:\d{1,3}\.){3}\d{1,3}(?::\d+)?\b|\b\d+\.\d+\b",
        "",
        line,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan text-like files for review candidates.")
    parser.add_argument("path", type=Path, help="File or directory to scan")
    args = parser.parse_args()
    files = (
        [args.path]
        if args.path.is_file()
        else sorted(
            p
            for p in args.path.rglob("*")
            if p.is_file()
            and not any(part in EXCLUDED_DIRECTORY_NAMES for part in p.parts)
        )
    )
    findings = 0
    for path in files:
        try:
            text = path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for label, pattern in PATTERNS.items():
            for line_number, line in enumerate(text.splitlines(), start=1):
                if pattern.search(scan_text(line, label)):
                    print(f"REVIEW: {path}:{line_number}: possible {label}")
                    findings += 1
    print(f"Completed scan: {findings} review candidate(s). Human review remains required.")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
