"""Constructed reconciliations with planted control breaks."""

from __future__ import annotations

from frclab.models import Line, ReconcilingItem, Reconciliation, ThreeWay


def flagship_stale_outstanding() -> Reconciliation:
    """Bank rec that ties by treating a cleared check as outstanding.

    Bank ending 9,700 already includes check 1001 (300) as a paid item.
    Books never recorded the check (GL 10,000). Listing 1001 as
    outstanding adds 300 back on the bank side so the rec ties.
    A zero unexplained difference is not a clean reconciliation.
    """
    return Reconciliation(
        recon_id="rec-flagship-stale-check",
        title="Cash rec that ties on a stale outstanding check",
        period="2026-03",
        bank_balance=9700.0,
        book_balance=10000.0,
        bank_lines=[
            Line(
                "B-1001",
                "bank",
                -300.0,
                "2026-03-28",
                "2026-03",
                "cash",
                "Vendor A",
                "1001",
                "cleared check 1001",
            ),
            Line(
                "B-DEP",
                "bank",
                500.0,
                "2026-03-10",
                "2026-03",
                "cash",
                "Customer",
                "DEP-10",
                "deposit",
            ),
        ],
        book_lines=[
            Line(
                "K-DEP",
                "book",
                500.0,
                "2026-03-10",
                "2026-03",
                "cash",
                "Customer",
                "DEP-10",
                "deposit",
            ),
        ],
        items=[
            ReconcilingItem(
                "RI-1001",
                "bank",
                300.0,
                "outstanding_check",
                "1001",
                status="open",
            )
        ],
        notes="Flagship: DOUBLE_COUNT_CLEARED_ITEM conceals an unrecorded disbursement.",
    )


def clean_rec() -> Reconciliation:
    """Outstanding check is not on the bank statement; rec ties honestly."""
    return Reconciliation(
        recon_id="rec-clean",
        title="Outstanding check not present in bank activity",
        period="2026-03",
        bank_balance=10000.0,
        book_balance=9700.0,
        bank_lines=[
            Line("B-DEP", "bank", 200.0, "2026-03-05", "2026-03", "cash", "Customer", "DEP-05"),
        ],
        book_lines=[
            Line("K-DEP", "book", 200.0, "2026-03-05", "2026-03", "cash", "Customer", "DEP-05"),
            Line("K-1002", "book", -300.0, "2026-03-30", "2026-03", "cash", "Vendor B", "1002"),
        ],
        items=[
            ReconcilingItem("RI-1002", "bank", -300.0, "outstanding_check", "1002", status="open"),
        ],
    )


def cutoff_break() -> Reconciliation:
    return Reconciliation(
        recon_id="rec-cutoff",
        title="Book line dated in April posted to March",
        period="2026-03",
        bank_balance=100.0,
        book_balance=100.0,
        bank_lines=[],
        book_lines=[
            Line("K-APR", "book", 40.0, "2026-04-01", "2026-03", "cash", "Customer", "DEP-APR"),
        ],
        items=[],
    )


def completeness_gap() -> Reconciliation:
    """Bank line with no book line and no reconciling item."""
    return Reconciliation(
        recon_id="rec-completeness",
        title="Bank deposit not on books and not listed as DIT/other",
        period="2026-03",
        bank_balance=800.0,
        book_balance=500.0,
        bank_lines=[
            Line("B-X", "bank", 300.0, "2026-03-12", "2026-03", "cash", "Customer Z", "DEP-Z"),
        ],
        book_lines=[],
        items=[],
    )


def classification_mispost() -> Reconciliation:
    return Reconciliation(
        recon_id="rec-class",
        title="Book cash line coded to expense",
        period="2026-03",
        bank_balance=0.0,
        book_balance=0.0,
        bank_lines=[],
        book_lines=[
            Line("K-EXP", "book", -75.0, "2026-03-08", "2026-03", "expense", "Vendor", "INV-9"),
        ],
        items=[],
    )


def three_way_breaks() -> Reconciliation:
    return Reconciliation(
        recon_id="rec-three-way",
        title="PO / receipt / invoice planted quantity and price breaks",
        period="2026-03",
        bank_balance=0.0,
        book_balance=0.0,
        matches=[
            ThreeWay("TW-CLEAN", po_qty=10, po_price=5.0, received_qty=10, invoice_qty=10, invoice_price=5.0),
            ThreeWay(
                "TW-QTY",
                po_qty=10,
                po_price=5.0,
                received_qty=8,
                invoice_qty=10,
                invoice_price=5.0,
            ),
            ThreeWay(
                "TW-PRICE",
                po_qty=4,
                po_price=20.0,
                received_qty=4,
                invoice_qty=4,
                invoice_price=25.0,
                tolerance=0.5,
            ),
        ],
    )


def all_cases() -> list[Reconciliation]:
    return [
        flagship_stale_outstanding(),
        clean_rec(),
        cutoff_break(),
        completeness_gap(),
        classification_mispost(),
        three_way_breaks(),
    ]
