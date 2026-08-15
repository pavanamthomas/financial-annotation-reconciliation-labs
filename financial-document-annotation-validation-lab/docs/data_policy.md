# Data policy

This repository is constructed so that every illustration can be
reproduced from YAML in `cases/` and the validator. It does not ship,
download, or OCR third-party financial documents.

## What is permitted

- Constructed invoice, statement, and note-style text in YAML.
- Closed-form sums of labelled amounts.
- Cohen's kappa on a supplied count table.

## What is excluded

- EDGAR filings, vendor invoices, bank PDFs, or OCR dumps.
- Model weights and API calls to an extractor.
- A second-rater study of this corpus.

I have not dual-coded these YAML files. Do not drop an OCR dump or an EDGAR
extract into `cases/`.

## Interpretation

A quiet check on a constructed invoice is a laboratory result, not
evidence that a live extraction is correct.
