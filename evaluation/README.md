# Section VI evaluation protocol

The public evidence index starts in a **pending** state. Populate it only after
a controlled-access run completes and the proposed public artifact has passed
rights/privacy review.

For each run, preserve in restricted storage: input manifest and hashes,
versions/configuration, command log, per-item pipeline artifacts, provenance
and trajectory records, RDF, validation report, and query output. Keep Run-0,
Run-1, and Run-Var separate. Run-Var must change exactly one documented factor.

Public publication may report approved aggregate outcomes and integrity hashes.
Use the scripts in `scripts/` inside the controlled environment. A validation
script or query template is not evidence until it has completed successfully and
its output is retained.

The query templates in `queries/` avoid returning article body text, titles,
entity values, or classifications. The executed aggregate audit and precise
claim boundary are in `EXECUTED_AUDIT.md` and `evidence-status.json`.
