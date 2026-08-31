# Fixed evaluation design

## Evaluation sample

Freeze 10–12 restricted Estonian employment-related articles before executing
the real runs. Selection must follow a documented rule and cover job gain, job
loss, no-event, and ambiguous cases. Record only opaque IDs and approved
aggregates publicly. Source snapshots and labels remain controlled.

Two researchers should review the reference fields: event type, employing
organization, job count when explicit, evidence span, EMTAK context, and
expected disposition. Record disagreements and their resolution; do not claim a
large-sample accuracy benchmark.

## Runs

- **Run-0:** baseline execution with the frozen sample, contract, models,
  prompts, mappings, and acceptance policy.
- **Run-1:** independent repeat with exactly the same substantive configuration.
- **Run-Var:** repeat with one declared factor changed. The preferred minimal
  factor is `employment_confidence_threshold`; all other substantive fields
  remain identical.

Run directories must be isolated. A failed item makes the run incomplete; the
orchestrator must not suppress the failure.

## Comparison semantics

Compare canonical core RDF separately from run-specific provenance. Timestamps,
run IDs, and generated evidence hashes are expected to differ. Employment-event
type, job count, organization, EMTAK assertion, and acceptance decision are core
comparison fields.

## Acceptance outcomes

The versioned policy defines accepted, conditional, and rejected outcomes. Each
validation report must identify the rule, observed field, severity, and evidence
pointer. The sample or controlled negative fixtures must exercise all outcome
classes.

## Trace walkthroughs

Choose at least three statements using a rule fixed before inspecting their
trace results. Each walkthrough must recover source evidence, intermediate
artifacts, ordered steps, model/configuration, contract version, validation
report, and acceptance decision using the stored evidence and SPARQL queries.

## Required result tables

1. sample composition and reference-review summary;
2. Run-0/Run-1 core RDF and decision agreement;
3. Run-Var differences and attribution to the changed factor;
4. accepted/conditional/rejected distribution;
5. trace-link and competency-query success;
6. legacy versus enhanced traceability coverage.
