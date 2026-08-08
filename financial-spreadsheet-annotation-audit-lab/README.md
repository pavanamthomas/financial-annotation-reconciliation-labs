# financial-spreadsheet-annotation-audit-lab

Dr. Pavanam Thomas · [pavanamthomas](https://github.com/pavanamthomas) · thomaspavanam@gmail.com  
Copyright 2026 · MIT License

An annotation is not an audit. It is a claim about a cell, a range, and a number. I keep constructed grids here so I can check whether that claim is internally consistent, and whether consistency with the claimed range is being mistaken for a complete total.

The workbooks are Python objects. They are not Excel files, not a reporting pack, and not a live general ledger. Recalculation covers `SUM` of an A1 range and a two-cell `+`/`−`. Unsupported formulae are a coverage limit (`docs/data_policy.md`).

Open work is `ROADMAP.md`. Failures I keep on purpose are `docs/failures_and_corrections.md`. The flagship argument is `CASE_STUDY.md`.

## What is checked

| Code | Claim under test |
| --- | --- |
| `RANGE_OFF_BY_ONE` | An adjacent numeric input sits outside a total range that still sums to the annotated number |
| `RANGE_INCLUDES_SUBTOTAL` | A total range includes a cell marked as a total or subtotal |
| `TOTAL_MISMATCH` | Claimed value, cell value, and reconstructed range sum disagree |
| `CROSS_FOOT_FAILURE` | Grand total does not equal the body sum (or row vs column body sums disagree) |
| `FORMULA_CLAIM_ON_HARDCODE` | Annotation says formula; the cell has no formula |
| `HIDDEN_INSIDE_TOTAL` | A hidden cell is inside the claimed range |
| `DUPLICATE_ANNOTATION` | Two annotations on one cell |
| `ANNOTATION_ORPHAN` | Annotation points at a cell that is not on the sheet |
| `SIGN_CONVENTION` | A contra-revenue line is stored positive and added into net |
| `STALE_CLAIMED_VALUE` | Cached value or annotation does not match a recomputed formula |
| `UNAUDITED_MATERIAL` | An input above a documented threshold has no annotation |

The clean workbook is part of the design: the same checks stay quiet when the range is complete and the numbers tie.

Identities with a known numerical check are tested. That is all the tests claim.

## Flagship

Open `CASE_STUDY.md` and `src/fsaslab/workbooks.py::flagship_off_by_one`.

Product rows B2:B4 sum to 900. Product D in B5 is 50 and sits next to the range. The total cell and the annotation both say 900 = `SUM(B2:B4)`. Reconstructing the annotated range recovers 900. The auditor reports `RANGE_OFF_BY_ONE`, not `TOTAL_MISMATCH`.

A tick mark on a total that matches its own range is not evidence that the range is the economic total.

## Install and run

Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
python scripts/run_all.py
```

Dependencies: `numpy`, `pandas`, `pytest`. There is no spreadsheet file parser and no market-data client.

`scripts/run_all.py` writes finding tables under `outputs/tables/`. Those CSVs are output, not source data.

## Layout

```
src/fsaslab/        addresses, formulae, workbooks, checks, report
scripts/run_all.py  audits every constructed workbook
tests/              planted-defect recovery and the clean tie-out
CASE_STUDY.md
docs/failures_and_corrections.md
docs/data_policy.md
docs/lab_process.md
```

## What this is not

Not an Excel add-in, a formula engine, or a substitute for tracing to source documents. Not a statement about how often off-by-one totals occur in practice. Passing CI means the laboratory still recovers the planted defects and still stays quiet on the clean grid.

## Author

Dr. Pavanam Thomas  
GitHub: [pavanamthomas](https://github.com/pavanamthomas)  
Email: thomaspavanam@gmail.com

See `CITATION.cff`. MIT License; copyright 2026 Dr. Pavanam Thomas, `LICENSE`.
