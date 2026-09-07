# Validation record

Validation was executed on 2026-08-31 against the controlled Run-0, Run-1, and
Run-Var packages.

- Python unit tests: 20 passed, 0 failed.
- RDFLib 7.6.0 Turtle parsing: 36 passed, 0 failed.
- Apache Jena RIOT 6.2.0 Turtle validation: 36 passed, 0 failed.
- SPARQL trace walkthroughs: 3 passed, 0 failed.
- Run-0 versus Run-1: 12/12 canonical semantic outputs and 12/12 acceptance
  decisions identical.
- Run-0 versus Run-Var: the only declared configuration change was the
  employment-confidence threshold (`0.70` to `0.90`); one acceptance decision
  changed and 11 did not.

The exact source PDFs and manifest are public. Detailed logs, RDF files, query
results, raw model I/O, and unreviewed per-item outputs remain controlled. These
counts report successful technical checks, not independent review of the
reference labels or population-level classifier accuracy.

Public checks from the repository root:

```bash
python3 -m pip install -r evaluation/requirements-validation.txt
python3 -m unittest discover -s tests -v
python3 evaluation/scripts/privacy_scan.py .
```

Controlled reviewers validate each generated Turtle file with `riot --validate`
and execute `evaluation/scripts/query_rdf.py` with a controlled Turtle input,
one of the queries under `evaluation/queries/`, and an output path inside the
controlled package. The controlled `ALL_SHA256SUMS.txt` inventories the retained
logs, RDF, comparisons, queries, raw invocations, and post-commit verification
artifacts. It is withheld because its relative paths expose item identifiers.
