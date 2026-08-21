# Data policy

This repository is constructed so that every numerical illustration can
be reproduced from the source code. It does not ship, download, or parse
third-party bank files or general-ledger extracts.

## What is permitted

- Python `Reconciliation` objects in `src/frclab/ledgers.py`.
- Closed-form adjusted-bank and three-way amount identities.

## What is excluded

- BAI2, CAMT, OFX, or vendor bank statements.
- ERP extracts and undocumented CSV dumps of live books.

Functions will take a DataFrame you build elsewhere. Do not commit a
bank file or a GL extract.

## Interpretation

A quiet check on a constructed rec is a laboratory result, not evidence
that a live cash rec is clean.
