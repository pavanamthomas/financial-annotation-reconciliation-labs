"""Control tests on constructed reconciliations.

Adjusted bank = bank_balance + sum(bank-side reconciling items).
A zero unexplained difference is reported separately from item validity.
"""

from __future__ import annotations

from frclab.models import Finding, Reconciliation

PERIOD_PREFIX = 7  # YYYY-MM


def _finding(
    code: str,
    severity: str,
    rec: Reconciliation,
    ref: str | None,
    assertion: str | None,
    message: str,
    **evidence: str | float | int | bool | None,
) -> Finding:
    return Finding(code, severity, rec.recon_id, ref, assertion, message, dict(evidence))


def adjusted_bank(rec: Reconciliation) -> float:
    delta = sum(item.amount for item in rec.items if item.side == "bank")
    return rec.bank_balance + delta


def adjusted_book(rec: Reconciliation) -> float:
    delta = sum(item.amount for item in rec.items if item.side == "book")
    return rec.book_balance + delta


def unexplained(rec: Reconciliation) -> float:
    return adjusted_bank(rec) - adjusted_book(rec)


def check_unexplained(rec: Reconciliation) -> list[Finding]:
    gap = unexplained(rec)
    if abs(gap) > 1e-9:
        severity = "error" if abs(gap) >= rec.materiality else "warning"
        return [
            _finding(
                "UNEXPLAINED_DIFFERENCE",
                severity,
                rec,
                None,
                "accuracy",
                "adjusted bank and adjusted book disagree",
                unexplained=gap,
                materiality=rec.materiality,
                adjusted_bank=adjusted_bank(rec),
                adjusted_book=adjusted_book(rec),
            )
        ]
    return []


def check_stale_outstanding(rec: Reconciliation) -> list[Finding]:
    bank_refs = {line.ref for line in rec.bank_lines}
    out: list[Finding] = []
    for item in rec.items:
        if item.reason != "outstanding_check":
            continue
        if item.ref in bank_refs:
            out.append(
                _finding(
                    "DOUBLE_COUNT_CLEARED_ITEM",
                    "error",
                    rec,
                    item.ref,
                    "existence",
                    "reconciling item is a check that already appears as a cleared bank line",
                    item_id=item.item_id,
                    amount=item.amount,
                )
            )
    return out


def check_completeness(rec: Reconciliation) -> list[Finding]:
    book_refs = {line.ref for line in rec.book_lines}
    item_refs = {item.ref for item in rec.items}
    out: list[Finding] = []
    for line in rec.bank_lines:
        if line.ref in book_refs or line.ref in item_refs:
            continue
        out.append(
            _finding(
                "COMPLETENESS_GAP",
                "error",
                rec,
                line.ref,
                "completeness",
                "bank line is not on the books and not listed as a reconciling item",
                amount=line.amount,
                line_id=line.line_id,
            )
        )
    return out


def check_existence(rec: Reconciliation) -> list[Finding]:
    bank_refs = {line.ref for line in rec.bank_lines}
    item_refs = {item.ref for item in rec.items}
    out: list[Finding] = []
    for line in rec.book_lines:
        if line.ref in bank_refs or line.ref in item_refs:
            continue
        out.append(
            _finding(
                "EXISTENCE_ORPHAN",
                "error",
                rec,
                line.ref,
                "existence",
                "book line is not on the bank statement and not listed as a reconciling item",
                amount=line.amount,
                line_id=line.line_id,
            )
        )
    return out


def check_cutoff(rec: Reconciliation) -> list[Finding]:
    out: list[Finding] = []
    for line in rec.bank_lines + rec.book_lines:
        if line.date[:PERIOD_PREFIX] != rec.period:
            if line.period == rec.period:
                out.append(
                    _finding(
                        "CUTOFF_BREAK",
                        "error",
                        rec,
                        line.ref,
                        "cutoff",
                        "line date is outside the recon period but the line is tagged to that period",
                        date=line.date,
                        period=line.period,
                        recon_period=rec.period,
                    )
                )
    return out


def check_classification(rec: Reconciliation) -> list[Finding]:
    out: list[Finding] = []
    for line in rec.book_lines:
        if line.account not in {"cash"}:
            out.append(
                _finding(
                    "CLASSIFICATION_MISPOST",
                    "warning",
                    rec,
                    line.ref,
                    "classification",
                    "cash reconciliation contains a book line not coded to cash",
                    account=line.account,
                    amount=line.amount,
                )
            )
    return out


def check_three_way(rec: Reconciliation) -> list[Finding]:
    out: list[Finding] = []
    for match in rec.matches:
        if abs(match.received_qty - match.po_qty) > match.tolerance or abs(
            match.invoice_qty - match.received_qty
        ) > match.tolerance:
            out.append(
                _finding(
                    "THREE_WAY_QTY_MISMATCH",
                    "error",
                    rec,
                    match.match_id,
                    "accuracy",
                    "PO, receipt, and invoice quantities do not agree within tolerance",
                    po_qty=match.po_qty,
                    received_qty=match.received_qty,
                    invoice_qty=match.invoice_qty,
                    tolerance=match.tolerance,
                )
            )
        po_amt = match.po_qty * match.po_price
        inv_amt = match.invoice_qty * match.invoice_price
        if abs(inv_amt - po_amt) > match.tolerance:
            out.append(
                _finding(
                    "THREE_WAY_AMOUNT_TOLERANCE",
                    "error",
                    rec,
                    match.match_id,
                    "accuracy",
                    "invoice amount differs from PO amount by more than tolerance",
                    po_amount=po_amt,
                    invoice_amount=inv_amt,
                    tolerance=match.tolerance,
                )
            )
    return out


def evaluate_controls(rec: Reconciliation) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_unexplained(rec))
    findings.extend(check_stale_outstanding(rec))
    findings.extend(check_completeness(rec))
    findings.extend(check_existence(rec))
    findings.extend(check_cutoff(rec))
    findings.extend(check_classification(rec))
    findings.extend(check_three_way(rec))
    return findings
