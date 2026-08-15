# Roadmap

Extraction, OCR, and sampling claims this laboratory still does not make
(August 2026).

## In scope now

- Constructed YAML documents, span schema, parse agreement, invoice
  arithmetic, one scale-word check, exact-match rater disagreement,
  kappa arithmetic on a supplied table.

## Remaining bounds

1. No PDF or OCR pipeline.
2. No token-level IOB tagging.
3. No sampling inference about extractor error rates.

## Explicitly not in scope

- A production labelling tool.
- Treating a green test suite as evidence about a live document set.

Close an issue only with a test, a note in `CASE_STUDY.md`, or an
explicit limitation.
