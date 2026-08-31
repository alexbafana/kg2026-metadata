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

The detailed logs, RDF files, query results, raw model I/O, and per-item outputs
remain controlled because they may reproduce or reveal restricted source
content. These counts report successful technical checks, not independent
review of the reference labels or population-level classifier accuracy.
