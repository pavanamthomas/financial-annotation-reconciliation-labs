"""Deterministic checks on constructed document annotations.

Passing schema is not a validated extraction. Arithmetic of labelled
amounts is independent of span offsets.
"""

from __future__ import annotations

from datetime import datetime

from fdavlab.models import Document, Finding, Span


def _finding(
    code: str,
    severity: str,
    doc: Document,
    annotation_id: str | None,
    message: str,
    **evidence: str | float | int | bool | None,
) -> Finding:
    return Finding(code, severity, doc.document_id, annotation_id, message, dict(evidence))


def span_text(doc: Document, span: Span) -> str:
    return doc.text[span.start : span.end]


def check_schema(doc: Document, spans: list[Span]) -> list[Finding]:
    out: list[Finding] = []
    n = len(doc.text)
    for span in spans:
        if span.start < 0 or span.end > n or span.start >= span.end:
            out.append(
                _finding(
                    "SCHEMA_SPAN_BOUNDS",
                    "error",
                    doc,
                    span.annotation_id,
                    "span start/end is not a valid slice of the document text",
                    start=span.start,
                    end=span.end,
                    n=n,
                )
            )
            continue
        if not span.label:
            out.append(
                _finding(
                    "SCHEMA_LABEL",
                    "error",
                    doc,
                    span.annotation_id,
                    "span is missing a label",
                )
            )
    return out


def check_parse(doc: Document, spans: list[Span]) -> list[Finding]:
    out: list[Finding] = []
    for span in spans:
        if span.start < 0 or span.end > len(doc.text) or span.start >= span.end:
            continue
        text = span_text(doc, span).strip()
        if span.label in {"amount", "line_item", "tax", "subtotal", "total"}:
            if span.parsed_value is None:
                out.append(
                    _finding(
                        "PARSE_MISSING",
                        "error",
                        doc,
                        span.annotation_id,
                        "numeric label has no parsed_value",
                        text=text,
                    )
                )
                continue
            try:
                parsed = float(span.parsed_value)
            except (TypeError, ValueError):
                out.append(
                    _finding(
                        "PARSE_MISMATCH",
                        "error",
                        doc,
                        span.annotation_id,
                        "parsed_value is not numeric",
                        text=text,
                        parsed_value=str(span.parsed_value),
                    )
                )
                continue
            stripped = text.replace("$", "").replace(",", "").replace("£", "").replace("€", "")
            try:
                from_text = float(stripped)
            except ValueError:
                out.append(
                    _finding(
                        "PARSE_MISMATCH",
                        "error",
                        doc,
                        span.annotation_id,
                        "span text is not a number but the label is numeric",
                        text=text,
                        parsed=parsed,
                    )
                )
                continue
            if abs(from_text - parsed) > 1e-9:
                out.append(
                    _finding(
                        "PARSE_MISMATCH",
                        "error",
                        doc,
                        span.annotation_id,
                        "span text and parsed_value disagree",
                        text=text,
                        from_text=from_text,
                        parsed=parsed,
                    )
                )
        if span.label == "date" and span.parsed_value is not None:
            try:
                datetime.strptime(str(span.parsed_value), "%Y-%m-%d")
            except ValueError:
                out.append(
                    _finding(
                        "DATE_UNPARSEABLE",
                        "error",
                        doc,
                        span.annotation_id,
                        "date parsed_value is not YYYY-MM-DD",
                        parsed_value=str(span.parsed_value),
                    )
                )
    return out


def check_exclusive_overlap(doc: Document, spans: list[Span]) -> list[Finding]:
    exclusive = {"total", "subtotal", "tax"}
    tagged = [s for s in spans if s.label in exclusive]
    out: list[Finding] = []
    for i, a in enumerate(tagged):
        for b in tagged[i + 1 :]:
            if a.start < b.end and b.start < a.end:
                out.append(
                    _finding(
                        "SPAN_OVERLAP",
                        "error",
                        doc,
                        a.annotation_id,
                        "exclusive numeric labels overlap",
                        other=b.annotation_id,
                        a_label=a.label,
                        b_label=b.label,
                    )
                )
    return out


def _amounts(spans: list[Span], label: str) -> list[float]:
    out: list[float] = []
    for span in spans:
        if span.label != label or span.parsed_value is None:
            continue
        try:
            out.append(float(span.parsed_value))
        except (TypeError, ValueError):
            continue
    return out


