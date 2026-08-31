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

The executed controlled pilot covers the employment-classification and
downstream evidence/RDF/acceptance stages only. It does not represent a rerun of
the historical upstream NLP, NER, or EMTAK stages.

## Directory map

| Path | Role |
| --- | --- |
| [`protocol/`](protocol/) | Fixed design, claim matrix, metrics, run definitions, and independent review |
| `contracts/v1/` | Versioned input/output schemas and acceptance policy |
| `fixtures/public/` | Author-created synthetic smoke-test cases; never empirical paper evidence |
| [`harness/`](harness/) | Executable evidence assembly, provenance, trajectory, validation, and comparison tools |
| `queries/` | SPARQL competency and audit queries |
| `baseline/` | Legacy corpus-level audit and limitations |
| [`results/public/`](results/public/) | Synthetic results and disclosure-screened aggregates |
| [`stages/`](stages/) | Controlled dataset preparation and local employment-classifier execution |
| `scripts/` | Supporting validation and privacy utilities |

`evaluation/runs/` is an ignored conventional path for local controlled work;
the current authoritative pilot evidence is retained outside this public Git
tree. Run-0, Run-1, and Run-Var count as demonstrated only because their
complete controlled packages and successful command records exist.

## Status boundary

The legacy RIOT/SPARQL audit is executed baseline evidence. The public fixture
workflow remains an exercisability test. A controlled 12-item employment-stage
pilot has now also executed; only its disclosure-screened aggregate is public, and its
reference-based metrics remain provisional pending independent review. Current
demonstrated and pending claims are listed in [`evidence-status.json`](evidence-status.json).
New reviewers should follow [`protocol/INDEPENDENT_REVIEW.md`](protocol/INDEPENDENT_REVIEW.md)
and start with the [`public pilot summary`](results/public/employment-pilot/README.md).
