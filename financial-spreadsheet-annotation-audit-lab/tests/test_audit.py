"""Planted-defect recovery for the annotation auditor."""

from fsaslab.checks import audit
from fsaslab.formulas import evaluate
from fsaslab.workbooks import (
    clean_tie_out,
    cross_foot_break,
    duplicate_and_orphan,
    flagship_off_by_one,
    hardcode_labelled_formula,
    hidden_inside_total,
    sign_convention,
)


def codes(book_ann, wanted: str) -> list:
    book, anns = book_ann
    return [f for f in audit(book, anns) if f.code == wanted]


def test_flagship_range_off_by_one_excluded_product_d():
    hits = codes(flagship_off_by_one(), "RANGE_OFF_BY_ONE")
    assert hits, "adjacent Product D must be reported as excluded from the total"
    assert any("B5" in str(f.evidence.get("excluded", "")) for f in hits)
    excluded_sum = hits[0].evidence["excluded_sum"]
    assert abs(float(excluded_sum) - 50.0) < 1e-12


def test_flagship_annotated_range_still_sums_to_claimed():
    book, anns = flagship_off_by_one()
    sheet = book.sheet("PnL")
    result = evaluate(sheet, "SUM(B2:B4)")
    assert result.ok
    assert abs(result.value - 900.0) < 1e-12
    # Tying to the annotated range is not the same as a complete revenue total.
    assert not codes((book, anns), "TOTAL_MISMATCH")


def test_clean_workbook_has_no_error_findings():
    book, anns = clean_tie_out()
    errors = [f for f in audit(book, anns) if f.severity == "error"]
    assert errors == []


def test_cross_foot_grand_total_does_not_equal_body():
    hits = codes(cross_foot_break(), "CROSS_FOOT_FAILURE")
    assert hits
    body_sums = [f.evidence.get("body_sum") for f in hits if "body_sum" in f.evidence]
    assert any(abs(float(v) - 70.0) < 1e-12 for v in body_sums)


def test_hidden_row_inside_total():
    hits = codes(hidden_inside_total(), "HIDDEN_INSIDE_TOTAL")
    assert hits
    assert "B3" in str(hits[0].evidence.get("hidden", ""))


def test_hardcode_claimed_as_formula():
    hits = codes(hardcode_labelled_formula(), "FORMULA_CLAIM_ON_HARDCODE")
    assert len(hits) == 1
    assert hits[0].cell == "B2"


def test_duplicate_and_orphan():
    dups = codes(duplicate_and_orphan(), "DUPLICATE_ANNOTATION")
    orphans = codes(duplicate_and_orphan(), "ANNOTATION_ORPHAN")
    assert dups
    assert orphans
    assert orphans[0].cell == "B9"


def test_sign_convention_adds_returns():
    hits = codes(sign_convention(), "SIGN_CONVENTION")
    assert hits
    assert abs(float(hits[0].evidence["summed"]) - 540.0) < 1e-12
