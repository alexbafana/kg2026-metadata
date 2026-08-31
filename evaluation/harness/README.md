# Evaluation harness

`run_evaluation.py` assembles per-item evidence, PROV/trajectory-linked RDF, and
acceptance decisions from a dataset and recorded stage outputs. It is fail-fast
and refuses to write into a non-empty run directory.

The public fixture adapter is deliberately not described as NLP or LLM
execution. The controlled pilot separately used the version-pinned local model
stage in `evaluation/stages/` while retaining the same evidence contract.

From the repository root:

```bash
python3 -m pip install -r evaluation/requirements-validation.txt
python3 -m unittest discover -s tests -v
```

The test suite currently contains 20 tests. Then run the public fixture into a
fresh output directory:

```bash
python3 evaluation/harness/run_evaluation.py \
  --dataset evaluation/fixtures/public/articles.csv \
  --predictions evaluation/fixtures/public/predictions.json \
  --config evaluation/fixtures/public/run-0.config.json \
  --output /tmp/kg2026-fixture-run-0

python3 evaluation/harness/run_evaluation.py \
  --dataset evaluation/fixtures/public/articles.csv \
  --predictions evaluation/fixtures/public/predictions.json \
  --config evaluation/fixtures/public/run-1.config.json \
  --output /tmp/kg2026-fixture-run-1
```

Run-0 and Run-1 must use identical substantive settings. Run-Var changes only
the pre-registered confidence threshold. Use `compare_runs.py` to compare core
semantic and decision fields separately from run-specific provenance.

```bash
python3 evaluation/harness/compare_runs.py \
  /tmp/kg2026-fixture-run-0 \
  /tmp/kg2026-fixture-run-1 \
  --output /tmp/kg2026-fixture-comparison.json
```

The named directories are examples; choose fresh directories because the
harness deliberately refuses to overwrite non-empty evidence packages. For the
controlled model stage and retained empirical result, see
[`../stages/README.md`](../stages/README.md) and
[`../results/public/employment-pilot/README.md`](../results/public/employment-pilot/README.md).
