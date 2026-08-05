"""Constructed workbooks with planted annotation defects.

These grids are not Excel files and not extracts from a reporting pack.
Every number is chosen so a check can be shown to fire or to stay quiet.
"""

from __future__ import annotations

from fsaslab.models import Annotation, Cell, Sheet, Workbook


def _sheet(name: str, cells: list[Cell]) -> Sheet:
    return Sheet(name=name, cells={c.address: c for c in cells})


def flagship_off_by_one() -> tuple[Workbook, list[Annotation]]:
    """P&L total annotated as SUM(B2:B4) while B5 is an adjacent revenue row.

    Reconstructing the annotated range recovers 900. The adjacent row is 50.
    An annotation that ties to its own range is not a complete total.
    """
    pnl = _sheet(
        "PnL",
        [
            Cell("A1", "Line", role="label"),
            Cell("B1", "Q4", role="label"),
            Cell("A2", "Product A", role="label"),
            Cell("B2", 400.0, role="input"),
            Cell("A3", "Product B", role="label"),
            Cell("B3", 350.0, role="input"),
            Cell("A4", "Product C", role="label"),
            Cell("B4", 150.0, role="input"),
            Cell("A5", "Product D", role="label"),
            Cell("B5", 50.0, role="input"),
            Cell("A6", "Total revenue", role="label"),
            Cell("B6", 900.0, formula="SUM(B2:B4)", role="total"),
            Cell("A7", "COGS", role="label"),
            Cell("B7", 400.0, role="input"),
            Cell("A8", "Gross profit", role="label"),
            Cell("B8", 500.0, formula="B6-B7", role="total"),
        ],
    )
    book = Workbook(
        workbook_id="wb-flagship-off-by-one",
        title="Q4 product revenue with an excluded adjacent row",
        sheets={"PnL": pnl},
        notes="Flagship: RANGE_OFF_BY_ONE on B6.",
    )
    annotations = [
        Annotation(
            "ANN-REV-TOTAL",
            sheet="PnL",
            cell="B6",
            claim_type="total",
            claimed_range="B2:B4",
            claimed_value=900.0,
            note="Q4 total revenue = SUM of product rows",
        ),
        Annotation(
            "ANN-GP",
            sheet="PnL",
            cell="B8",
            claim_type="formula",
            claimed_range=None,
            claimed_value=500.0,
            note="gross profit = revenue − COGS",
        ),
    ]
    return book, annotations


def cross_foot_break() -> tuple[Workbook, list[Annotation]]:
    """Row totals and column totals disagree at the grand total."""
    matrix = _sheet(
        "Matrix",
        [
            Cell("A1", "Dept", role="label"),
            Cell("B1", "North", role="label"),
            Cell("C1", "South", role="label"),
            Cell("D1", "Row total", role="label"),
            Cell("A2", "Hardware", role="label"),
            Cell("B2", 10.0, role="input"),
            Cell("C2", 20.0, role="input"),
            Cell("D2", 30.0, formula="SUM(B2:C2)", role="total"),
            Cell("A3", "Services", role="label"),
            Cell("B3", 15.0, role="input"),
            Cell("C3", 25.0, role="input"),
            Cell("D3", 40.0, formula="SUM(B3:C3)", role="total"),
            Cell("A4", "Col total", role="label"),
            Cell("B4", 25.0, formula="SUM(B2:B3)", role="total"),
            Cell("C4", 45.0, formula="SUM(C2:C3)", role="total"),
            # Planted: 80 instead of 70 (25+45 or 30+40).
            Cell("D4", 80.0, formula="SUM(D2:D3)", role="total"),
        ],
    )
    book = Workbook(
        "wb-cross-foot",
        "Department matrix with a broken grand total",
        sheets={"Matrix": matrix},
    )
    annotations = [
        Annotation(
            "ANN-CF",
            sheet="Matrix",
            cell="D4",
            claim_type="cross_foot",
            claimed_range="B2:C3",
            claimed_value=80.0,
            note="grand total cross-foots row and column totals",
        )
    ]
    return book, annotations


