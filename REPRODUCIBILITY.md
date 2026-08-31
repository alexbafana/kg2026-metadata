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

Run-0, Run-1, and Run-Var therefore remain **pending**. They must not be started
until a frozen, rights-approved evaluation manifest, an executed environment
lock, isolated per-run output directories, failure-propagating orchestration,
and complete provenance/trajectory generation are implemented. Run-Var must
change one recorded factor only.

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

## Release boundary

A GitHub tag or DOI freezes the package; it does not repair missing evidence.
The citable Section VI release is therefore pending completion and review of the
items above. A version-specific DOI must be inserted into `CITATION.cff` only
after the archive has actually minted it.
