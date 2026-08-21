# Case study: a rec that ties on a cleared check

Workbook `rec-flagship-stale-check`.

| Object | Amount |
| --- | --- |
| Bank ending balance | 9,700 |
| Cleared bank line, check 1001 | −300 (already in the 9,700) |
| Book cash | 10,000 |
| Reconciling item: “outstanding check 1001” added on the bank side | +300 |
| Adjusted bank | 10,000 |
| Unexplained difference | 0 |

The check has cleared. Adding it back as outstanding restores the pre-clearing bank figure so it matches books that never recorded the disbursement.

## What holds

`adjusted_bank − adjusted_book = 0`. A reviewer who only looks at that cell will tick the rec.

## What does not hold

Ref 1001 is in `bank_lines`. An outstanding check is a timing difference: on the books, not yet on the bank. This item is the opposite, and the sign on the bank side is an add-back. The unexplained difference is mechanically zero because the stale item is the entire 300 gap.

The auditor reports `DOUBLE_COUNT_CLEARED_ITEM` and `ZERO_UNEXPLAINED_IS_NOT_CLEAN`. It does **not** report `UNEXPLAINED_DIFFERENCE`.

## What cannot be concluded

That cash was stolen. The laboratory knows a ref collision between a reconciling item and a cleared bank line. It does not know intent. The same checks on `rec-clean` (outstanding check 1002 not present in bank activity; unexplained 0) stay at zero errors.

Locked by `tests/test_controls.py::test_flagship_ties_and_is_not_clean` and `test_clean_rec_has_no_error_findings`.
