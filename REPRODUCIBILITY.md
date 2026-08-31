# Reproducibility status

This repository separates executable methods from demonstrated evidence. A
script, query, or protocol is not evidence until its command completed and the
result was retained. The current status is recorded in
[`evaluation/evidence-status.json`](evaluation/evidence-status.json).

## Deterministic and external stages

Parsing an existing Turtle artifact with a fixed RIOT version and executing a
fixed SPARQL query over it are deterministic for the retained input bytes. The
legacy pipeline as a whole is not currently reproducible: dependencies and
model revisions are unpinned, models may be downloaded at runtime, the EMTAK
stage calls an external API, RDF generation writes the wall-clock time, and the
pipeline writes into shared output locations.

The legacy pipeline as a whole was not rerun. A narrower employment-stage pilot
was executed against a frozen controlled 12-item sample. Run-0 and Run-1 used
identical substantive settings; Run-Var reused the retained Run-0 predictions
and changed only the declared acceptance threshold from `0.70` to `0.90`.
Source material, normalized text, raw model I/O, preliminary labels, and
item-level results remain outside Git. Reviewer-safe aggregates are retained in
[`evaluation/results/public/employment-pilot/`](evaluation/results/public/employment-pilot/).

The claim-aligned harness provides isolated output directories, explicit
contract/version fields, ordered trajectories, PROV-linked RDF, and fail-fast
acceptance reports. Its public fixture runs demonstrate that machinery only;
they use recorded author-created fixture predictions. Separately, the
controlled employment pilot used a digest-pinned local Llama 3.2 invocation and
retained invocation evidence in controlled storage. That execution does not
demonstrate rerunning the upstream NLP, NER, or EMTAK stages.

## Executed RDF audit

The retained public result reports only aggregate counts and corpus-level
integrity information. It excludes body text, titles, named entities,
per-article classifications, and per-record hashes. Commands and engine version
are documented in [`evaluation/EXECUTED_AUDIT.md`](evaluation/EXECUTED_AUDIT.md).

## Traceability boundary

Three controlled artifacts were checked for correspondence between plaintext,
metadata, entity inventory, EMTAK output, and RDF. Those checks establish
artifact correspondence only. They do not establish complete source-to-RDF
provenance because the retained RDF has no `prov:wasGeneratedBy` or
`ver:hasProcessingTrajectory` links and the source inventory lacks verified
retrieval records for most items. Detailed hashes remain restricted.

## Claim-aligned protocol

The authoritative evaluation requirements are in
[`evaluation/protocol/CLAIM_EVIDENCE_MATRIX.md`](evaluation/protocol/CLAIM_EVIDENCE_MATRIX.md).
The legacy 162-file audit is the before-state; the paper's empirical claims
require the controlled real employment sample and genuine model runs.

## Release boundary

A GitHub tag or DOI freezes the package; it does not repair missing evidence.
The technical pilot is complete, but its preliminary reference labels and
public-release boundary still require review by two independent reviewers.
The citable Section VI release therefore remains pending that review and any
resulting corrections. A version-specific DOI must be inserted into
`CITATION.cff` only after the archive has actually minted it.
