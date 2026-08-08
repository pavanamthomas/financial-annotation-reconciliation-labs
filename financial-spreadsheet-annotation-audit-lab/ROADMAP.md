# Roadmap

Annotation, file-format, and sampling claims this laboratory still does
not make (August 2026).

This repository is an analytical and educational spreadsheet-annotation
lab. It is not an audit opinion and not a file converter.

## In scope now

- Constructed grids, A1 ranges, `SUM` and two-cell `+`/`−`.
- Off-by-one adjacency, cross-foot, hidden cells, formula-vs-hardcode,
  orphan and duplicate annotations, a contra-revenue sign pattern.
- A clean workbook on which error-level checks stay quiet.

## Failures that are part of the design

- An annotation can match its claimed range and still miss an adjacent
  input (`RANGE_OFF_BY_ONE` vs `TOTAL_MISMATCH`).
- A grand-total cell can disagree with a body that itself cross-foots.

Details: `docs/failures_and_corrections.md`.

## Remaining bounds

1. No `.xlsx` parser. External files stay out of the tree.
2. No shared-formula, array, or `OFFSET`/`INDIRECT` evaluation.
3. No sampling inference about spreadsheet error rates.

## Explicitly not in scope

- Rewriting a source workbook.
- Treating a green test suite as evidence about a client file.

Close an issue only with a test, a note in `CASE_STUDY.md`, or an
explicit limitation.
