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

The public-tree inventory was also checked for source PDFs, normalized real
article datasets, raw model I/O, controlled reference labels, and per-item real
predictions. None is included in the proposed commit. The public pilot result
contains aggregate counts and cryptographic hashes only.

This technical and manual check reduces disclosure risk but is not a legal
opinion or proof of GDPR/copyright compliance. Two independent reviewers must
review the actual proposed release diff and record their decision under
[`INDEPENDENT_REVIEW.md`](../../../protocol/INDEPENDENT_REVIEW.md) before a
public release is frozen.
