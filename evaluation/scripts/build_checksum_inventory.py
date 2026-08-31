#!/usr/bin/env python3
"""Create or verify a deterministic SHA-256 inventory for an evidence tree."""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path


EXCLUDED_NAMES = {".DS_Store"}


def digest(path: Path) -> str:
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            value.update(chunk)
    return value.hexdigest()


def entries(root: Path, inventory: Path) -> list[tuple[str, str]]:
    return [
        (digest(path), path.relative_to(root).as_posix())
        for path in sorted(root.rglob("*"))
        if path.is_file()
        and path.resolve() != inventory.resolve()
        and path.name not in EXCLUDED_NAMES
    ]


def render(values: list[tuple[str, str]]) -> str:
    return "".join(f"{file_digest}  {relative_path}\n" for file_digest, relative_path in values)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--root", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--verify", action="store_true")
    args = parser.parse_args()

    root = args.root.resolve()
    output = args.output.resolve()
    if not root.is_dir() or (output != root and root not in output.parents):
        raise ValueError("output must be inside an existing inventory root")
    expected = render(entries(root, output))
    if args.verify:
        if output.read_text(encoding="utf-8") != expected:
            raise ValueError("checksum inventory does not match the evidence tree")
        print(f"verified {expected.count(chr(10))} files")
        return 0

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = output.with_name(f".{output.name}.tmp")
    temporary.write_text(expected, encoding="utf-8")
    temporary.replace(output)
    print(f"inventoried {len(entries(root, output))} files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
