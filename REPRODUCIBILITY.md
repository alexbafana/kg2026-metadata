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
The exact 12 PDF inputs and source manifest are public under
[`evaluation/data/employment-sample-v1/`](evaluation/data/employment-sample-v1/),
so third parties can reconstruct the normalized evaluation input. Raw model
I/O, preliminary labels, and unreviewed item-level results remain outside Git.
Reviewer-safe aggregates are retained in
[`evaluation/results/public/employment-pilot/`](evaluation/results/public/employment-pilot/).

The claim-aligned harness provides isolated output directories, explicit
contract/version fields, ordered trajectories, PROV-linked RDF, and fail-fast
acceptance reports. Its public fixture runs demonstrate that machinery only;
they use recorded author-created fixture predictions. Separately, the
employment pilot used a digest-pinned local Llama 3.2 invocation and retained
invocation evidence in controlled storage. Public source availability now
permits rerunning that stage with the declared setup. That execution does not
demonstrate rerunning the upstream NLP, NER, or EMTAK stages.

## Executed RDF audit

The retained public result reports only aggregate counts and corpus-level
integrity information. It excludes body text, titles, named entities,
per-article classifications, and per-record hashes. Commands and engine version
are documented in [`evaluation/EXECUTED_AUDIT.md`](evaluation/EXECUTED_AUDIT.md).

## Traceability boundary

Three legacy controlled correspondence candidates were checked across
plaintext, metadata, entity inventory, EMTAK output, and RDF. Those legacy
checks establish artifact correspondence only: the legacy RDF has no
`prov:wasGeneratedBy` or `ver:hasProcessingTrajectory` links. By contrast, the
enhanced 12-item employment pilot generated those links and demonstrated three
complete trace walkthroughs. Source PDFs are public; detailed unreviewed
item-level run evidence remains controlled.

## Claim-aligned protocol

The authoritative evaluation requirements are in
[`evaluation/protocol/CLAIM_EVIDENCE_MATRIX.md`](evaluation/protocol/CLAIM_EVIDENCE_MATRIX.md).
The legacy 162-file audit is the before-state. The controlled employment sample
and genuine local model runs now supply the bounded pilot evidence; its
reference-based metrics remain provisional pending independent review.

## Release boundary

A GitHub tag or DOI freezes the package; it does not repair missing evidence.
The technical pilot is complete, but its preliminary reference labels and
public-release boundary still require review by two independent reviewers.
The citable Section VI release therefore remains pending that review and any
resulting corrections. A version-specific DOI must be inserted into
`CITATION.cff` only after the archive has actually minted it.
