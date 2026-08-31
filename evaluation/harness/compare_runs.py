#!/usr/bin/env python3
"""Compare canonical core results and acceptance decisions between two runs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("left", type=Path)
    parser.add_argument("right", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    left = load(args.left / "aggregate-results.json")
    right = load(args.right / "aggregate-results.json")
    left_items = {item["record_id"]: item for item in left["per_record"]}
    right_items = {item["record_id"]: item for item in right["per_record"]}
    if set(left_items) != set(right_items):
        raise ValueError("run record IDs differ")
    rows = []
    for record_id in sorted(left_items):
        l_item, r_item = left_items[record_id], right_items[record_id]
        rows.append(
            {
                "record_id": record_id,
                "core_identical": l_item["core_sha256"] == r_item["core_sha256"],
                "decision_identical": l_item["acceptance_decision"] == r_item["acceptance_decision"],
                "left_decision": l_item["acceptance_decision"],
                "right_decision": r_item["acceptance_decision"],
                "changed_fields": sorted(
                    key
                    for key in ("event_type", "job_count", "organization", "emtak_code", "acceptance_decision")
                    if l_item.get(key) != r_item.get(key)
                ),
            }
        )
    result = {
        "left_run": left["run_id"],
        "right_run": right["run_id"],
        "record_count": len(rows),
        "core_identical_count": sum(row["core_identical"] for row in rows),
        "decision_identical_count": sum(row["decision_identical"] for row in rows),
        "records": rows,
    }
    rendered = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
