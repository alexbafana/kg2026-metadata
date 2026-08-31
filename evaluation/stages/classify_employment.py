#!/usr/bin/env python3
"""Execute the employment-classification stage with a local Ollama model.

Inputs, raw requests, raw responses, and per-item predictions can contain
restricted article content and must be written only to controlled storage.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import io
import json
import platform
import re
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urlparse


EXPECTED_FIELDS = {"event_type", "job_count", "organization", "confidence", "evidence_text"}
EVENT_TYPES = {"job_gain", "job_loss", "no_event", "ambiguous"}
EMPLOYMENT_TERMS = ("töökoht", "töötaja", "koonda", "lisandu", "kaob", "luuakse", "loob ")
NUMBER_WORDS = {
    0: ("null",),
    1: ("üks", "uhe"),
    2: ("kaks",),
    3: ("kolm",),
    4: ("neli",),
    5: ("viis",),
    6: ("kuus",),
    7: ("seitse",),
    8: ("kaheksa",),
    9: ("üheksa", "uheksa"),
    10: ("kümme", "kumme"),
    12: ("kaksteist",),
    20: ("kakskümmend", "kakskummend"),
    100: ("sada",),
    2000: ("kaks tuhat",),
}
SAFE_RECORD_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_object(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def file_sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def evidence_supports_count(evidence: str, count: int) -> bool:
    digits = {int(value.replace(" ", "")) for value in re.findall(r"\b\d[\d ]*\d\b|\b\d\b", evidence)}
    if count in digits:
        return True
    lowered = evidence.casefold()
    return any(
        re.search(rf"(?<!\w){re.escape(word)}(?!\w)", lowered) is not None
        for word in NUMBER_WORDS.get(count, ())
    )


def ground_evidence(value: dict, body: str) -> tuple[dict, list[str]]:
    if not isinstance(value, dict):
        raise ValueError("prediction must be a JSON object")
    evidence = value.get("evidence_text", "")
    event_type = value.get("event_type")
    count = value.get("job_count")
    if count is not None and (not isinstance(count, int) or isinstance(count, bool) or count < 0):
        raise ValueError(f"job_count must be a non-negative integer or null: {count!r}")
    lowered = evidence.casefold() if isinstance(evidence, str) else ""
    already_grounded = (
        isinstance(evidence, str)
        and evidence in body
        and (event_type not in {"job_gain", "job_loss"} or any(term in lowered for term in EMPLOYMENT_TERMS))
        and (count is None or evidence_supports_count(evidence, count))
    )
    if already_grounded:
        return value, []
    updated = dict(value)
    if event_type in {"job_gain", "job_loss"}:
        sentences = [item.strip() for item in re.split(r"(?<=[.!?])\s+", body) if item.strip()]
        candidates = [
            sentence
            for sentence in sentences
            if any(term in sentence.casefold() for term in EMPLOYMENT_TERMS)
            and (count is None or evidence_supports_count(sentence, count))
        ]
        organization = value.get("organization")
        if organization:
            organization_candidates = [item for item in candidates if organization.casefold() in item.casefold()]
            if organization_candidates:
                candidates = organization_candidates
        if candidates:
            updated["evidence_text"] = min(candidates, key=len)
            return updated, ["evidence_text_replaced_with_shortest_grounded_sentence"]
    elif isinstance(evidence, str) and evidence not in body:
        updated["evidence_text"] = ""
        return updated, ["nonexact_optional_evidence_removed"]
    return value, []


def validate_prediction(value: object, body: str) -> dict:
    if not isinstance(value, dict) or set(value) != EXPECTED_FIELDS:
        raise ValueError(f"prediction fields must be exactly {sorted(EXPECTED_FIELDS)}")
    event_type = value["event_type"]
    if event_type not in EVENT_TYPES:
        raise ValueError(f"invalid event_type: {event_type!r}")
    count = value["job_count"]
    if count is not None and (not isinstance(count, int) or isinstance(count, bool) or count < 0):
        raise ValueError(f"job_count must be a non-negative integer or null: {count!r}")
    organization = value["organization"]
    if organization is not None and not isinstance(organization, str):
        raise ValueError("organization must be a string or null")
    confidence = value["confidence"]
    if isinstance(confidence, bool) or not isinstance(confidence, (int, float)) or not 0 <= confidence <= 1:
        raise ValueError(f"confidence must be within [0,1]: {confidence!r}")
    evidence = value["evidence_text"]
    if not isinstance(evidence, str):
        raise ValueError("evidence_text must be a string")
    if event_type in {"job_gain", "job_loss"} and not evidence.strip():
        raise ValueError("gain/loss prediction requires evidence_text")
    if evidence and evidence not in body:
        raise ValueError("evidence_text is not an exact substring of the normalized source body")
    if event_type in {"job_gain", "job_loss"} and not any(term in evidence.casefold() for term in EMPLOYMENT_TERMS):
        raise ValueError("gain/loss evidence_text does not contain employment-change wording")
    if count is not None and not evidence_supports_count(evidence, count):
        raise ValueError("job_count is not explicitly supported by evidence_text")
    return value


def post_json(url: str, payload: dict, timeout_seconds: int) -> dict:
    request = urllib.request.Request(
        url,
        data=canonical_bytes(payload),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=timeout_seconds) as response:
        return json.loads(response.read().decode("utf-8"))


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
    temporary.replace(path)


def write_bytes(path: Path, value: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    temporary = path.with_name(f".{path.name}.tmp")
    temporary.write_bytes(value)
    temporary.replace(path)


def require_within(path: Path, root: Path) -> None:
    resolved_path = path.resolve()
    resolved_root = root.resolve()
    if resolved_path != resolved_root and resolved_root not in resolved_path.parents:
        raise ValueError(f"controlled output must be within {resolved_root}: {resolved_path}")


def require_distinct_outputs(output: Path, run_manifest: Path, raw_dir: Path) -> None:
    output_resolved = output.resolve()
    manifest_resolved = run_manifest.resolve()
    raw_resolved = raw_dir.resolve()
    if output_resolved == manifest_resolved:
        raise ValueError("output and run-manifest must be distinct files")
    for file_path in (output_resolved, manifest_resolved):
        if (
            file_path == raw_resolved
            or raw_resolved in file_path.parents
            or file_path in raw_resolved.parents
        ):
            raise ValueError("output files must not be inside raw-dir")


def show_endpoint(chat_endpoint: str) -> str:
    parsed = urlparse(chat_endpoint)
    return parsed._replace(path="/api/show", params="", query="", fragment="").geturl()


def render_prompt(template: str, article_json: str) -> str:
    if template.count("{{article_json}}") != 1:
        raise ValueError("prompt must contain exactly one {{article_json}} placeholder")
    return template.replace("{{article_json}}", article_json)


def correction_messages(messages: list[dict], response: dict | None, error: str) -> list[dict]:
    if response is None:
        return messages
    return [
        *messages,
        {"role": "assistant", "content": response.get("message", {}).get("content", "")},
        {
            "role": "user",
            "content": (
                "The JSON failed deterministic validation: "
                f"{error}. Return a corrected JSON object only. "
                "Copy evidence_text exactly from INPUT_JSON.body and do not invent a count."
            ),
        },
    ]


def validate_checkpoint(
    checkpoint: object,
    *,
    run_id: str,
    record_id: str,
    input_sha256: str,
    execution_fingerprint: str,
) -> dict:
    if not isinstance(checkpoint, dict):
        raise ValueError(f"invalid resume checkpoint for {record_id}")
    expected = {
        "run_id": run_id,
        "record_id": record_id,
        "input_sha256": input_sha256,
        "execution_fingerprint": execution_fingerprint,
    }
    for key, value in expected.items():
        if checkpoint.get(key) != value:
            raise ValueError(f"resume checkpoint {record_id} has mismatched {key}")
    attempts = checkpoint.get("attempts")
    if not isinstance(attempts, list):
        raise ValueError(f"resume checkpoint {record_id} has invalid attempts")
    for attempt in attempts:
        if not isinstance(attempt, dict) or sha256_object(attempt.get("request")) != attempt.get("request_sha256"):
            raise ValueError(f"resume checkpoint {record_id} has invalid request hash")
        response = attempt.get("response")
        expected_response_sha = sha256_object(response) if response is not None else None
        if expected_response_sha != attempt.get("response_sha256"):
            raise ValueError(f"resume checkpoint {record_id} has invalid response hash")
    prediction = checkpoint.get("processed_prediction")
    expected_prediction_sha = sha256_object(prediction) if prediction is not None else None
    if checkpoint.get("processed_prediction_sha256") != expected_prediction_sha:
        raise ValueError(f"resume checkpoint {record_id} has invalid processed prediction hash")
    return checkpoint


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--prompt", required=True, type=Path)
    parser.add_argument("--schema", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--raw-dir", required=True, type=Path)
    parser.add_argument("--run-manifest", required=True, type=Path)
    parser.add_argument("--run-id", required=True)
    parser.add_argument("--controlled-root", required=True, type=Path)
    parser.add_argument("--model", required=True)
    parser.add_argument("--model-layer-sha256", required=True)
    parser.add_argument("--model-manifest", required=True, type=Path)
    parser.add_argument("--endpoint", default="http://127.0.0.1:11434/api/chat")
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--temperature", type=float, default=0.0)
    parser.add_argument("--top-k", type=int, default=1)
    parser.add_argument("--top-p", type=float, default=1.0)
    parser.add_argument("--num-ctx", type=int, default=8192)
    parser.add_argument("--timeout-seconds", type=int, default=600)
    parser.add_argument("--max-attempts", type=int, default=3)
    parser.add_argument("--resume", action="store_true")
    args = parser.parse_args()

    endpoint = urlparse(args.endpoint)
    if endpoint.scheme != "http" or endpoint.hostname not in {"127.0.0.1", "localhost", "::1"}:
        raise ValueError("restricted classifier permits only a loopback HTTP endpoint")
    for output in (args.output, args.run_manifest, args.raw_dir):
        require_within(output, args.controlled_root)
    require_distinct_outputs(args.output, args.run_manifest, args.raw_dir)
    if not re.fullmatch(r"[0-9a-f]{64}", args.model_layer_sha256):
        raise ValueError("model-layer-sha256 must be a lowercase SHA-256 digest")
    model_manifest_bytes = args.model_manifest.read_bytes()
    model_manifest_sha256 = hashlib.sha256(model_manifest_bytes).hexdigest()
    model_manifest = json.loads(model_manifest_bytes.decode("utf-8"))
    installed_digests = {
        item.get("digest", "").removeprefix("sha256:")
        for item in [model_manifest.get("config", {}), *model_manifest.get("layers", [])]
    }
    if args.model_layer_sha256 not in installed_digests:
        raise ValueError("declared model layer digest is absent from the installed model manifest")

    for output in (args.output, args.run_manifest):
        if output.exists():
            raise FileExistsError(f"refusing to overwrite: {output}")
    if args.raw_dir.exists() and any(args.raw_dir.iterdir()) and not args.resume:
        raise FileExistsError(f"raw output directory is not empty: {args.raw_dir}")

    prompt_bytes = args.prompt.read_bytes()
    schema_bytes = args.schema.read_bytes()
    dataset_bytes = args.dataset.read_bytes()
    prompt_sha256 = hashlib.sha256(prompt_bytes).hexdigest()
    schema_sha256 = hashlib.sha256(schema_bytes).hexdigest()
    dataset_sha256 = hashlib.sha256(dataset_bytes).hexdigest()
    prompt_template = prompt_bytes.decode("utf-8")
    render_prompt(prompt_template, "{}")
    schema = json.loads(schema_bytes.decode("utf-8"))
    with io.StringIO(dataset_bytes.decode("utf-8"), newline="") as stream:
        records = list(csv.DictReader(stream))
    if not records:
        raise ValueError("dataset is empty")
    if args.max_attempts < 1:
        raise ValueError("max-attempts must be at least 1")
    required_fields = {"id", "title", "body", "date", "source"}
    identifiers = []
    for record in records:
        if set(record) != required_fields or not all(record[field] for field in required_fields):
            raise ValueError("each dataset row must contain exactly five non-empty contract fields")
        if not SAFE_RECORD_ID.fullmatch(record["id"]):
            raise ValueError(f"unsafe record ID: {record['id']!r}")
        identifiers.append(record["id"])
    if len(identifiers) != len(set(identifiers)):
        raise ValueError("dataset contains duplicate record IDs")

    options = {
        "temperature": args.temperature,
        "seed": args.seed,
        "top_k": args.top_k,
        "top_p": args.top_p,
        "num_ctx": args.num_ctx,
    }
    live_model_metadata = post_json(
        show_endpoint(args.endpoint), {"model": args.model}, args.timeout_seconds
    )
    live_model_metadata_sha256 = sha256_object(live_model_metadata)
    environment_dir = args.raw_dir / "_environment"
    retained_manifest = environment_dir / "model-manifest.json"
    retained_show = environment_dir / "ollama-show.json"
    if args.resume and retained_manifest.exists():
        if retained_manifest.read_bytes() != model_manifest_bytes:
            raise ValueError("retained model manifest differs from resume input")
    else:
        write_bytes(retained_manifest, model_manifest_bytes)
    if args.resume and retained_show.exists():
        if sha256_object(json.loads(retained_show.read_text(encoding="utf-8"))) != live_model_metadata_sha256:
            raise ValueError("live Ollama model metadata differs from resumed run")
    else:
        write_json(retained_show, live_model_metadata)

    execution_fingerprint = sha256_object(
        {
            "dataset_sha256": dataset_sha256,
            "endpoint": args.endpoint,
            "live_model_metadata_sha256": live_model_metadata_sha256,
            "max_attempts": args.max_attempts,
            "model": args.model,
            "model_layer_sha256": args.model_layer_sha256,
            "model_manifest_sha256": model_manifest_sha256,
            "options": options,
            "prompt_sha256": prompt_sha256,
            "schema_sha256": schema_sha256,
        }
    )
    run_state_path = environment_dir / "run-state.json"
    if args.resume:
        if not run_state_path.is_file():
            raise ValueError("resume requires the retained run-state checkpoint")
        run_state = json.loads(run_state_path.read_text(encoding="utf-8"))
        if run_state.get("run_id") != args.run_id:
            raise ValueError("retained run state has a different run ID")
        if run_state.get("execution_fingerprint") != execution_fingerprint:
            raise ValueError("retained run state has a different execution fingerprint")
        started_at = run_state.get("started_at")
        if not isinstance(started_at, str) or not started_at:
            raise ValueError("retained run state has no valid start time")
    else:
        started_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
        write_json(
            run_state_path,
            {
                "run_id": args.run_id,
                "execution_fingerprint": execution_fingerprint,
                "started_at": started_at,
                "status": "in_progress",
            },
        )
    predictions = {}
    items = []
    runtime_version = subprocess.run(
        ["ollama", "--version"], check=True, capture_output=True, text=True
    ).stdout.strip()
    for record in records:
        input_sha256 = hashlib.sha256(record["body"].encode("utf-8")).hexdigest()
        article_json = json.dumps(record, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
        prompt = render_prompt(prompt_template, article_json)
        messages = [{"role": "user", "content": prompt}]
        attempts = []
        employment = None
        checkpoint_path = args.raw_dir / f"{record['id']}.json"
        if args.resume and checkpoint_path.exists():
            checkpoint = validate_checkpoint(
                json.loads(checkpoint_path.read_text(encoding="utf-8")),
                run_id=args.run_id,
                record_id=record["id"],
                input_sha256=input_sha256,
                execution_fingerprint=execution_fingerprint,
            )
            attempts = checkpoint["attempts"]
            employment = checkpoint.get("processed_prediction")
            if employment is not None:
                employment = validate_prediction(employment, record["body"])
            elif attempts:
                last_attempt = attempts[-1]
                messages = correction_messages(
                    last_attempt["request"]["messages"],
                    last_attempt.get("response"),
                    last_attempt.get("validation_error") or last_attempt.get("transport_error") or "unknown error",
                )
        else:
            write_json(
                checkpoint_path,
                {
                    "run_id": args.run_id,
                    "record_id": record["id"],
                    "input_sha256": input_sha256,
                    "execution_fingerprint": execution_fingerprint,
                    "attempt_count": 0,
                    "attempts": [],
                    "final_status": "in_progress",
                    "processed_prediction": None,
                    "processed_prediction_sha256": None,
                },
            )

        for attempt_number in range(len(attempts) + 1, args.max_attempts + 1):
            if employment is not None:
                break
            request_payload = {
                "model": args.model,
                "messages": messages,
                "stream": False,
                "format": schema,
                "options": options,
                "keep_alive": "10m",
            }
            request_started = time.monotonic()
            response = None
            transport_error = None
            validation_error = None
            normalization_actions = []
            try:
                response = post_json(args.endpoint, request_payload, args.timeout_seconds)
                if response.get("model") not in {None, args.model}:
                    raise RuntimeError(
                        f"response model {response.get('model')!r} differs from requested {args.model!r}"
                    )
                if not response.get("done"):
                    raise RuntimeError("model response was not complete")
                decoded = json.loads(response["message"]["content"])
                grounded, normalization_actions = ground_evidence(decoded, record["body"])
                employment = validate_prediction(grounded, record["body"])
            except (urllib.error.URLError, TimeoutError, OSError) as error:
                transport_error = f"{type(error).__name__}: {error}"
            except (KeyError, TypeError, AttributeError, json.JSONDecodeError, RuntimeError, ValueError) as error:
                validation_error = str(error)
            elapsed_ms = round((time.monotonic() - request_started) * 1000)
            attempts.append(
                {
                    "attempt": attempt_number,
                    "request": request_payload,
                    "request_sha256": sha256_object(request_payload),
                    "response": response,
                    "response_sha256": sha256_object(response) if response is not None else None,
                    "elapsed_ms": elapsed_ms,
                    "transport_error": transport_error,
                    "validation_error": validation_error,
                    "normalization_actions": (
                        normalization_actions
                        if validation_error is None and transport_error is None
                        else []
                    ),
                }
            )
            final_status = "valid" if employment is not None else (
                "failed" if attempt_number == args.max_attempts else "retry_pending"
            )
            write_json(
                checkpoint_path,
                {
                    "run_id": args.run_id,
                    "record_id": record["id"],
                    "input_sha256": input_sha256,
                    "execution_fingerprint": execution_fingerprint,
                    "attempt_count": len(attempts),
                    "attempts": attempts,
                    "final_status": final_status,
                    "processed_prediction": employment,
                    "processed_prediction_sha256": (
                        sha256_object(employment) if employment is not None else None
                    ),
                },
            )
            if employment is not None:
                break
            messages = correction_messages(
                messages,
                response,
                validation_error or transport_error or "unknown error",
            )
        if employment is None:
            raise ValueError(f"no valid prediction after {args.max_attempts} attempts for {record['id']}")
        predictions[record["id"]] = {
            "nlp": {"status": "not_executed_in_employment_stage"},
            "ner": {"status": "not_executed_in_employment_stage", "entities": []},
            "employment": employment,
            "emtak": {"code": "NOT_EVALUATED", "label": "Not evaluated in employment-stage run", "confidence": None},
        }
        final_attempt = attempts[-1]
        items.append(
            {
                "record_id": record["id"],
                "input_sha256": input_sha256,
                "request_sha256": final_attempt["request_sha256"],
                "response_sha256": final_attempt["response_sha256"],
                "prediction_sha256": sha256_object(employment),
                "attempt_count": len(attempts),
                "elapsed_ms": sum(attempt["elapsed_ms"] for attempt in attempts),
            }
        )

    write_json(args.output, predictions)
    completed_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    manifest = {
        "schema_version": "1.0",
        "run_id": args.run_id,
        "provider": "local-ollama",
        "endpoint_scope": "localhost",
        "model_tag": args.model,
        "model_layer_sha256": args.model_layer_sha256,
        "model_manifest_sha256": model_manifest_sha256,
        "live_model_metadata_sha256": live_model_metadata_sha256,
        "execution_fingerprint": execution_fingerprint,
        "runtime_version": runtime_version,
        "execution_environment": {
            "platform": platform.platform(),
            "machine": platform.machine(),
            "python": sys.version.split()[0],
        },
        "generation_options": options,
        "max_attempts": args.max_attempts,
        "prompt_sha256": prompt_sha256,
        "schema_sha256": schema_sha256,
        "dataset_sha256": dataset_sha256,
        "predictions_sha256": file_sha256(args.output),
        "started_at": started_at,
        "completed_at": completed_at,
        "record_count": len(records),
        "items": items,
    }
    write_json(args.run_manifest, manifest)
    write_json(
        run_state_path,
        {
            "run_id": args.run_id,
            "execution_fingerprint": execution_fingerprint,
            "started_at": started_at,
            "completed_at": completed_at,
            "status": "complete",
            "predictions_sha256": manifest["predictions_sha256"],
            "run_manifest_sha256": file_sha256(args.run_manifest),
        },
    )
    print(json.dumps({"run_id": args.run_id, "records": len(records), "predictions_sha256": manifest["predictions_sha256"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
