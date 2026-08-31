# Security, privacy, and rights boundary

This repository is public metadata only. A public release requires a documented
source-by-source assessment of copyright/licensing, confidentiality, and data
protection. Public availability of a source does not by itself authorise
redistribution of its text or derived copies.

Never commit source texts, RDF `bodyText` values, token-level annotations,
named-entity outputs, model indexes, API keys, passwords, access links, or
unreviewed evidence logs. The `.gitignore` file blocks common restricted paths;
it is not a substitute for human review.

The owner must retain a rights inventory identifying source URL, retrieval date,
rights holder, lawful basis, licence/permission, release decision, and reviewer.
If a rights holder or data controller does not approve public release, store the
item only in the controlled-access package and publish no more than approved
metadata.

Run [`evaluation/scripts/privacy_scan.py`](evaluation/scripts/privacy_scan.py)
as a triage aid before release. The executed public-diff record is in
[`evaluation/results/public/employment-pilot/PRIVACY_REVIEW.md`](evaluation/results/public/employment-pilot/PRIVACY_REVIEW.md).
The scanner cannot establish legal compliance or identify all personal data;
the independent release review in
[`evaluation/protocol/INDEPENDENT_REVIEW.md`](evaluation/protocol/INDEPENDENT_REVIEW.md)
remains required.
