#!/usr/bin/env python3
"""Verify that repeated and varied run configurations obey the protocol."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


IGNORED = {"run_id", "run_type", "varied_factor"}


def substantive(config: dict) -> dict:
    return {key: value for key, value in config.items() if key not in IGNORED}


def differences(left: object, right: object, path: str = "") -> list[str]:
    if isinstance(left, dict) and isinstance(right, dict):
        found = []
        for key in sorted(set(left) | set(right)):
            found.extend(differences(left.get(key), right.get(key), f"{path}/{key}"))
        return found
    return [] if left == right else [path or "/"]


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("run_0", type=Path)
    parser.add_argument("run_1", type=Path)
    parser.add_argument("run_var", type=Path)
    args = parser.parse_args()
    run_0, run_1, run_var = map(load, (args.run_0, args.run_1, args.run_var))
    repeat_diff = differences(substantive(run_0), substantive(run_1))
    variant_diff = differences(substantive(run_0), substantive(run_var))
    declared = run_var.get("varied_factor", {}).get("name")
    expected = f"/{declared}" if declared else None
    result = {
        "repeat_substantive_differences": repeat_diff,
        "variant_substantive_differences": variant_diff,
        "declared_varied_factor": declared,
        "valid": repeat_diff == [] and variant_diff == [expected],
    }
    print(json.dumps(result, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
