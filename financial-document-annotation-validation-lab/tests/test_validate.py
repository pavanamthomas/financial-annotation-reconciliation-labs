"""Schema, arithmetic, and planted-defect recovery."""

from pathlib import Path

from fdavlab.checks import cohens_kappa, validate
from fdavlab.loader import load_all, load_case

CASES = Path(__file__).resolve().parents[1] / "cases"


def by_id(doc_id: str):
    return load_case(next(CASES.rglob(f"{doc_id}.yaml")))


def codes(doc_id: str):
    doc = by_id(doc_id)
    return {f.code for f in validate(doc)}


def test_corpus_loads():
    docs = load_all()
    ids = {d.document_id for d in docs}
    assert "INV-FLAGSHIP-SUBTOTAL-AS-TOTAL" in ids
    assert "INV-CLEAN-TIE" in ids
    assert len(docs) >= 6


def test_flagship_schema_passes_arithmetic_fails():
    doc = by_id("INV-FLAGSHIP-SUBTOTAL-AS-TOTAL")
    findings = validate(doc)
    codeset = {f.code for f in findings}
    assert "SCHEMA_SPAN_BOUNDS" not in codeset
    assert "PARSE_MISMATCH" not in codeset
    assert "TOTAL_ARITHMETIC" in codeset
    arith = next(f for f in findings if f.code == "TOTAL_ARITHMETIC")
    assert abs(float(arith.evidence["expected"]) - 1080.0) < 1e-12
    assert abs(float(arith.evidence["labelled_total"]) - 1000.0) < 1e-12


def test_clean_invoice_has_no_error_findings():
    errors = [f for f in validate(by_id("INV-CLEAN-TIE")) if f.severity == "error"]
    assert errors == []


def test_parse_mismatch():
    assert "PARSE_MISMATCH" in codes("INV-PARSE-MISMATCH")


def test_overlap():
    assert "SPAN_OVERLAP" in codes("INV-OVERLAP-TOTAL-TAX")


def test_date_unparseable():
    assert "DATE_UNPARSEABLE" in codes("INV-DATE-BAD")


def test_unit_mismatch_thousand():
    assert "UNIT_MISMATCH" in codes("EXT-THOUSAND-UNSCALED")
    gold = by_id("EXT-THOUSAND-UNSCALED")
    gold_findings = validate(gold, use="gold")
    assert not any(f.code == "UNIT_MISMATCH" for f in gold_findings)


def test_statement_loads_without_invoice_arithmetic():
    doc = by_id("STMT-OPENING-CLOSING")
    assert doc.doc_type == "statement"
    assert "TOTAL_ARITHMETIC" not in {f.code for f in validate(doc)}


def test_cohens_kappa_perfect_and_known_table():
    assert abs(cohens_kappa([[10, 0], [0, 5]]) - 1.0) < 1e-12
    # [[20,5],[10,15]]: n=50, po=35/50=0.7
    # row margins 0.5/0.5, col 0.6/0.4, pe=0.5
    kappa = cohens_kappa([[20, 5], [10, 15]])
    assert abs(kappa - 0.4) < 1e-12


def test_flagship_rater_b_disagrees_on_label():
    assert "RATER_DISAGREEMENT" in codes("INV-FLAGSHIP-SUBTOTAL-AS-TOTAL")
