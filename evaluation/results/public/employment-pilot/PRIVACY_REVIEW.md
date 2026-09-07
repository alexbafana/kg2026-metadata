# Public-diff privacy review

The repository privacy scanner was run over the proposed public tree on
2026-08-31. The initial scan reported three candidate phone-number findings.
Manual inspection classified all three as false positives:

1. the published macro-F1 decimal in `aggregate-summary.json`;
2. the loopback Ollama URL `127.0.0.1:11434`; and
3. the classifier's loopback host allow-list.

The scanner was then hardened to distinguish decimal and loopback machine
numbers from phone candidates, with regression tests for both false positives
and a synthetic true-positive pattern. The final proposed-tree scan reported
zero candidates.

The 2026-08-31 scan predated written permission to publish the 12 source PDFs.
Those exact captures are now included under
`evaluation/data/employment-sample-v1/` with a source manifest and checksum for
each file. Normalized datasets, raw model I/O, controlled reference labels, and
unreviewed per-item predictions remain excluded. The public pilot result still
contains aggregate counts and cryptographic hashes only.

The scanner was rerun on 2026-09-07 after adding the authorized source package.
It reported 22 review candidates in the new README and manifest. Manual review
confirmed that all were false positives caused by public ERR record IDs, PDF
filenames, byte counts, and hexadecimal SHA-256 values; none was a telephone
number or Estonian personal identification code. The scanner does not extract
or assess PDF contents, so the published captures and the complete release diff
still require the independent manual review prescribed below.

This technical and manual check reduces disclosure risk but is not a legal
opinion or proof of GDPR/copyright compliance. Two independent reviewers must
review the actual proposed release diff and record their decision under
[`INDEPENDENT_REVIEW.md`](../../../protocol/INDEPENDENT_REVIEW.md) before a
public release is frozen.
