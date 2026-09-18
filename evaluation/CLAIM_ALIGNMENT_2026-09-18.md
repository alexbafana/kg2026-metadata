# Manuscript claim–evidence alignment (2026-09-18)

This note supplements, but does not revise, the fixed evaluation protocol.
It maps the current manuscript's architecture to the evidence actually
available after the supplementary checks.

| Design element | Evidence available now | Boundary |
| --- | --- | --- |
| Public running-case sources | Exact 12 ERR PDF captures and manifest in this repository, with written ERR permission | Per-item model predictions and run packages remain controlled |
| Employment-stage repeatability | Controlled aggregate reports 12/12 identical five-field cores and decisions; prediction-file digests match | Not independent replication on a second installation |
| Policy variation | Controlled aggregate reports one changed decision under threshold 0.70 to 0.90; public synthetic fixture demonstrates the same mechanism | Controlled per-item causal lineage is not public |
| RDF syntax | Original controlled record reports 36/36 RDFLib and RIOT parses | Parsing is not semantic validation |
| Trace-shape conformance | Supplementary Jena SHACL check reports 36/36 conformant files | Shapes cover selected links, confidence bounds, steps, and outcomes only |
| Statement trace retrieval | Original 3/3 controlled walkthroughs; supplementary mode query succeeds for 36/36 files with ten stage rows each | Query results and RDF remain controlled; no explicit assertion-to-JSON or exact-fragment link |
| Reference agreement | Provisional 6/12 event-type and 4/5 eligible count agreement | Independent second review and adjudication pending |
| Complete pipeline, standalone trace bundle, ledger anchor, human-review route | Proposed design or future work | Not evaluated by these checks |

The supplementary check method, version, and aggregate counts are in
[`results/public/employment-pilot/SUPPLEMENTARY_VALIDATION.md`](results/public/employment-pilot/SUPPLEMENTARY_VALIDATION.md).
No aggregate result should be read as proof of factual correctness of an
individual employment claim or population-level accuracy.
