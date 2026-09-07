# Employment evaluation stages

These scripts implement the two stages needed for the employment pilot. The
exact 12 PDF inputs and source manifest are public under
[`../data/employment-sample-v1/`](../data/employment-sample-v1/); generated raw
model I/O and unreviewed item-level outputs are not committed.

`build_controlled_dataset.py` extracts normalized text from the PDFs, checks
source hashes against the manifest, and writes a CSV plus an extraction
manifest.

`classify_employment.py` invokes an Ollama-compatible endpoint restricted to a
loopback address, verifies the installed model layer digest, validates every
response against the employment contract, checks that evidence occurs verbatim
in the controlled input, and retains raw and parsed outputs atomically under a
declared controlled root.

The first command below reconstructs the exact normalized input from the public
source package. Use a fresh local output directory:

```bash
python3 evaluation/stages/build_controlled_dataset.py \
  --manifest evaluation/data/employment-sample-v1/sample-manifest.json \
  --pdf-dir evaluation/data/employment-sample-v1/articles \
  --output /tmp/employment-sample-v1/articles.csv \
  --extraction-manifest /tmp/employment-sample-v1/extraction-manifest.json

python3 evaluation/stages/classify_employment.py \
  --dataset /tmp/employment-sample-v1/articles.csv \
  --output <controlled>/runs/run-0/predictions.json \
  --raw-dir <controlled>/runs/run-0/raw-model-io \
  --run-manifest <controlled>/runs/run-0/model-run-manifest.json \
  --run-id employment-run-0 \
  --model-manifest <controlled>/model-manifest.json \
  --controlled-root <controlled> \
  --model llama3.2 \
  --model-layer-sha256 <verified-model-layer-sha256> \
  --prompt evaluation/prompts/employment-v2.txt \
  --schema evaluation/contracts/v1/schemas/employment.schema.json
```

The executed commands, manifests, and output hashes are retained with the
evidence package. The public aggregate does not expose evidence excerpts or
per-item predictions.

If execution is interrupted, rerun the classifier with the same arguments plus
`--resume`. It verifies the frozen execution fingerprint and every retained
request, response, and prediction hash before skipping a completed record or
continuing an incomplete one.

The executed local tag was `llama3.2`; its manifest was verified against model
layer digest
`dde5aa3fc5ffc17176b5e8bdc82f587b24b2678c6c66101bf7da77af9f7ccdff`.
See the [`public aggregate`](../results/public/employment-pilot/aggregate-summary.json)
and [`independent-review protocol`](../protocol/INDEPENDENT_REVIEW.md). The
exact source inputs are public. Raw invocation records and unreviewed item-level
outputs remain controlled.
