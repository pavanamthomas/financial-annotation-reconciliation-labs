"""Planted control-break recovery."""

from frclab.controls import adjusted_bank, evaluate_controls, unexplained
from frclab.ledgers import (
    classification_mispost,
    clean_rec,
    completeness_gap,
    cutoff_break,
    flagship_stale_outstanding,
    three_way_breaks,
)


def codes(rec) -> set[str]:
    return {f.code for f in evaluate_controls(rec)}


def test_flagship_ties_and_is_not_clean():
    rec = flagship_stale_outstanding()
    assert abs(unexplained(rec)) < 1e-12
    assert abs(adjusted_bank(rec) - 10000.0) < 1e-12
    found = codes(rec)
    assert "DOUBLE_COUNT_CLEARED_ITEM" in found
    assert "ZERO_UNEXPLAINED_IS_NOT_CLEAN" in found
    assert "UNEXPLAINED_DIFFERENCE" not in found


def test_clean_rec_has_no_error_findings():
    rec = clean_rec()
    assert abs(unexplained(rec)) < 1e-12
    errors = [f for f in evaluate_controls(rec) if f.severity == "error"]
    assert errors == []


def test_cutoff_break():
    assert "CUTOFF_BREAK" in codes(cutoff_break())


def test_completeness_gap():
    assert "COMPLETENESS_GAP" in codes(completeness_gap())


def test_classification_mispost():
    assert "CLASSIFICATION_MISPOST" in codes(classification_mispost())


def test_three_way_qty_and_price():
    rec = three_way_breaks()
    found = codes(rec)
    assert "THREE_WAY_QTY_MISMATCH" in found
    assert "THREE_WAY_AMOUNT_TOLERANCE" in found
    qty = [f for f in evaluate_controls(rec) if f.code == "THREE_WAY_QTY_MISMATCH"]
    assert any(f.ref == "TW-QTY" for f in qty)
    amt = [f for f in evaluate_controls(rec) if f.code == "THREE_WAY_AMOUNT_TOLERANCE"]
    assert any(f.ref == "TW-PRICE" for f in amt)
    assert not any(f.ref == "TW-CLEAN" for f in evaluate_controls(rec))
