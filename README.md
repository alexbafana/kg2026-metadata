# KG 2026 Metadata

This is the public reproducibility companion for the Section VI evaluation of
a trajectory-aware NLP-to-RDF pipeline. It includes the exact 12 ERR article
captures used by the employment-stage pilot, published with written permission,
together with methods, contracts, manifests, and disclosure-screened aggregate results.
Credentials, model assets, and unreviewed run evidence are not included.

New readers should begin with the
[`DOCUMENTATION_INDEX.md`](DOCUMENTATION_INDEX.md) navigation guide.

## What this repository supports

- review of the pipeline implementation and evaluation protocol;
- inspection of the exact 12 source PDFs, metadata, manifests, hashes, and
  disclosure-screened aggregate results, explicitly provisional where noted;
- reconstruction of the normalized 12-item input and an attempted
  re-execution of the employment-stage evaluation by researchers with the
  declared model setup; exact model assets and item-level evidence remain
  required for independent equality checks;
- public execution of a synthetic contract/trajectory/acceptance smoke test.
- inspection of supplementary aggregate trace-shape and stage-mode checks
  against retained controlled RDF, without access to per-item outputs.

The [12-article dataset](evaluation/data/employment-sample-v1/) is directly
available in this repository. Detailed raw model I/O and unreviewed item-level
evidence remain outside GitHub under the process in [DATA_ACCESS.md](DATA_ACCESS.md).

## Repository structure

| Path | Purpose |
| --- | --- |
| `pipeline/` | Legacy pipeline source retained as baseline material; not the Section VI executor. |
| `metadata/` | Empty, schema-led public manifest templates; add only approved metadata. |
| `evaluation/protocol/` | Normative claim-to-evidence matrix and fixed experimental design. |
| `evaluation/data/employment-sample-v1/` | Exact 12 ERR article captures, manifest, source links, and checksums. |
| `evaluation/contracts/v1/` | Versioned transformation and acceptance contract. |
| `vocab/` | Repository-controlled schema and version vocabulary used by generated RDF. |
| `evaluation/harness/` | Evidence, provenance, trajectory, RDF, acceptance, and comparison tools. |
| `evaluation/stages/` | Controlled dataset preparation and local employment-classifier execution. |
| `evaluation/fixtures/public/` | Author-created exercisability cases. |
| `evaluation/results/public/` | Synthetic results and disclosure-screened real aggregates only. |
| `DOCUMENTATION_INDEX.md` | Newcomer guide, evidence map, and release checklist. |
| `DATA_ACCESS.md` | Controlled-access and reviewer procedure. |
| `REPRODUCIBILITY.md` | Executed/pending boundary and reproducibility limitations. |
| `SECURITY.md` | Publication boundary and release checks. |

## Section VI claim boundary

Evidence is **demonstrated** only where an artifact exists and the corresponding
command completed successfully. This repository supplies the claim-aligned
protocol, versioned contract, executable fixture workflow, reviewed aggregate
legacy RDF audit, and a disclosure-screened aggregate from an executed controlled
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
model accuracy. Choose a fresh output directory when rerunning because the
harness intentionally refuses to overwrite an existing non-empty directory.

## Employment-stage reproduction

The experiment uses the frozen public 12-item employment sample and a
digest-pinned local employment classifier. The source captures and manifest are
available under [`evaluation/data/employment-sample-v1/`](evaluation/data/employment-sample-v1/).
Raw model I/O and unreviewed item-level decisions remain outside GitHub; see
[DATA_ACCESS.md](DATA_ACCESS.md).

See the [controlled-stage instructions](evaluation/stages/README.md),
[public pilot summary](evaluation/results/public/employment-pilot/README.md),
and [independent-review protocol](evaluation/protocol/INDEPENDENT_REVIEW.md).

Before adding public metadata, validate each row against
[`metadata/article-manifest-schema.json`](metadata/article-manifest-schema.json)
and complete the rights review described in [SECURITY.md](SECURITY.md).
