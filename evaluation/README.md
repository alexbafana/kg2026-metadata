# Section VI evaluation package

This directory is organized around the claims made in Section VI of the paper,
not around the accidental contents of the legacy repository.

## Evaluation object

The object under evaluation is a trajectory-aware, contract-governed
NLP-to-RDF pipeline instantiated by the employment-event running case. The
evaluation must test:

1. ordered and branch-aware trajectory metadata;
2. repeatable execution and explainable controlled variation;
3. a versioned transformation contract and transparent acceptance decisions;
4. statement-level tracing from RDF to source evidence, processing steps,
   model/configuration, contract, and decision; and
5. compatibility with RDF, SPARQL, and PROV-O conventions.

See [`protocol/CLAIM_EVIDENCE_MATRIX.md`](protocol/CLAIM_EVIDENCE_MATRIX.md)
for the normative claim-to-evidence mapping.

## Directory map

| Path | Role |
| --- | --- |
| `protocol/` | Fixed evaluation design, selection rules, claims, metrics, and run definitions |
| `contracts/v1/` | Versioned input/output schemas and acceptance policy |
| `fixtures/public/` | Author-created synthetic smoke-test cases; never empirical paper evidence |
| `harness/` | Executable evidence assembly, provenance, trajectory, validation, and comparison tools |
| `queries/` | SPARQL competency and audit queries |
| `baseline/` | Legacy corpus-level audit and limitations |
| `results/public/` | Reviewed aggregate results only |
| `stages/` | Controlled dataset preparation and local employment-classifier adapters |
| `scripts/` | Supporting validation and privacy utilities |

Run-specific real evidence belongs in `evaluation/runs/`, which is ignored by
Git and must remain controlled. Run-0, Run-1, and Run-Var are demonstrated only
after their complete output directories exist and their commands succeed.

## Status boundary

The legacy RIOT/SPARQL audit is executed baseline evidence. The public fixture
workflow remains an exercisability test. A controlled 12-item employment-stage
pilot has now also executed; only its reviewer-safe aggregate is public, and its
reference-based metrics remain provisional pending independent review. Current
demonstrated and pending claims are listed in [`evidence-status.json`](evidence-status.json).
