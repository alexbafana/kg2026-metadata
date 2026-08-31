#!/usr/bin/env python3
"""Score structured employment predictions against a controlled label projection.

This scorer deliberately does not read or emit article text. Reference projections
remain provisional until every record has ``review_status: "final"``.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from pathlib import Path
from typing import Any


EVENT_TYPES = ("job_gain", "job_loss", "no_event", "ambiguous")
REVIEW_STATUSES = ("preliminary", "second_reviewed", "final")
REFERENCE_SCHEMA_VERSION = "controlled-reference-projection-v1"


class InputError(ValueError):
    """Raised when an input cannot be scored safely."""


def load_json(path: Path) -> Any:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise InputError(f"invalid JSON in {path}: {exc}") from exc


def require_object(value: Any, location: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise InputError(f"{location} must be a JSON object")
    return value


def require_nonempty_string(value: Any, location: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise InputError(f"{location} must be a non-empty string")
    return value


def parse_predictions(document: Any) -> dict[str, dict[str, Any]]:
    root = require_object(document, "predictions")
    raw_records = root.get("records", root)
    records = require_object(raw_records, "predictions.records")
    parsed: dict[str, dict[str, Any]] = {}
    for record_id, raw in records.items():
        require_nonempty_string(record_id, "prediction record id")
        record = require_object(raw, f"predictions[{record_id!r}]")
        employment = require_object(
            record.get("employment", record),
            f"predictions[{record_id!r}].employment",
        )
        event_type = employment.get("event_type")
        if event_type not in EVENT_TYPES:
            raise InputError(
                f"predictions[{record_id!r}].employment.event_type must be one of "
                f"{', '.join(EVENT_TYPES)}"
            )
        count = employment.get("job_count")
        if count is not None and (not isinstance(count, int) or isinstance(count, bool) or count < 0):
            raise InputError(
                f"predictions[{record_id!r}].employment.job_count must be null or a "
                "non-negative integer"
            )
        span_ids_raw = employment.get("evidence_span_ids")
        if span_ids_raw is None:
            one_span = employment.get("evidence_span_id")
            if one_span is not None:
                span_ids_raw = [one_span]
            else:
                evidence_text = employment.get("evidence_text", "")
                if not isinstance(evidence_text, str):
                    raise InputError(
                        f"predictions[{record_id!r}].employment.evidence_text must be a string"
                    )
                span_ids_raw = (
                    ["sha256:" + hashlib.sha256(evidence_text.encode("utf-8")).hexdigest()]
                    if evidence_text
                    else []
                )
        if not isinstance(span_ids_raw, list) or any(
            not isinstance(item, str) or not item.strip() for item in span_ids_raw
        ):
            raise InputError(
                f"predictions[{record_id!r}].employment.evidence_span_ids must be "
                "an array of non-empty strings"
            )
        parsed[record_id] = {
            "event_type": event_type,
            "job_count": count,
            "evidence_span_ids": set(span_ids_raw),
        }
    if not parsed:
        raise InputError("predictions must contain at least one record")
    return parsed


def parse_references(document: Any) -> tuple[dict[str, dict[str, Any]], dict[str, str]]:
    root = require_object(document, "references")
    if "records" not in root:
        raise InputError("references.records is required")
    raw_records = root["records"]
    if not isinstance(raw_records, list) or not raw_records:
        raise InputError("references.records must be a non-empty array")

    schema_version = require_nonempty_string(
        root.get("schema_version"), "references.schema_version"
    )
    if schema_version != REFERENCE_SCHEMA_VERSION:
        raise InputError(
            f"references.schema_version must be {REFERENCE_SCHEMA_VERSION!r}"
        )
    metadata = {
        "schema_version": schema_version,
        "sample_id": require_nonempty_string(root.get("sample_id"), "references.sample_id"),
    }
    parsed: dict[str, dict[str, Any]] = {}
    forbidden_text_keys = {"article_text", "full_text", "source_text", "body"}
    for index, raw in enumerate(raw_records):
        record = require_object(raw, f"references.records[{index}]")
        forbidden = forbidden_text_keys.intersection(record)
        if forbidden:
            raise InputError(
                f"references.records[{index}] contains prohibited article-text field(s): "
                f"{', '.join(sorted(forbidden))}"
            )
        record_id = require_nonempty_string(
            record.get("record_id"), f"references.records[{index}].record_id"
        )
        if record_id in parsed:
            raise InputError(f"duplicate reference record_id: {record_id}")
        review_status = record.get("review_status")
        if review_status not in REVIEW_STATUSES:
            raise InputError(
                f"references.records[{index}].review_status must be one of "
                f"{', '.join(REVIEW_STATUSES)}"
            )
        event_type = record.get("event_type")
        if event_type not in EVENT_TYPES:
            raise InputError(
                f"references.records[{index}].event_type must be one of "
                f"{', '.join(EVENT_TYPES)}"
            )

        count_spec = require_object(
            record.get("job_count"), f"references.records[{index}].job_count"
        )
        if not isinstance(count_spec.get("scorable"), bool):
            raise InputError(
                f"references.records[{index}].job_count.scorable must be boolean"
            )
        count = count_spec.get("value")
        if count_spec["scorable"]:
            if not isinstance(count, int) or isinstance(count, bool) or count < 0:
                raise InputError(
                    f"references.records[{index}].job_count.value must be a non-negative "
                    "integer when scorable is true"
                )
        elif count is not None:
            raise InputError(
                f"references.records[{index}].job_count.value must be null when scorable "
                "is false"
            )

        span_ids = record.get("evidence_span_ids")
        if not isinstance(span_ids, list) or any(
            not isinstance(item, str) or not item.strip() for item in span_ids
        ):
            raise InputError(
                f"references.records[{index}].evidence_span_ids must be an array of "
                "non-empty strings"
            )
        if len(span_ids) != len(set(span_ids)):
            raise InputError(
                f"references.records[{index}].evidence_span_ids contains duplicates"
            )
        parsed[record_id] = {
            "review_status": review_status,
            "event_type": event_type,
            "job_count_scorable": count_spec["scorable"],
            "job_count": count,
            "evidence_span_ids": set(span_ids),
        }
    return parsed, metadata


def safe_rate(numerator: int, denominator: int) -> float | None:
    return numerator / denominator if denominator else None


def score(
    predictions: dict[str, dict[str, Any]],
    references: dict[str, dict[str, Any]],
    metadata: dict[str, str],
) -> dict[str, Any]:
    predicted_ids = set(predictions)
    reference_ids = set(references)
    if predicted_ids != reference_ids:
        missing = sorted(reference_ids - predicted_ids)
        extra = sorted(predicted_ids - reference_ids)
        raise InputError(
            "prediction/reference record IDs differ; "
            f"missing_predictions={missing}, extra_predictions={extra}"
        )

    confusion = {
        expected: {predicted: 0 for predicted in EVENT_TYPES}
        for expected in EVENT_TYPES
    }
    correct = 0
    for record_id in sorted(reference_ids):
        expected = references[record_id]["event_type"]
        predicted = predictions[record_id]["event_type"]
        confusion[expected][predicted] += 1
        correct += int(expected == predicted)

    present_classes = [
        event_type
        for event_type in EVENT_TYPES
        if any(ref["event_type"] == event_type for ref in references.values())
    ]
    per_class: dict[str, dict[str, float | int]] = {}
    f1_values: list[float] = []
    for event_type in present_classes:
        true_positive = confusion[event_type][event_type]
        false_positive = sum(
            confusion[other][event_type] for other in EVENT_TYPES if other != event_type
        )
        false_negative = sum(
            confusion[event_type][other] for other in EVENT_TYPES if other != event_type
        )
        precision = safe_rate(true_positive, true_positive + false_positive) or 0.0
        recall = safe_rate(true_positive, true_positive + false_negative) or 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        f1_values.append(f1)
        per_class[event_type] = {
            "support": sum(confusion[event_type].values()),
            "precision": precision,
            "recall": recall,
            "f1": f1,
        }

    count_scorable = [
        record_id
        for record_id, reference in references.items()
        if reference["job_count_scorable"]
    ]
    count_correct = sum(
        predictions[record_id]["job_count"] == references[record_id]["job_count"]
        for record_id in count_scorable
    )

    grounding_scorable = [
        record_id
        for record_id, reference in references.items()
        if reference["evidence_span_ids"]
    ]
    grounding_correct = sum(
        bool(
            predictions[record_id]["evidence_span_ids"]
            & references[record_id]["evidence_span_ids"]
        )
        for record_id in grounding_scorable
    )

    all_final = all(ref["review_status"] == "final" for ref in references.values())
    result = {
        "schema_version": "employment-score-v1",
        "sample_id": metadata["sample_id"],
        "reference_schema_version": metadata["schema_version"],
        "result_status": "final" if all_final else "provisional",
        "all_references_final": all_final,
        "record_count": len(references),
        "event_type": {
            "labels": list(EVENT_TYPES),
            "confusion_matrix": confusion,
            "exact_agreement": {
                "correct": correct,
                "scored": len(references),
                "rate": safe_rate(correct, len(references)),
            },
            "macro_f1": sum(f1_values) / len(f1_values),
            "macro_f1_classes": present_classes,
            "per_class": per_class,
        },
        "job_count_exact_agreement": {
            "correct": count_correct,
            "scored": len(count_scorable),
            "rate": safe_rate(count_correct, len(count_scorable)),
            "criterion": "reference job_count.scorable is true",
        },
        "evidence_grounding": {
            "grounded": grounding_correct,
            "scored": len(grounding_scorable),
            "rate": safe_rate(grounding_correct, len(grounding_scorable)),
            "criterion": "at least one predicted opaque span ID (or exact evidence-text SHA-256) matches an approved reference span ID",
        },
        "limitations": [
            "No article body is read and no evidence text is emitted; controlled prediction snippets are reduced to SHA-256 in memory.",
            "A provisional result must not be reported as a final evaluation.",
            "Macro-F1 is computed over event classes present in the reference sample.",
        ],
    }
    # Guard against accidental non-finite JSON if arithmetic changes later.
    if any(
        isinstance(value, float) and not math.isfinite(value)
        for value in f1_values
    ):
        raise InputError("computed a non-finite metric")
    return result


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--references", required=True, type=Path)
    parser.add_argument(
        "--output",
        type=Path,
        help="write JSON here; omit to print to standard output",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    try:
        predictions = parse_predictions(load_json(args.predictions))
        references, metadata = parse_references(load_json(args.references))
        result = score(predictions, references, metadata)
        rendered = json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False) + "\n"
        if args.output:
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(rendered, encoding="utf-8")
        else:
            sys.stdout.write(rendered)
        return 0
    except InputError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
