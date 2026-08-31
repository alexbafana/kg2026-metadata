# Controlled evaluation stages

These scripts implement the two stages needed for the controlled employment
pilot. They are public methods, not a public copy of the restricted inputs or
outputs.

`build_controlled_dataset.py` extracts normalized text from locally held PDFs,
checks source hashes against the controlled manifest, and writes a controlled
CSV plus an extraction manifest. Its output must never be committed.

`classify_employment.py` invokes an Ollama-compatible endpoint restricted to a
loopback address, verifies the installed model layer digest, validates every
response against the employment contract, checks that evidence occurs verbatim
in the controlled input, and retains raw and parsed outputs atomically under a
declared controlled root.

Example command shapes (replace every placeholder with a controlled local
path):

```bash
python3 evaluation/stages/build_controlled_dataset.py \
  --manifest <controlled>/sample-manifest.json \
  --pdf-dir <controlled>/source-inbox \
  --output <controlled>/model-input/articles.csv \
  --extraction-manifest <controlled>/model-input/extraction-manifest.json

python3 evaluation/stages/classify_employment.py \
  --dataset <controlled>/model-input/articles.csv \
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

The actual controlled commands, manifests, inputs, and output hashes are
retained with the evidence package. The public aggregate does not expose
article text, evidence excerpts, or per-item predictions.

If execution is interrupted, rerun the classifier with the same arguments plus
`--resume`. It verifies the frozen execution fingerprint and every retained
request, response, and prediction hash before skipping a completed record or
continuing an incomplete one.
