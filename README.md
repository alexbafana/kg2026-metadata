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

It does not provide open-data replication. The full evidence package is held
outside GitHub under the process in [DATA_ACCESS.md](DATA_ACCESS.md).

## Repository structure

| Path | Purpose |
| --- | --- |
| `pipeline/` | Legacy pipeline source retained for methodological review. |
| `metadata/` | Empty, schema-led public manifest templates; add only approved metadata. |
| `evaluation/` | Validation/query helpers and Section VI evidence protocol. |
| `DATA_ACCESS.md` | Controlled-access and reviewer procedure. |
| `REPRODUCIBILITY.md` | Executed/pending boundary and reproducibility limitations. |
| `SECURITY.md` | Publication boundary and release checks. |

## Section VI claim boundary

Evidence is **demonstrated** only where the actual reviewed artifact and a
successful execution record are available. This repository currently supplies
the protocol, tooling, and a reviewed aggregate RDF syntax/query audit. It does
not claim a completed Run-0/Run-1/Run-Var evaluation.

## Controlled execution

The scripts require approved source data and assets that are deliberately not
in this repository. In a controlled environment, install
`pipeline/requirements.txt`, supply the approved assets, set `OPENAI_API_KEY`
only in the environment, and record exact versions, command line, input/output
hashes, and validation results. See [DATA_ACCESS.md](DATA_ACCESS.md).

Before adding public metadata, validate each row against
[`metadata/article-manifest-schema.json`](metadata/article-manifest-schema.json)
and complete the rights review described in [SECURITY.md](SECURITY.md).
