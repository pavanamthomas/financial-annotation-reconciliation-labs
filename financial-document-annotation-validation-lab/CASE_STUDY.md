# Case study: a total span that is the subtotal

Case `INV-FLAGSHIP-SUBTOTAL-AS-TOTAL`.

```
Widgets $400.00
Gaskets $600.00
Subtotal $1,000.00
Tax $80.00
Total $1,000.00
```

Candidate annotation `A-TOT` covers `$1,000.00` on the Total line, label `total`, `parsed_value` 1000. The slice is in bounds. The parse matches the characters.

## What holds

Schema. Parse. Exclusive labels `subtotal`, `tax`, and `total` do not overlap.

## What does not hold

Line items 400 + 600 = 1,000. Plus tax 80 = 1,080. The labelled total is 1,000. That equals the labelled subtotal.

The auditor reports `TOTAL_ARITHMETIC` (`expected=1080`, `labelled_total=1000`) and `SUBTOTAL_LABELLED_AS_TOTAL`. Constructed rater B labels the same slice `subtotal`, so `RATER_DISAGREEMENT` is also on the page. That rater disagreement is a constructed fixture, not a kappa study.

## What cannot be concluded

That the vendor intended 1,080. The document as printed may be wrong, or tax may be included elsewhere. The laboratory knows labelled amounts and arithmetic. It does not know the contract.

The same checks on `INV-CLEAN-TIE` stay at zero errors (100 + 50 + 12 = 162).

Locked by `tests/test_validate.py::test_flagship_schema_passes_arithmetic_fails` and `test_clean_invoice_has_no_error_findings`.
