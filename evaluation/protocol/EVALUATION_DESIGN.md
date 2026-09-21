# Fixed evaluation design

## Evaluation sample

The sample was frozen before model execution as 12 Estonian employment-related
articles covering apparent job gain, job loss, no-event, and ambiguous or
difficult cases. The exact source PDFs, manifest, URLs, and checksums are public
under [`../data/employment-sample-v1/`](../data/employment-sample-v1/) with
written ERR permission. Preliminary labels and unreviewed item-level results
remain controlled.

Two independent researchers must review the reference fields: event type,
employing organization, job count when explicit, evidence span, and expected
disposition. Record disagreements and their resolution; do not claim a
large-sample accuracy benchmark. EMTAK was not executed in this pilot.

## Runs

- **Run-0:** baseline execution with the frozen sample, contract, models,
  prompts, mappings, and acceptance policy.
- **Run-1:** separate repeat on the same local setup with exactly the same
  substantive configuration.
- **Run-Var:** the frozen Run-0 predictions were reused and only
  `employment_confidence_threshold` changed from 0.70 to 0.90. This is an
  acceptance-policy variation, not a third model invocation.

Run directories must be isolated. A failed item makes the run incomplete; the
orchestrator must not suppress the failure.

## Comparison semantics

Compare canonical semantic fields separately from run-specific provenance.
Timestamps and run IDs are expected to differ. Employment-event type, job
count, organization, EMTAK placeholder, and acceptance decision are the five
declared comparison fields. The EMTAK value is `NOT_EVALUATED`, so it records
the contract boundary rather than a produced classification; the evidence
hash is retained as a diagnostic field outside this comparison core.

## Acceptance outcomes

The versioned policy defines accepted, conditional, and rejected outcomes. Each
validation report must identify the rule, observed field, severity, and evidence
pointer. The sample or controlled negative fixtures must exercise all outcome
classes.

## Trace walkthroughs

Choose at least three statements using a rule fixed before inspecting their
trace results. The current controlled walkthroughs recover source references
and hashes, ordered steps, model/configuration, contract version, validation
report, and acceptance decision. Intermediate-artifact retrieval is required
where those artifacts are retained, but is not claimed for the current pilot.

## Required result tables

1. sample composition and reference-review summary;
2. Run-0/Run-1 core RDF and decision agreement;
3. Run-Var differences and attribution to the changed factor;
4. accepted/conditional/rejected distribution;
5. trace-link and competency-query success;
6. legacy versus enhanced traceability coverage.
