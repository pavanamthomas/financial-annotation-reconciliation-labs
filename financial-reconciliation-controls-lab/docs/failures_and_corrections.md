# Failures and corrections

A rec that ties can still be the wrong description of cash.

| What was tried | How it failed | Diagnostic | Correction | Locked by | What remains unknown |
| --- | --- | --- | --- | --- | --- |
| Tick the rec because unexplained = 0 | Check 1001 is already a cleared bank line | Ref intersection of items and `bank_lines` | `DOUBLE_COUNT_CLEARED_ITEM` and `ZERO_UNEXPLAINED_IS_NOT_CLEAN` | `tests/test_controls.py::test_flagship_ties_and_is_not_clean` | Intent; other reconciling-item types with the same arithmetic |
| Ignore a bank deposit not on books | Completeness assertion | Bank ref not in books or items | `COMPLETENESS_GAP` | `tests/test_controls.py::test_completeness_gap` | Timing that belongs in DIT but was omitted |
| Post an April cash receipt to March | Line date is 1 Apr, recon period is March | Date prefix ≠ period | `CUTOFF_BREAK` | `tests/test_controls.py::test_cutoff_break` | Intraday cutoff; time zones |
| Match invoice qty to PO while receipt is short | Three-way quantity | `THREE_WAY_QTY_MISMATCH` | `tests/test_controls.py::test_three_way_qty_and_price` | Partial receipts that are still open |

Process: `docs/lab_process.md`.
