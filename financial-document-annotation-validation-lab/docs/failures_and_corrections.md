# Failures and corrections

A span that is in bounds and parses as the characters on the page can
still name the wrong object.

| What was tried | How it failed | Diagnostic | Correction | Locked by | What remains unknown |
| --- | --- | --- | --- | --- | --- |
| Accept `Total $1,000.00` because the parse matches | Line items + tax = 1,080 | Independent sum of `line_item` and `tax` | `TOTAL_ARITHMETIC` and `SUBTOTAL_LABELLED_AS_TOTAL` | `tests/test_validate.py::test_flagship_schema_passes_arithmetic_fails` | Whether the printed document omitted tax on purpose |
| Store inventory as 4,200 | The next word is thousand | Scale-word window after the span | `UNIT_MISMATCH` | `tests/test_validate.py::test_unit_mismatch_thousand` | Other scale words; mixed unit notes |
| Treat overlapping tax/total slices as two facts | Exclusive labels share characters | Interval overlap | `SPAN_OVERLAP` | `tests/test_validate.py::test_overlap` | Nested amounts that are legitimately overlapping in prose |
| Treat `TOTAL_ARITHMETIC` as enough | Recoding the span to `subtotal` would hide 1000 vs 1080 | Labelled total equals labelled subtotal | Split `SUBTOTAL_LABELLED_AS_TOTAL` | `tests/test_validate.py::test_flagship_schema_passes_arithmetic_fails` | Intent of the printed total |

Process: `docs/lab_process.md`.
