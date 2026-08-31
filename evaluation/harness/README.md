# Evaluation harness

`run_evaluation.py` assembles per-item evidence, PROV/trajectory-linked RDF, and
acceptance decisions from a dataset and recorded stage outputs. It is fail-fast
and refuses to write into a non-empty run directory.

The public fixture adapter is deliberately not described as NLP or LLM
execution. The controlled pilot separately used the version-pinned local model
stage in `evaluation/stages/` while retaining the same evidence contract.

From the repository root:

```bash
python3 evaluation/harness/run_evaluation.py \
  --dataset evaluation/fixtures/public/articles.csv \
  --predictions evaluation/fixtures/public/predictions.json \
  --config evaluation/fixtures/public/run-0.config.json \
  --output /tmp/kg2026-fixture-run-0
```

Run-0 and Run-1 must use identical substantive settings. Run-Var changes only
the pre-registered confidence threshold. Use `compare_runs.py` to compare core
semantic and decision fields separately from run-specific provenance.
