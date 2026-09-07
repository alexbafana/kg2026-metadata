# Evaluation dataset card

## Public employment sample

The pilot uses 12 frozen Estonian articles selected before model execution to
cover apparent gain, loss, no-event, and difficult or ambiguous cases. The
exact PDFs, source inventory, source URLs, and checksums are public under
[`data/employment-sample-v1/`](data/employment-sample-v1/) with written ERR
permission. The normalized input can be reconstructed from these files. Two
independent reviews and adjudication are still required before the
reference-based metrics become final.

## Current restricted legacy corpus

The current 162-item corpus covers only 2019-11-06 through 2019-11-08. A
read-only keyword audit found very few plausible employment-gain/loss cases.
It is therefore a valid legacy RDF baseline but is not, by itself, a credible
balanced employment-event evaluation sample.

The published 12-article challenge sample addresses the legacy corpus imbalance
for a bounded pilot, but it is purposively selected and does not support
prevalence estimates or population-level accuracy claims. The separate
162-item legacy corpus remains restricted.

## Public fixtures

`fixtures/public/articles.csv` contains three short author-created examples.
They exist solely to test repository exercisability, all acceptance branches,
RDF generation, provenance/trajectory links, SHACL, and SPARQL queries.

## Reference review

Reference labels are independent oracle data and must never be passed to the
employment classifier. Two researchers should record event type, organization,
job count, evidence span, expected disposition, reviewer IDs, and resolution of
any disagreement.

Use the [`independent-review protocol`](protocol/INDEPENDENT_REVIEW.md) for the
item-level decisions. The current disclosure-screened
[`public aggregate`](results/public/employment-pilot/aggregate-summary.json)
remains provisional until that process is complete.
