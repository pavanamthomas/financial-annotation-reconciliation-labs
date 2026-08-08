# Case study: a total that ties to the wrong range

Workbook `wb-flagship-off-by-one` is a four-product Q4 revenue block.

| Cell | Label | Value | Formula |
| --- | --- | --- | --- |
| B2 | Product A | 400 | (input) |
| B3 | Product B | 350 | (input) |
| B4 | Product C | 150 | (input) |
| B5 | Product D | 50 | (input) |
| B6 | Total revenue | 900 | `SUM(B2:B4)` |

Annotation `ANN-REV-TOTAL` on B6: claim type `total`, range `B2:B4`, claimed value 900.

## What holds

`SUM(B2:B4)` = 400 + 350 + 150 = 900. The cached value matches. The annotation matches. A reviewer who only recomputes the annotated range will tick the cell.

## What does not hold

B5 is an adjacent numeric input of the same role. It is not in the range. The complete product sum is 950. Gross profit in B8 is computed from the incomplete total, so the error carries.

The auditor reports `RANGE_OFF_BY_ONE` with `excluded=B5` and `excluded_sum=50`. It does **not** report `TOTAL_MISMATCH` on this workbook. That is deliberate. `TOTAL_MISMATCH` is for a claimed number that fails to equal its own range. This annotation equals its own range.

## What cannot be concluded

That Product D “should” be in revenue. The laboratory does not know the chart of accounts. It knows adjacency, role tags on a constructed grid, and arithmetic. An excluded adjacent input is a defect class to inspect, not a posting instruction.

The same checks on `wb-clean` stay at zero errors. Recovery of a planted miss, plus a quiet clean case, is the validation claim. It is not a sampling result about spreadsheet error rates.

Locked by `tests/test_audit.py::test_flagship_range_off_by_one_excluded_product_d` and `test_flagship_annotated_range_still_sums_to_claimed`.
