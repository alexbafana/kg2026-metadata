# Executed aggregate audit — 2026-08-31

## Scope and publication review

The audit used the 162 legacy Turtle artifacts in the restricted repository at
commit `234fd2fdb94cf005345f87573b317598979617f9`. The published results below
contain counts, engine versions, and a corpus-level plaintext integrity digest
only. They contain no article text, title, entity value, per-article
classification, or per-record digest. The repository privacy triage completed
with zero findings after Git internals and dependency directories were excluded.
This is a technical disclosure review, not a legal or institutional approval.

## Commands and results

Apache Jena was downloaded from the official Apache distribution, its published
SHA-512 was verified, and Jena ran on Java 25.0.2.

```text
Apache Jena RIOT version 6.2.0
RIOT_PASS=162
RIOT_FAIL=0
```

The three retained artifact-correspondence candidates each passed
`article-overview.rq` and `traceability-minimum.rq`. Across those candidates,
entity counts were 14, 3, and 10; EMTAK counts were 9, 7, and 11. All three had
`prov:generatedAtTime`; none had `prov:wasGeneratedBy` or
`ver:hasProcessingTrajectory`. Detailed per-artifact hashes remain restricted.

The aggregate `traceability-summary.rq` audit over all 162 RDF artifacts
returned:

```text
articleCount,withTimestampCount,withActivityCount,withTrajectoryCount
162,162,0,0
```

The aggregate plaintext inventory digest, calculated over sorted `shasum -a 256`
output for the 162 restricted plaintext files, is:

```text
e98395c5a1dc51f8b7cfc99c294daaf3546899bc8d8baafa2c31fcfe4eda86c0
```

This digest identifies the audited byte set but does not establish copyright,
licensing, lawful basis, or source provenance.
