# financial-document-annotation-validation-lab

Dr. Pavanam Thomas · [pavanamthomas](https://github.com/pavanamthomas) · thomaspavanam@gmail.com  
Copyright 2026 · MIT License

Passing schema is not a validated extraction. A span can be in bounds, parse as the number on the page, and still name the wrong economic object.

I keep constructed invoices, a statement extract, and one note-style sentence here so I can check span bounds, parse agreement, exclusive-label overlap, invoice arithmetic, a scale word after a face number, and exact-match disagreement between two constructed raters. The documents are YAML. They are not EDGAR filings, vendor OCR, or a production labelling project.

Cohen's kappa is checked on known count tables as arithmetic (`docs/label_authorship.md`). It is not double-coding of this corpus. One author wrote the YAML.

Open work is `ROADMAP.md`. Failures I keep on purpose are `docs/failures_and_corrections.md`. The flagship argument is `CASE_STUDY.md`.

## What is checked

| Code | Claim under test |
| --- | --- |
| `SCHEMA_SPAN_BOUNDS` | `start`/`end` is a valid slice of `text` |
| `PARSE_MISMATCH` | Numeric span text disagrees with `parsed_value` |
| `DATE_UNPARSEABLE` | Date `parsed_value` is not `YYYY-MM-DD` |
| `SPAN_OVERLAP` | Exclusive labels (`total`, `subtotal`, `tax`) share a slice |
| `TOTAL_ARITHMETIC` | Labelled total ≠ line items + tax |
| `SUBTOTAL_LABELLED_AS_TOTAL` | Labelled total equals the subtotal, not line items plus tax |
| `UNIT_MISMATCH` | Face number followed by “thousand”/“million”, `parsed_value` unscaled |
| `CURRENCY_INCONSISTENT` | Currency span disagrees with the document field |
| `RATER_DISAGREEMENT` | Constructed rater B does not exactly match rater A |

The clean invoice is part of the design: the same checks stay quiet when line items plus tax equal the labelled total.

## Flagship

Open `CASE_STUDY.md` and `cases/invoices/INV-FLAGSHIP-SUBTOTAL-AS-TOTAL.yaml`.

Widgets 400 + gaskets 600 = 1,000. Tax 80. Economic total 1,080. The page prints `Total $1,000.00`. Candidate spans are in bounds and parse. The auditor reports `TOTAL_ARITHMETIC` and `SUBTOTAL_LABELLED_AS_TOTAL`.

A valid offset is not a validated total.

## Install and run

Python 3.11 or newer.

```bash
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -e ".[dev]"
pytest -q
python scripts/run_all.py
```

Dependencies: `numpy`, `pandas`, `pyyaml`, `pytest`. There is no OCR client and no EDGAR downloader.

## Layout

```
cases/invoices/ statements/ extracts/
src/fdavlab/     models, loader, checks
scripts/run_all.py
tests/
CASE_STUDY.md
docs/label_authorship.md
docs/failures_and_corrections.md
```

## What this is not

Not a labelling tool, a model, or an inter-annotator study. Not a claim about extraction error rates on live documents. Passing CI means the laboratory still recovers the planted misses and still stays quiet on the clean invoice.

## Author

Dr. Pavanam Thomas  
GitHub: [pavanamthomas](https://github.com/pavanamthomas)  
Email: thomaspavanam@gmail.com

See `CITATION.cff`. MIT License; copyright 2026 Dr. Pavanam Thomas, `LICENSE`.
