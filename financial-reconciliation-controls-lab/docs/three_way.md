# Three-way match notes

PO, goods receipt, and invoice are three documents about one purchase.
Quantity and amount can disagree even when each document is internally
consistent.

The constructed cases sit on `rec-three-way` in `src/frclab/ledgers.py`.

| Match | What I planted |
| --- | --- |
| `TW-CLEAN` | 10 units at 5. Quiet. |
| `TW-QTY` | PO and invoice 10, receipt 8. `THREE_WAY_QTY_MISMATCH`. |
| `TW-PRICE` | 4 units, PO 20, invoice 25, tolerance 0.5. `THREE_WAY_AMOUNT_TOLERANCE`. |

I am not modelling partial receipts that stay open on purpose. A short
receipt here is a break, not a goods-in-transit account.

Cutoff on the cash rec is a different claim (`CUTOFF_BREAK`): a 1 April
book line tagged to March. Do not fold that into three-way quantity.
