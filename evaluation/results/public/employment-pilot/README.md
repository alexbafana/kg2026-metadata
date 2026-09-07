# Employment-stage pilot evidence

This directory contains disclosure-screened aggregate evidence from the
12-item employment sample. The exact source PDFs and manifest are public under
[`../../../data/employment-sample-v1/`](../../../data/employment-sample-v1/),
allowing third parties to inspect the evaluated sources and reconstruct the
normalized input. Raw model requests and responses, preliminary labels,
evidence quotations, and unreviewed per-item predictions remain controlled.

The aggregate agreement values are **provisional** until two independent
reviewers inspect the reference projection and adjudicate disagreements.
They must not be cited as final accuracy results.

Demonstrated now:

- a digest-pinned local LLM employment stage executed on 12 controlled inputs;
- a separate identical-configuration repeat on the same local setup;
- an acceptance-threshold variant with one attributable decision change;
- deterministic schema/evidence/count validation;
- RDFLib and Apache Jena RIOT parsing of all 36 generated Turtle artifacts;
- three successful SPARQL trace walkthroughs.

See [`aggregate-summary.json`](aggregate-summary.json) for the minimized
machine-readable results, [`VALIDATION.md`](VALIDATION.md) for technical checks,
and [`PRIVACY_REVIEW.md`](PRIVACY_REVIEW.md) for the public-diff screening record.

Still not demonstrated:

- general or population-level classification accuracy;
- rerun NLP, NER, or EMTAK classification;
- independent replication on a separate model installation; or
- final reference-based metrics before the two-reviewer process is complete.
