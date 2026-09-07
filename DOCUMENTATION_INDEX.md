# Documentation map

This repository is the public reproducibility companion for Section VI of the
NLP-to-knowledge-graph paper. It contains methods, contracts, synthetic
fixtures, legacy aggregate evidence, disclosure-screened pilot aggregates, and
the exact 12 ERR source PDFs used by the employment-stage evaluation. Raw model
I/O, preliminary labels, and unreviewed item-level predictions remain outside
the public tree.

## Start here

| Question | Document or directory |
| --- | --- |
| What is this repository and what can it support? | [`README.md`](README.md) |
| What is demonstrated, provisional, or pending? | [`REPRODUCIBILITY.md`](REPRODUCIBILITY.md) and [`evaluation/evidence-status.json`](evaluation/evidence-status.json) |
| Which paper claims are evaluated? | [`evaluation/protocol/CLAIM_EVIDENCE_MATRIX.md`](evaluation/protocol/CLAIM_EVIDENCE_MATRIX.md) |
| How was the controlled pilot designed? | [`evaluation/protocol/EVALUATION_DESIGN.md`](evaluation/protocol/EVALUATION_DESIGN.md) |
| What data was used and why? | [`evaluation/DATASET_CARD.md`](evaluation/DATASET_CARD.md) |
| Where are the 12 source articles? | [`evaluation/data/employment-sample-v1/`](evaluation/data/employment-sample-v1/) |
| Where are the public pilot results? | [`evaluation/results/public/employment-pilot/`](evaluation/results/public/employment-pilot/) |
| How do I run the public smoke test? | [`evaluation/harness/README.md`](evaluation/harness/README.md) |
| How are controlled inputs/model outputs produced? | [`evaluation/stages/README.md`](evaluation/stages/README.md) |
| How must independent reviewers check the evidence? | [`evaluation/protocol/INDEPENDENT_REVIEW.md`](evaluation/protocol/INDEPENDENT_REVIEW.md) |
| Which materials are public or controlled? | [`DATA_ACCESS.md`](DATA_ACCESS.md) and [`SECURITY.md`](SECURITY.md) |
| What did the legacy baseline show? | [`evaluation/EXECUTED_AUDIT.md`](evaluation/EXECUTED_AUDIT.md) |

## Repository layers

1. `pipeline/` preserves the historical implementation for inspection. It was
   not rerun as the Section VI experiment.
2. `evaluation/fixtures/public/` provides author-created smoke-test data that
   anyone can execute without controlled access.
3. `evaluation/contracts/`, `evaluation/harness/`, `evaluation/stages/`, and
   `evaluation/queries/` contain the evaluation method.
4. `evaluation/data/employment-sample-v1/` contains the frozen 12 PDFs and
   source manifest needed to reconstruct the normalized evaluation input.
5. `evaluation/results/public/` contains synthetic results and
   disclosure-screened aggregates. Raw invocations, unreviewed item-level run
   evidence, and preliminary references remain outside GitHub.

## Current result in one paragraph

The local Llama 3.2 employment stage processed all 12 controlled inputs twice
with identical substantive settings; the prediction-file hash, 12/12 canonical
semantic outputs, and 12/12 acceptance decisions matched. A threshold-only
variant changed one decision. RDFLib and Apache Jena RIOT parsed all 36
generated Turtle artifacts, and three SPARQL trace walkthroughs succeeded. The
preliminary event-type agreement is 6/12 (macro-F1 0.310), and exact job-count
agreement is 4/5 eligible items. Those reference-based values remain
provisional pending two independent reviews; they are not population-level
accuracy estimates.

## What a third party can reproduce now

- run the three-item public synthetic fixture and inspect its evidence package;
- inspect and checksum the exact 12 ERR source captures;
- reconstruct the normalized 12-item input and rerun the employment stage with
  the declared model setup;
- inspect the schemas, acceptance contract, prompt, queries, comparison code,
  and scorer;
- verify public aggregate hashes and documented validation counts; and
- inspect the independent-review and privacy/release protocol.

The source-input barrier has been removed: the 12 PDFs and their manifest are
now public with written ERR permission. Exact reproduction still depends on the
declared software/model environment, while verification of preliminary labels
and unreviewed item-level run evidence follows [`DATA_ACCESS.md`](DATA_ACCESS.md).

## Release checklist

The technical pilot and post-commit verification are complete. Before citing a
fixed repository artifact in Section VI, the project must still:

1. retain the written ERR permission and the released source checksums;
2. obtain two independent item-level reference reviews and adjudicate any
   disagreement;
3. obtain independent technical and privacy/rights review of the frozen public
   diff and controlled evidence;
4. apply required corrections and freeze a reviewed commit;
5. create a GitHub release/tag; and
6. archive that exact release and add the minted DOI to `CITATION.cff`.

Until then, technical execution claims are demonstrated, reference-agreement
values are provisional, and the DOI/release are pending.
