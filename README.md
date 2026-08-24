# fin-check

Dr. Pavanam Thomas · [pavanamthomas](https://github.com/pavanamthomas) · thomaspavanam@gmail.com  
Copyright 2026 · MIT License

I put three small laboratories in one tree because they fail the same way: a number that ties is treated as a finished check.

| Lab | What I actually test |
| --- | --- |
| [`financial-spreadsheet-annotation-audit-lab`](financial-spreadsheet-annotation-audit-lab/) | A total annotated as `SUM(B2:B4)` while B5 is still a product row |
| [`financial-document-annotation-validation-lab`](financial-document-annotation-validation-lab/) | An invoice span labelled `total` that is the pre-tax subtotal |
| [`financial-reconciliation-controls-lab`](financial-reconciliation-controls-lab/) | A cash rec that ties by adding back a check already on the bank statement |

Each folder is its own package. Grids, invoices, and ledgers are written in the repo. I do not ship client files.

```bash
cd financial-spreadsheet-annotation-audit-lab
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
pytest -q
python scripts/run_all.py
```

Same four commands in the other two directories. Root CI runs all three.

```bash
origin repo clone pavanam-thomas/fin-check
```

A green badge is not an audit opinion. The interesting cases are in each `CASE_STUDY.md` and `docs/failures_and_corrections.md`.
