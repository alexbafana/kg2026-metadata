# KG 2026 Metadata

This is the public metadata and reproducibility companion for the Section VI
evaluation of a trajectory-aware NLP-to-RDF pipeline. It has a fresh Git
history and intentionally contains **no news article body text, per-article
derived output, model index, credential, or run evidence that could disclose
restricted source material**.

## What this repository supports

- review of the pipeline implementation and evaluation protocol;
- inspection of non-sensitive metadata, manifests, hashes, and aggregate
  results after they are reviewed for publication; and
- controlled re-execution by authorised reviewers who have approved access to
  the source corpus and model assets.
- public execution of a synthetic contract/trajectory/acceptance smoke test.

It does not provide open-data replication. The full evidence package is held
outside GitHub under the process in [DATA_ACCESS.md](DATA_ACCESS.md).

## Repository structure

| Path | Purpose |
| --- | --- |
| `pipeline/` | Legacy pipeline source retained as baseline material; not the Section VI executor. |
| `metadata/` | Empty, schema-led public manifest templates; add only approved metadata. |
| `evaluation/protocol/` | Normative claim-to-evidence matrix and fixed experimental design. |
| `evaluation/contracts/v1/` | Versioned transformation and acceptance contract. |
| `evaluation/harness/` | Evidence, provenance, trajectory, RDF, acceptance, and comparison tools. |
| `evaluation/fixtures/public/` | Author-created exercisability cases. |
| `evaluation/results/public/` | Synthetic results and reviewed real aggregates only. |
| `DATA_ACCESS.md` | Controlled-access and reviewer procedure. |
| `REPRODUCIBILITY.md` | Executed/pending boundary and reproducibility limitations. |
| `SECURITY.md` | Publication boundary and release checks. |

## Section VI claim boundary

Evidence is **demonstrated** only where an artifact exists and the corresponding
command completed successfully. This repository supplies the claim-aligned
protocol, versioned contract, executable fixture workflow, reviewed aggregate
legacy RDF audit, and a reviewer-safe aggregate from an executed controlled
employment-stage Run-0/Run-1/Run-Var pilot. Reference-based agreement remains
provisional until two independent reviewers complete the recorded protocol.

## Five-minute public check

```bash
python3 evaluation/harness/run_evaluation.py \
  --dataset evaluation/fixtures/public/articles.csv \
  --predictions evaluation/fixtures/public/predictions.json \
  --config evaluation/fixtures/public/run-0.config.json \
  --output /tmp/kg2026-fixture-run-0
```

The author-created fixture is a smoke test, not evidence about real news or
model accuracy.

## Controlled execution

The controlled experiment uses a frozen 12-item employment sample and a
digest-pinned local employment classifier. Restricted inputs, raw model I/O,
per-item predictions, and exact evidence remain outside GitHub. See
[DATA_ACCESS.md](DATA_ACCESS.md).

Before adding public metadata, validate each row against
[`metadata/article-manifest-schema.json`](metadata/article-manifest-schema.json)
and complete the rights review described in [SECURITY.md](SECURITY.md).
