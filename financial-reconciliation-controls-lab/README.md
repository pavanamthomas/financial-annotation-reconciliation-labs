# financial-reconciliation-controls-lab

Dr. Pavanam Thomas · [pavanamthomas](https://github.com/pavanamthomas) · thomaspavanam@gmail.com  
Copyright 2026 · MIT License

A zero unexplained difference is not a clean reconciliation. It is a claim that every difference between bank and book has been named, and that those names are valid.

I keep constructed cash recs and three-way matches here so I can check unexplained differences, stale outstanding checks, completeness and existence of lines, cutoff, classification, and PO/receipt/invoice quantities and amounts. The ledgers are Python objects. They are not a bank file, not a GL extract, and not a client working paper.

Open work is `ROADMAP.md`. Failures I keep on purpose are `docs/failures_and_corrections.md`. The flagship argument is `CASE_STUDY.md`.

## What is checked

| Code | Assertion | Claim under test |
| --- | --- | --- |
| `UNEXPLAINED_DIFFERENCE` | accuracy | Adjusted bank ≠ adjusted book |
| `DOUBLE_COUNT_CLEARED_ITEM` | existence | Outstanding check ref already appears as a cleared bank line |
| `ZERO_UNEXPLAINED_IS_NOT_CLEAN` | accuracy | The rec ties only after such a stale item |
| `COMPLETENESS_GAP` | completeness | Bank line not on books and not a reconciling item |
| `EXISTENCE_ORPHAN` | existence | Book line not on the bank statement and not a reconciling item |
| `CUTOFF_BREAK` | cutoff | Line date is outside the recon period while tagged to that period |
| `CLASSIFICATION_MISPOST` | classification | Cash rec contains a book line not coded to cash |
| `THREE_WAY_QTY_MISMATCH` | accuracy | PO, receipt, and invoice quantities disagree beyond tolerance |
| `THREE_WAY_AMOUNT_TOLERANCE` | accuracy | Invoice amount differs from PO amount beyond tolerance |

Adjusted bank is `bank_balance` plus bank-side reconciling items. Adjusted book is `book_balance` plus book-side items. The clean rec is part of the design: an outstanding check that is not on the bank statement, with a zero unexplained difference and no error-level findings.

## Flagship

Open `CASE_STUDY.md` and `src/frclab/ledgers.py::flagship_stale_outstanding`.

Bank ending 9,700 already includes cleared check 1001 for 300. Books never recorded it (GL 10,000). The worksheet adds 300 back on the bank side as an “outstanding check”. Adjusted bank 10,000 equals books. Unexplained difference 0.

The auditor reports `DOUBLE_COUNT_CLEARED_ITEM` and `ZERO_UNEXPLAINED_IS_NOT_CLEAN`. It does not report `UNEXPLAINED_DIFFERENCE`.

A tie-out is not evidence that the reconciling items are true.

## Install and run

Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
python scripts/run_all.py
```

Dependencies: `numpy`, `pandas`, `pytest`. There is no bank-file parser.

## Layout

```
src/frclab/        models, ledgers, controls
scripts/run_all.py
tests/
CASE_STUDY.md
docs/three_way.md
docs/failures_and_corrections.md
docs/data_policy.md
docs/lab_process.md
```

## What this is not

Not a bank-rec product, a SOX tester, or an audit opinion. Not a sampling result about how often stale outstanding checks occur. Passing CI means the laboratory still recovers the planted breaks and still stays quiet on the clean rec.

## Author

Dr. Pavanam Thomas  
GitHub: [pavanamthomas](https://github.com/pavanamthomas)  
Email: thomaspavanam@gmail.com

See `CITATION.cff`. MIT License; copyright 2026 Dr. Pavanam Thomas, `LICENSE`.
