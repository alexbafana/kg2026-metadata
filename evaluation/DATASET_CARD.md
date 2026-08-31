# Evaluation dataset card

## Required real sample

Section VI requires a frozen, controlled set of 10–12 Estonian articles with
reviewed employment-event references. The target composition should include at
least two job-gain, two job-loss, two ambiguous, and several no-event cases,
subject to what the sources actually support. Selection and exclusions must be
reported without silently balancing after viewing model results.

## Current restricted legacy corpus

The current 162-item corpus covers only 2019-11-06 through 2019-11-08. A
read-only keyword audit found very few plausible employment-gain/loss cases.
It is therefore a valid legacy RDF baseline but is not, by itself, a credible
balanced employment-event evaluation sample.

No article text is published here. Before real execution, the research team
must either enrich the controlled sample with suitable rights-reviewed sources
or report the severe class imbalance and narrow the empirical claim.

## Public fixtures

`fixtures/public/articles.csv` contains three short author-created examples.
They exist solely to test repository exercisability, all acceptance branches,
RDF generation, provenance/trajectory links, SHACL, and SPARQL queries.

## Reference review

Reference labels are independent oracle data and must never be passed to the
employment classifier. Two researchers should record event type, organization,
job count, evidence span, expected disposition, reviewer IDs, and resolution of
any disagreement.
