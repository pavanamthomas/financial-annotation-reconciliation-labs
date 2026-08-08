# Failures and corrections

An annotation that is arithmetically true of its own range can still be
the wrong description of a total. The rows below are numerical or
conceptual failures retained in the laboratory.

| What was tried | How it failed | Diagnostic | Correction | Locked by | What remains unknown |
| --- | --- | --- | --- | --- | --- |
| Tick B6 because `SUM(B2:B4)` = 900 | Adjacent Product D (B5 = 50) is excluded | Neighbour of the range is a numeric input | Report `RANGE_OFF_BY_ONE`; do not call it `TOTAL_MISMATCH` | `tests/test_audit.py::test_flagship_range_off_by_one_excluded_product_d` | Whether Product D is revenue in a real chart of accounts |
| Quote the grand total cell as a cross-foot | Cell 80 vs body sum 70 | Recompute the body independently of D4 | Report `CROSS_FOOT_FAILURE` | `tests/test_audit.py::test_cross_foot_grand_total_does_not_equal_body` | Multi-sheet consolidations |
| Treat a typed tax amount as a formula | No formula string on the cell | Claim type `formula` vs empty formula field | `FORMULA_CLAIM_ON_HARDCODE` | `tests/test_audit.py::test_hardcode_claimed_as_formula` | Shared workbooks where cached values are stale after a recalc |
| SUM of revenue and returns stored positive | Net is 540 instead of 460 | Contra keyword on the row label | `SIGN_CONVENTION` | `tests/test_audit.py::test_sign_convention_adds_returns` | Sign conventions that are documented but not recoverable from a label |
| Include a hidden legal cost in opex | Total 190 includes 30 the reviewer does not see | `hidden=True` on B3 | `HIDDEN_INSIDE_TOTAL` | `tests/test_audit.py::test_hidden_row_inside_total` | Excel very-hidden sheets; grouped outlines |
| Eight-way neighbours on a column total | Diagonal cells next to `SUM(B2:B3)` flagged as excluded inputs | Restrict adjacency to up/down/left/right | Orthogonal `neighbours` | `tests/test_addresses.py::test_neighbours_include_adjacent_row` | Merged cells; ranges that skip a blank row |

Process: `docs/lab_process.md`.
