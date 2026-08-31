#!/usr/bin/env python3
"""Assemble Section VI evidence from a dataset and recorded stage outputs.

The public fixture adapter demonstrates the contract, provenance, trajectory,
RDF, and acceptance path. It is not an NLP/LLM implementation and its results
must not be reported as empirical paper evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import quote


STAGES = [
    "ingest",
    "parse",
    "nlp",
    "ner",
    "employment_classification",
    "emtak_classification",
    "provenance_generation",
    "trajectory_generation",
    "rdf_mapping",
    "acceptance_validation",
]
EVENT_TYPES = {"job_gain", "job_loss", "no_event", "ambiguous"}
SAFE_RECORD_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def canonical_bytes(value: object) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256(value: object) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def write_json(path: Path, value: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")


def literal(value: object) -> str:
    return json.dumps(str(value), ensure_ascii=False)


def iri(kind: str, value: str) -> str:
    return f"https://w3id.org/kg2026/{kind}/{quote(value, safe='')}"


def check(rule_id: str, passed: bool, severity: str, evidence: str) -> dict[str, str]:
    return {
        "rule_id": rule_id,
        "status": "pass" if passed else "fail",
        "severity": severity,
        "evidence": evidence,
    }


def validation_report(record: dict[str, str], prediction: dict, config: dict) -> dict:
    employment = prediction.get("employment", {})
    event_type = employment.get("event_type")
    job_count = employment.get("job_count")
    confidence = employment.get("confidence")
    evidence_text = employment.get("evidence_text", "")
    gain_or_loss = event_type in {"job_gain", "job_loss"}

    checks = [
        check(
            "R-INPUT-COMPLETE",
            all(record.get(field) for field in ("id", "body", "date", "source")),
            "reject",
            "dataset row fields id/body/date/source",
        ),
        check("R-EVENT-TYPE", event_type in EVENT_TYPES, "reject", f"employment.event_type={event_type!r}"),
        check(
            "R-JOB-COUNT",
            job_count is None or (isinstance(job_count, int) and not isinstance(job_count, bool) and job_count >= 0),
            "reject",
            f"employment.job_count={job_count!r}",
        ),
        check(
            "R-EVIDENCE",
            not gain_or_loss or (bool(evidence_text.strip()) and evidence_text in record["body"]),
            "conditional",
            "employment.evidence_text must be an exact normalized-source substring",
        ),
        check(
            "R-CONFIDENCE",
            not gain_or_loss or (isinstance(confidence, (int, float)) and confidence >= config["employment_confidence_threshold"]),
            "conditional",
            f"confidence={confidence!r}; threshold={config['employment_confidence_threshold']}",
        ),
        check("R-PROVENANCE", True, "reject", "generated assertion/activity/source links"),
        check("R-TRAJECTORY", True, "reject", "generated assertion/trajectory/contract links"),
    ]
    failed = [item for item in checks if item["status"] == "fail"]
    if any(item["severity"] == "reject" for item in failed):
        decision = "rejected"
    elif failed:
        decision = "conditional"
    else:
        decision = "accepted"
    return {"record_id": record["id"], "run_id": config["run_id"], "decision": decision, "checks": checks}


def turtle(record: dict[str, str], prediction: dict, config: dict, provenance: dict, trajectory: dict, report: dict) -> str:
    record_id = record["id"]
    run_id = config["run_id"]
    employment = prediction["employment"]
    emtak = prediction["emtak"]
    article = iri("article", record_id)
    assertion = iri("assertion", f"{record_id}-employment")
    run = iri("run", run_id)
    source = iri("source", record_id)
    traj = iri("trajectory", trajectory["trajectory_id"])
    decision = iri("decision", f"{run_id}-{record_id}")
    contract = iri("contract", f"TC-NLP-RDF-{config['contract_version']}")
    model = iri("model", f"{config['model']['name']}-{config['model']['version']}")
    lines = [
        "@prefix dcterms: <http://purl.org/dc/terms/> .",
        "@prefix ex: <https://w3id.org/kg2026/schema/> .",
        "@prefix prov: <http://www.w3.org/ns/prov#> .",
        "@prefix rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#> .",
        "@prefix ver: <https://w3id.org/kg2026/version/> .",
        "@prefix xsd: <http://www.w3.org/2001/XMLSchema#> .",
        "",
        f"<{article}> a ex:Article ; ex:hasEmploymentAssertion <{assertion}> .",
        f"<{source}> a prov:Entity ; ex:sha256 {literal(provenance['source_sha256'])} ; ex:normalizedTextSha256 {literal(provenance['normalized_text_sha256'])} .",
        f"<{assertion}> a rdf:Statement, ex:EmploymentAssertion ;",
        f"  rdf:subject <{article}> ;",
        "  rdf:predicate ex:employmentEvent ;",
        f"  rdf:object {literal(employment['event_type'])} ;",
        f"  ex:employmentEvent {literal(employment['event_type'])} ;",
        f"  ex:confidence {employment['confidence']} ;",
        f"  ex:evidenceSha256 {literal(provenance['evidence_sha256'])} ;",
        f"  prov:wasDerivedFrom <{source}> ;",
        f"  prov:wasGeneratedBy <{run}> ;",
        f"  ver:hasProcessingTrajectory <{traj}> ;",
        f"  ex:governedBy <{contract}> ;",
        f"  ex:validatedBy <{decision}> .",
    ]
    if employment.get("job_count") is not None:
        lines.append(f"<{assertion}> ex:jobCount {employment['job_count']} .")
    if employment.get("organization"):
        lines.append(f"<{assertion}> ex:organization {literal(employment['organization'])} .")
    if emtak.get("code") and emtak.get("code") != "NOT_EVALUATED":
        lines.append(f"<{assertion}> ex:hasEMTAKCode {literal(emtak['code'])} .")
    lines.extend(
        [
            f"<{run}> a prov:Activity, ex:PipelineRun ; prov:used <{source}> ; ex:usedModel <{model}> ; ex:boundToContract <{contract}> .",
            f"<{traj}> a ex:ProcessingTrajectory ; ex:run <{run}> ; ex:branchTaken {literal(report['decision'])} .",
            f"<{decision}> a ex:AcceptanceDecision ; ex:outcome {literal(report['decision'])} .",
            f"<{contract}> a ex:TransformationContract ; dcterms:hasVersion {literal(config['contract_version'])} .",
            f"<{model}> a prov:SoftwareAgent ; dcterms:hasVersion {literal(config['model']['version'])} ; ex:promptVersion {literal(config['model']['prompt_version'])} .",
        ]
    )
    for step in trajectory["steps"]:
        step_iri = iri("step", f"{trajectory['trajectory_id']}-{step['position']:02d}")
        lines.append(
            f"<{traj}> ex:hasStep <{step_iri}> . <{step_iri}> a ex:ProcessingStep ; ex:position {step['position']} ; ex:stage {literal(step['stage'])} ; ex:mode {literal(step['mode'])} ."
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dataset", required=True, type=Path)
    parser.add_argument("--predictions", required=True, type=Path)
    parser.add_argument("--config", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--extraction-manifest", type=Path)
    args = parser.parse_args()

    config = json.loads(args.config.read_text(encoding="utf-8"))
    predictions = json.loads(args.predictions.read_text(encoding="utf-8"))
    with args.dataset.open(encoding="utf-8", newline="") as stream:
        records = list(csv.DictReader(stream))
    if not records:
        raise ValueError("dataset is empty")
    record_ids = [record["id"] for record in records]
    if len(record_ids) != len(set(record_ids)):
        raise ValueError("dataset contains duplicate record IDs")
    if any(not SAFE_RECORD_ID.fullmatch(record_id) for record_id in record_ids):
        raise ValueError("dataset contains unsafe record IDs")
    if set(record_ids) != set(predictions):
        raise ValueError(
            f"prediction IDs differ: missing={sorted(set(record_ids) - set(predictions))}, "
            f"extra={sorted(set(predictions) - set(record_ids))}"
        )
    if args.output.exists() and any(args.output.iterdir()):
        raise FileExistsError(f"output directory is not empty: {args.output}")

    extraction_records = {}
    extraction_manifest_sha = None
    if args.extraction_manifest:
        extraction = json.loads(args.extraction_manifest.read_text(encoding="utf-8"))
        extraction_records = {item["record_id"]: item for item in extraction["records"]}
        if set(extraction_records) != set(record_ids):
            raise ValueError("extraction-manifest record IDs differ from dataset")
        if extraction["dataset_sha256"] != hashlib.sha256(args.dataset.read_bytes()).hexdigest():
            raise ValueError("extraction-manifest dataset hash mismatch")
        extraction_manifest_sha = hashlib.sha256(args.extraction_manifest.read_bytes()).hexdigest()

    generated_at = datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    decisions = {"accepted": 0, "conditional": 0, "rejected": 0}
    per_record = []
    for record in records:
        record_id = record["id"]
        prediction = predictions[record_id]
        extraction_record = extraction_records.get(record_id)
        source_sha = extraction_record["pdf_sha256"] if extraction_record else sha256(record)
        normalized_text_sha = (
            extraction_record["normalized_text_sha256"]
            if extraction_record
            else hashlib.sha256(record["body"].encode("utf-8")).hexdigest()
        )
        evidence_sha = hashlib.sha256(prediction["employment"].get("evidence_text", "").encode("utf-8")).hexdigest()
        report = validation_report(record, prediction, config)
        decisions[report["decision"]] += 1
        trajectory = {
            "trajectory_id": f"{config['run_id']}-{record_id}",
            "run_id": config["run_id"],
            "record_id": record_id,
            "contract_version": config["contract_version"],
            "steps": [
                {
                    "position": position,
                    "stage": stage,
                    "mode": config.get("stage_modes", {}).get(stage, config.get("stage_mode", "unspecified")),
                }
                for position, stage in enumerate(STAGES, start=1)
            ],
        }
        provenance = {
            "run_id": config["run_id"],
            "record_id": record_id,
            "generated_at": generated_at,
            "source_sha256": source_sha,
            "normalized_text_sha256": normalized_text_sha,
            "evidence_sha256": evidence_sha,
            "model": config["model"],
            "config_sha256": sha256(config),
        }
        item_dir = args.output / "evidence" / record_id
        write_json(item_dir / "parsed.json", record)
        write_json(item_dir / "nlp.json", prediction["nlp"])
        write_json(item_dir / "ner.json", prediction["ner"])
        write_json(item_dir / "employment.json", prediction["employment"])
        write_json(item_dir / "emtak.json", prediction["emtak"])
        write_json(item_dir / "provenance.json", provenance)
        write_json(item_dir / "trajectory.json", trajectory)
        write_json(item_dir / "validation.json", report)
        ttl = turtle(record, prediction, config, provenance, trajectory, report)
        rdf_path = args.output / "rdf" / f"{record_id}.ttl"
        rdf_path.parent.mkdir(parents=True, exist_ok=True)
        rdf_path.write_text(ttl, encoding="utf-8")
        core = {
            "record_id": record_id,
            "event_type": prediction["employment"]["event_type"],
            "job_count": prediction["employment"].get("job_count"),
            "organization": prediction["employment"].get("organization"),
            "emtak_code": prediction["emtak"].get("code"),
            "acceptance_decision": report["decision"],
        }
        per_record.append({**core, "core_sha256": sha256(core)})

    manifest = {
        "run_id": config["run_id"],
        "run_type": config["run_type"],
        "generated_at": generated_at,
        "record_count": len(records),
        "dataset_sha256": hashlib.sha256(args.dataset.read_bytes()).hexdigest(),
        "predictions_sha256": hashlib.sha256(args.predictions.read_bytes()).hexdigest(),
        "extraction_manifest_sha256": extraction_manifest_sha,
        "config": config,
        "config_sha256": sha256(config),
    }
    aggregate = {"run_id": config["run_id"], "record_count": len(records), "decisions": decisions, "per_record": per_record}
    write_json(args.output / "run-manifest.json", manifest)
    write_json(args.output / "aggregate-results.json", aggregate)
    print(json.dumps({"output": str(args.output), **aggregate["decisions"]}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
