# Independent evidence review protocol

## Purpose and status rule

This protocol defines the independent checks required before evidence from this
repository is described in Section VI of the paper. The authors who generate
the sample, model outputs, run packages, comparisons, or metrics must not be the
only reviewers of those artifacts.

Two independent reviewers should each record an explicit decision for every
assigned check. Silence, receipt of a link, repository access, or absence of a
reported problem is **not validation**. Until the applicable decisions are
recorded, the corresponding evidence remains pending.

## Materials supplied to each reviewer

Replace the placeholders below when the evidence package is frozen.

- Repository commit: `<COMMIT_SHA>`
- Fixed release/tag: `<RELEASE_TAG_OR_PENDING>`
- Public repository URL: `<PUBLIC_REPOSITORY_URL>`
- Public source sample: `evaluation/data/employment-sample-v1/`
- Controlled run-evidence location: `<CONTROLLED_ACCESS_LOCATION>`
- Sample manifest and hashes: `<SAMPLE_MANIFEST_PATH_OR_ID>`
- Reference-label file: `<REFERENCE_LABEL_PATH_OR_ID>`
- Run-0 manifest: `<RUN_0_MANIFEST_PATH_OR_ID>`
- Run-1 manifest: `<RUN_1_MANIFEST_PATH_OR_ID>`
- Run-Var manifest: `<RUN_VAR_MANIFEST_PATH_OR_ID>`
- Aggregate results: `<RESULTS_PATH_OR_PENDING>`

Reviewers must use the same frozen commit and controlled evidence version. If a
review changes an artifact, freeze a new version and repeat every affected
check; do not silently amend reviewed evidence.

## A. Review of the 12-article reference sample

Review each article directly from the frozen public sample, without relying on
the generated prediction. For every item, independently record:

1. whether the source identity, title, publisher, URL, publication date, file
   hash, and opaque sample ID match the manifest;
2. the reference class: `job_gain`, `job_loss`, `no_event`, or `ambiguous`;
3. the employing organization, when supported by the text;
4. the job count, distinguishing people, positions, approximate counts,
   multiple counts, and absent counts;
5. whether the event is actual, announced, planned, forecast, aggregate, or
   explicitly negated;
6. the minimal source evidence supporting the label, recorded in the review
   material;
7. whether the item should be retained, relabelled, or excluded; and
8. any disagreement with the preliminary author-created reference label.

Do not infer that a headline alone establishes the reference label. Resolve
disagreements through a documented adjudication entry that preserves both
original reviews, the final label, the adjudicator, date, and rationale.

Required completion evidence:

- 12 item-level decisions from reviewer A;
- 12 item-level decisions from reviewer B;
- a disagreement/adjudication log, including an explicit `none` when there are
  no disagreements; and
- a signed or attributable final reference-label version with its content hash.

## B. Employment-classification stage

Confirm that the employment stage is an executed model stage rather than a
fixture containing recorded author-created predictions. Check:

- model/provider and exact model version or immutable deployment identifier;
- prompt/template version and hash;
- decoding parameters, seed where supported, and confidence threshold;
- input sample version and hash;
- executable command and software/environment versions;
- raw response retention in controlled access;
- parsing and schema-validation status for every item;
- failure, retry, and manual-intervention records; and
- output and manifest hashes.

The reviewer must be able to connect every reported prediction to an actual
recorded invocation. An undocumented manual prediction is not model execution.
Run-Var is not a third model invocation: it must trace to the frozen Run-0
prediction artifact and demonstrate that only the declared acceptance policy
was reapplied.

## C. Run-package integrity

Review Run-0, Run-1, and Run-Var separately. For each package, verify that:

- all 12 frozen inputs have one terminal item status;
- the run manifest identifies inputs, code commit, contract, model, prompt,
  configuration, environment, timestamps, and generated artifacts;
- failures and retries are visible and no item disappeared silently;
- provenance and trajectory records link each output to its inputs and ordered
  processing steps;
- RDF and validation reports exist and agree with the manifest; and
- package hashes recompute successfully.

For Run-0 versus Run-1, confirm that substantive configurations are identical
and assess agreement only on canonical semantic outputs and acceptance
decisions. Run IDs, timestamps, and run-specific provenance hashes are expected
to differ.

For Run-Var, confirm that exactly the declared factor changed and that reported
output differences are attributable to it. Record any undeclared difference as
a protocol deviation.

## D. Metrics and claims

Recompute the reported metrics from the frozen reference labels and retained
predictions. At minimum check:

- sample composition by reference class and modality;
- event-class agreement and its numerator/denominator;
- item-level qualitative organization review and explicit-count agreement,
  with eligibility rules stated (organization agreement is not currently
  reported as a numerical metric);
- Run-0/Run-1 semantic and acceptance-decision agreement;
- Run-Var changed-item count and attribution;
- accepted/conditional/rejected outcome distribution;
- trace-link completeness and competency-query success; and
- legacy-versus-enhanced traceability coverage.

Because the sample has only 12 purposively selected articles, report counts and
item-level outcomes. Do not generalize these results into NLP/EMTAK population
accuracy, state-of-the-art performance, or statistical representativeness.
Every Section VI claim must remain within the boundary in
`CLAIM_EVIDENCE_MATRIX.md`.

## E. Privacy, rights, and public-release boundary

Review the proposed public diff and release contents, not merely the source
working directory. The 12 PDFs under `evaluation/data/employment-sample-v1/`
are an approved exception supported by retained written ERR permission. Confirm
that the public repository contains no:

- other article body text, screenshots, PDFs, or reconstructable excerpts
  outside that approved sample;
- personal data copied from the restricted sources;
- API keys, credentials, private endpoints, or access tokens;
- raw model responses that reproduce source content;
- controlled file paths or access details that disclose restricted material;
- unreviewed item-level real-source results; or
- claim that source texts are licensed for redistribution unless documented
  rights evidence supports it.

The public package may contain the approved 12 PDFs, reviewed non-sensitive
aggregates, opaque IDs, content hashes, protocols, schemas, and code. Unreviewed
item-level labels and run evidence remain in controlled review material.
Hash publication establishes identity, not redistribution rights or anonymity.

Record the privacy/rights scan command and result, manual review scope, reviewer,
date, exceptions, and disposition. Any exception must be resolved before public
release.

## F. Reviewer decision and sign-off

Each reviewer must return one decision for each area A–E:

- `accepted` — checked and supported by the inspected evidence;
- `accepted_with_corrections` — usable only after listed corrections are made
  and rechecked; or
- `not_accepted` — insufficient, inconsistent, or outside the claim boundary.

Use this record:

```text
Reviewer:
Reviewed commit:
Controlled evidence version/hash:
Area A — reference sample:
Area B — model stage:
Area C — Run-0/Run-1/Run-Var:
Area D — metrics and claims:
Area E — privacy/rights boundary:
Required corrections or limitations:
Date:
Signature or attributable approval:
```

Final evidence may be marked independently reviewed only after both reviews,
all required corrections, and affected rechecks are retained. Reviewer
agreement does not by itself demonstrate legal permission, independent external
replication, or broader classifier accuracy.
