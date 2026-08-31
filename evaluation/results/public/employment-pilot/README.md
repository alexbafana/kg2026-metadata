# Employment-stage pilot evidence

This directory contains only disclosure-screened aggregate evidence from the
controlled 12-item employment sample. The source PDFs, normalized article text,
raw model requests and responses, evidence quotations, and per-item predictions
remain in controlled storage and are not part of this repository.

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

Not demonstrated:

- general or population-level classification accuracy;
- rerun NLP, NER, or EMTAK classification;
- public reproducibility of the restricted article texts;
- legal permission to redistribute publisher content.