def check_invoice_arithmetic(doc: Document, spans: list[Span]) -> list[Finding]:
    if doc.doc_type != "invoice":
        return []
    lines = _amounts(spans, "line_item")
    taxes = _amounts(spans, "tax")
    subtotals = _amounts(spans, "subtotal")
    totals = _amounts(spans, "total")
    out: list[Finding] = []
    if lines:
        line_sum = float(sum(lines))
        if subtotals and abs(line_sum - subtotals[0]) > 1e-9:
            out.append(
                _finding(
                    "SUBTOTAL_ARITHMETIC",
                    "error",
                    doc,
                    None,
                    "labelled subtotal does not equal the sum of line items",
                    line_sum=line_sum,
                    subtotal=subtotals[0],
                )
            )
        expected_total = line_sum + (taxes[0] if taxes else 0.0)
        if totals and abs(expected_total - totals[0]) > 1e-9:
            out.append(
                _finding(
                    "TOTAL_ARITHMETIC",
                    "error",
                    doc,
                    None,
                    "labelled total does not equal line items plus tax",
                    expected=expected_total,
                    labelled_total=totals[0],
                    line_sum=line_sum,
                    tax=taxes[0] if taxes else 0.0,
                )
            )
            if subtotals and abs(totals[0] - subtotals[0]) < 1e-9:
                out.append(
                    _finding(
                        "SUBTOTAL_LABELLED_AS_TOTAL",
                        "error",
                        doc,
                        None,
                        "the span labelled total equals the subtotal, not line items plus tax",
                        subtotal=subtotals[0],
                        labelled_total=totals[0],
                        expected=expected_total,
                    )
                )
    return out


def check_scale_words(doc: Document, spans: list[Span]) -> list[Finding]:
    out: list[Finding] = []
    lower = doc.text.lower()
    for span in spans:
        if span.label not in {"amount", "line_item", "tax", "subtotal", "total"}:
            continue
        if span.parsed_value is None:
            continue
        following = lower[span.end : span.end + 16]
        scale = None
        factor = 1.0
        if "thousand" in following:
            scale, factor = "thousand", 1_000.0
        elif "million" in following:
            scale, factor = "million", 1_000_000.0
        if scale is None:
            continue
        try:
            parsed = float(span.parsed_value)
        except (TypeError, ValueError):
            continue
        text = span_text(doc, span).replace("$", "").replace(",", "").strip()
        try:
            face = float(text)
        except ValueError:
            continue
        if abs(parsed - face) < 1e-9:
            out.append(
                _finding(
                    "UNIT_MISMATCH",
                    "error",
                    doc,
                    span.annotation_id,
                    "numeric span is followed by a scale word but parsed_value is the face number",
                    scale=scale,
                    face=face,
                    parsed=parsed,
                    scaled=face * factor,
                )
            )
    return out


def check_currency(doc: Document, spans: list[Span]) -> list[Finding]:
    out: list[Finding] = []
    for span in spans:
        if span.label != "currency":
            continue
        text = span_text(doc, span).strip()
        parsed = str(span.parsed_value) if span.parsed_value is not None else text
        if parsed != doc.currency and text != doc.currency:
            out.append(
                _finding(
                    "CURRENCY_INCONSISTENT",
                    "warning",
                    doc,
                    span.annotation_id,
                    "currency span does not match the document currency field",
                    document_currency=doc.currency,
                    span_text=text,
                    parsed=parsed,
                )
            )
    return out


def exact_span_agreement(a: list[Span], b: list[Span]) -> float:
    """Share of (start, end, label) triples in A that appear in B.

    This is an exact-match rate on constructed raters, not a production
    inter-annotator study.
    """
    if not a:
        return 1.0
    keys_b = {(s.start, s.end, s.label) for s in b}
    hits = sum(1 for s in a if (s.start, s.end, s.label) in keys_b)
    return hits / len(a)


def cohens_kappa(table: list[tuple[int, int]]) -> float:
    """Cohen's kappa on a supplied 2x2 (or kxk) count table.

    Arithmetic only. Not double-coding of the YAML corpus.
    """
    import numpy as np

    mat = np.asarray(table, dtype=float)
    n = mat.sum()
    if n <= 0:
        raise ValueError("empty table")
    po = float(np.trace(mat) / n)
    pe = float((mat.sum(axis=0) / n * mat.sum(axis=1) / n).sum())
    if abs(1.0 - pe) < 1e-15:
        raise ValueError("pe = 1")
    return (po - pe) / (1.0 - pe)


def check_rater_disagreement(doc: Document) -> list[Finding]:
    if not doc.rater_b:
        return []
    rate = exact_span_agreement(doc.candidate, doc.rater_b)
    if rate < 1.0:
        return [
            _finding(
                "RATER_DISAGREEMENT",
                "info",
                doc,
                None,
                "constructed rater B does not exactly match rater A spans",
                exact_match_rate=rate,
                n_a=len(doc.candidate),
                n_b=len(doc.rater_b),
            )
        ]
    return []


def validate(doc: Document, *, use: str = "candidate") -> list[Finding]:
    spans = {"candidate": doc.candidate, "gold": doc.gold, "rater_b": doc.rater_b}[use]
    findings: list[Finding] = []
    findings.extend(check_schema(doc, spans))
    findings.extend(check_parse(doc, spans))
    findings.extend(check_exclusive_overlap(doc, spans))
    findings.extend(check_invoice_arithmetic(doc, spans))
    findings.extend(check_currency(doc, spans))
    findings.extend(check_scale_words(doc, spans))
    if use == "candidate":
        findings.extend(check_rater_disagreement(doc))
    return findings
