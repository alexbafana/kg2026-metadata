# Supplementary controlled trace validation (2026-09-18)

These checks were performed after the original controlled audit. They are
reported separately rather than retroactively described as predeclared
walkthroughs. The exact 12 source PDFs and manifest are public with written
ERR permission. The generated RDF and per-item query results remain controlled.

## Inputs and tools

- Git revision at execution: `e8e0d4630405e837b01f78ea1ee098aa4dbd8233`
  (before this supplementary report and query were added).
- Controlled input: 36 retained Turtle files, 12 in each of Run-0, Run-1,
  and Run-Var.
- Apache Jena SHACL 6.2.0.
- Shape file: `evaluation/contracts/v1/trace-shapes.ttl`,
  SHA-256 `ca79d938b6a94f58088c544abbc29b6ba46f26c76648597f75c6fefd93a34b2c`.
- Apache Jena ARQ 6.2.0.
- Query: `evaluation/queries/statement-trace-with-modes.rq`.

## Results

| Check | Result |
| --- | --- |
| Jena SHACL validation against the declared trace shapes | 36/36 conform |
| Extended statement-trace query | 36/36 execute and return ten positioned stage rows each |
| Total extended-query rows, excluding headers | 360 |

The SHACL shapes check required assertion links, confidence bounds, ten
trajectory step links, step fields, and an allowed decision outcome. Passing
these shapes does **not** establish factual correctness of an employment claim,
semantic coherence with external vocabularies, or completeness of intermediate
artifact links. The extended query retrieves the recorded stage labels and
execution modes, including modes marked not executed; it does not turn ten
declared stages into ten executed transformations. Neither check retrieves an
explicit statement-to-JSON or text-fragment link.

The commands used were, for each retained controlled Turtle file:

```bash
shacl validate \
  --shapes evaluation/contracts/v1/trace-shapes.ttl \
  --data CONTROLLED_FILE.ttl --text

arq --data=CONTROLLED_FILE.ttl \
  --query=evaluation/queries/statement-trace-with-modes.rq \
  --results=CSV
```

Only aggregate counts are released here. The controlled RDF and per-item
outputs are withheld pending the separate evidence-access and review process.