def hidden_inside_total() -> tuple[Workbook, list[Annotation]]:
    sheet = _sheet(
        "Opex",
        [
            Cell("A1", "Account", role="label"),
            Cell("B1", "Amount", role="label"),
            Cell("A2", "Rent", role="label"),
            Cell("B2", 120.0, role="input"),
            Cell("A3", "Legal (hidden)", role="label"),
            Cell("B3", 30.0, hidden=True, role="input"),
            Cell("A4", "Utilities", role="label"),
            Cell("B4", 40.0, role="input"),
            Cell("A5", "Total opex", role="label"),
            Cell("B5", 190.0, formula="SUM(B2:B4)", role="total"),
        ],
    )
    book = Workbook("wb-hidden-total", "Opex total that includes a hidden row", {"Opex": sheet})
    annotations = [
        Annotation(
            "ANN-OPEX",
            "Opex",
            "B5",
            "total",
            claimed_range="B2:B4",
            claimed_value=190.0,
            note="visible operating expenses",
        )
    ]
    return book, annotations


def hardcode_labelled_formula() -> tuple[Workbook, list[Annotation]]:
    sheet = _sheet(
        "Tax",
        [
            Cell("A1", "Taxable", role="label"),
            Cell("B1", 1000.0, role="input"),
            Cell("A2", "Tax 8%", role="label"),
            Cell("B2", 80.0, role="input"),  # hardcoded; no formula
        ],
    )
    book = Workbook("wb-hardcode-formula", "Tax amount typed, annotated as a formula", {"Tax": sheet})
    annotations = [
        Annotation(
            "ANN-TAX",
            "Tax",
            "B2",
            "formula",
            claimed_range=None,
            claimed_value=80.0,
            note="tax = 8% of taxable",
        )
    ]
    return book, annotations


def duplicate_and_orphan() -> tuple[Workbook, list[Annotation]]:
    sheet = _sheet(
        "Cash",
        [
            Cell("A1", "Cash", role="label"),
            Cell("B1", 250.0, role="input"),
        ],
    )
    book = Workbook("wb-dup-orphan", "Two annotations on one cell; one orphan pointer", {"Cash": sheet})
    annotations = [
        Annotation("ANN-CASH-1", "Cash", "B1", "audited", claimed_value=250.0, note="traced to bank"),
        Annotation("ANN-CASH-2", "Cash", "B1", "audited", claimed_value=250.0, note="second tick"),
        Annotation("ANN-GHOST", "Cash", "B9", "audited", claimed_value=0.0, note="points at empty cell"),
    ]
    return book, annotations


def sign_convention() -> tuple[Workbook, list[Annotation]]:
    sheet = _sheet(
        "IS",
        [
            Cell("A1", "Revenue", role="label"),
            Cell("B1", 500.0, role="input"),
            Cell("A2", "Returns", role="label"),
            Cell("B2", 40.0, role="input"),  # stored as positive in a contra line
            Cell("A3", "Net revenue", role="label"),
            Cell("B3", 540.0, formula="SUM(B1:B2)", role="total"),
        ],
    )
    book = Workbook(
        "wb-sign",
        "Returns stored positive and added into net revenue",
        {"IS": sheet},
    )
    annotations = [
        Annotation(
            "ANN-NET",
            "IS",
            "B3",
            "sign",
            claimed_range="B1:B2",
            claimed_value=540.0,
            note="net revenue; returns should reduce revenue",
        )
    ]
    return book, annotations


def clean_tie_out() -> tuple[Workbook, list[Annotation]]:
    """A total that includes every adjacent numeric input and matches."""
    sheet = _sheet(
        "Clean",
        [
            Cell("A1", "A", role="label"),
            Cell("B1", 10.0, role="input"),
            Cell("A2", "B", role="label"),
            Cell("B2", 20.0, role="input"),
            Cell("A3", "Total", role="label"),
            Cell("B3", 30.0, formula="SUM(B1:B2)", role="total"),
        ],
    )
    book = Workbook("wb-clean", "Annotated total that matches the reconstructed range", {"Clean": sheet})
    annotations = [
        Annotation(
            "ANN-CLEAN",
            "Clean",
            "B3",
            "total",
            claimed_range="B1:B2",
            claimed_value=30.0,
            note="two-line total",
        )
    ]
    return book, annotations


def all_cases() -> list[tuple[Workbook, list[Annotation]]]:
    return [
        flagship_off_by_one(),
        cross_foot_break(),
        hidden_inside_total(),
        hardcode_labelled_formula(),
        duplicate_and_orphan(),
        sign_convention(),
        clean_tie_out(),
    ]
