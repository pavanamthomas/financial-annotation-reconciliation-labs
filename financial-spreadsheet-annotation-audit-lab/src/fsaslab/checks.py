"""Deterministic annotation-audit checks.

Each check is a predicate on a constructed grid and a constructed
annotation list. A quiet check on the clean workbook is as much of the
design as a finding on a planted defect.
"""

from __future__ import annotations

from collections import defaultdict

from fsaslab.addresses import expand_range, neighbours
from fsaslab.formulas import evaluate, numeric_value, range_sum
from fsaslab.models import Annotation, Finding, Workbook

CODES = (
    "RANGE_OFF_BY_ONE",
    "RANGE_INCLUDES_SUBTOTAL",
    "TOTAL_MISMATCH",
    "CROSS_FOOT_FAILURE",
    "FORMULA_CLAIM_ON_HARDCODE",
    "HIDDEN_INSIDE_TOTAL",
    "DUPLICATE_ANNOTATION",
    "ANNOTATION_ORPHAN",
    "SIGN_CONVENTION",
    "STALE_CLAIMED_VALUE",
    "UNAUDITED_MATERIAL",
)


def _finding(
    code: str,
    severity: str,
    sheet: str,
    cell: str,
    annotation_id: str | None,
    message: str,
    **evidence: str | float | int | bool | None,
) -> Finding:
    return Finding(code, severity, sheet, cell, annotation_id, message, dict(evidence))


def check_orphans(book: Workbook, annotations: list[Annotation]) -> list[Finding]:
    out: list[Finding] = []
    for ann in annotations:
        sheet = book.sheets.get(ann.sheet)
        if sheet is None or sheet.get(ann.cell) is None:
            out.append(
                _finding(
                    "ANNOTATION_ORPHAN",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "annotation points at a cell that is not on the sheet",
                )
            )
    return out


def check_duplicates(annotations: list[Annotation]) -> list[Finding]:
    groups: dict[tuple[str, str], list[Annotation]] = defaultdict(list)
    for ann in annotations:
        groups[(ann.sheet, ann.cell.upper())].append(ann)
    out: list[Finding] = []
    for (sheet, cell), anns in groups.items():
        if len(anns) > 1:
            ids = ",".join(a.annotation_id for a in anns)
            out.append(
                _finding(
                    "DUPLICATE_ANNOTATION",
                    "warning",
                    sheet,
                    cell,
                    anns[0].annotation_id,
                    "more than one annotation on the same cell",
                    annotation_ids=ids,
                    count=len(anns),
                )
            )
    return out


def check_total_claims(book: Workbook, annotations: list[Annotation]) -> list[Finding]:
    out: list[Finding] = []
    for ann in annotations:
        if ann.claim_type not in {"total", "sign"}:
            continue
        sheet = book.sheets.get(ann.sheet)
        if sheet is None or ann.claimed_range is None:
            continue
        reconstructed, addresses, missing = range_sum(sheet, ann.claimed_range)
        if ann.claimed_value is not None and abs(reconstructed - float(ann.claimed_value)) > 1e-9:
            out.append(
                _finding(
                    "TOTAL_MISMATCH",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "claimed total does not equal the sum of the claimed range",
                    claimed=float(ann.claimed_value),
                    reconstructed=reconstructed,
                    missing=",".join(missing),
                )
            )
        cell = sheet.get(ann.cell)
        if cell is not None and isinstance(cell.value, (int, float)):
            if abs(float(cell.value) - reconstructed) > 1e-9:
                out.append(
                    _finding(
                        "TOTAL_MISMATCH",
                        "error",
                        ann.sheet,
                        ann.cell,
                        ann.annotation_id,
                        "cell value does not equal the sum of the claimed range",
                        cell_value=float(cell.value),
                        reconstructed=reconstructed,
                    )
                )
        roles = {addr: (sheet.get(addr).role if sheet.get(addr) else None) for addr in addresses}
        if any(role in {"total", "subtotal"} for addr, role in roles.items() if addr != ann.cell.upper()):
            included = ",".join(addr for addr, role in roles.items() if role in {"total", "subtotal"})
            out.append(
                _finding(
                    "RANGE_INCLUDES_SUBTOTAL",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "claimed range includes a cell marked as a total or subtotal",
                    included=included,
                )
            )
        addr_set = {a.upper() for a in addresses}
        adjacent_numeric: list[str] = []
        for addr in addresses:
            for nb in neighbours(addr):
                if nb in addr_set or nb == ann.cell.upper():
                    continue
                other = sheet.get(nb)
                if other is None or other.role != "input":
                    continue
                if numeric_value(sheet, nb) is None:
                    continue
                adjacent_numeric.append(nb)
        adjacent_numeric = sorted(set(adjacent_numeric))
        if adjacent_numeric:
            extra = sum(numeric_value(sheet, a) or 0.0 for a in adjacent_numeric)
            out.append(
                _finding(
                    "RANGE_OFF_BY_ONE",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "adjacent numeric input sits outside the claimed total range",
                    excluded=",".join(adjacent_numeric),
                    excluded_sum=extra,
                    annotated_sum=reconstructed,
                )
            )
        hidden = [addr for addr in addresses if (sheet.get(addr) and sheet.get(addr).hidden)]
        if hidden:
            out.append(
                _finding(
                    "HIDDEN_INSIDE_TOTAL",
                    "warning",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "claimed range includes a hidden cell",
                    hidden=",".join(hidden),
                )
            )
    return out


def check_cross_foot(book: Workbook, annotations: list[Annotation]) -> list[Finding]:
    out: list[Finding] = []
    for ann in annotations:
        if ann.claim_type != "cross_foot" or ann.claimed_range is None:
            continue
        sheet = book.sheets.get(ann.sheet)
        if sheet is None:
            continue
        body = expand_range(ann.claimed_range)
        from fsaslab.addresses import format_address, parse_address

        coords = [parse_address(a) for a in body]
        row_ids = sorted({r for r, _ in coords})
        col_ids = sorted({c for _, c in coords})

        row_totals = []
        for r in row_ids:
            row_totals.append(sum(numeric_value(sheet, format_address(r, c)) or 0.0 for c in col_ids))
        col_totals = []
        for c in col_ids:
            col_totals.append(sum(numeric_value(sheet, format_address(r, c)) or 0.0 for r in row_ids))
        row_sum = float(sum(row_totals))
        col_sum = float(sum(col_totals))
        claimed = float(ann.claimed_value) if ann.claimed_value is not None else None
        cell_val = numeric_value(sheet, ann.cell)
        if abs(row_sum - col_sum) > 1e-9:
            out.append(
                _finding(
                    "CROSS_FOOT_FAILURE",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "row totals and column totals disagree",
                    row_sum=row_sum,
                    col_sum=col_sum,
                )
            )
        if claimed is not None and abs(claimed - row_sum) > 1e-9:
            out.append(
                _finding(
                    "CROSS_FOOT_FAILURE",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "claimed grand total does not equal the body sum",
                    claimed=claimed,
                    body_sum=row_sum,
                )
            )
        if cell_val is not None and abs(cell_val - row_sum) > 1e-9:
            out.append(
                _finding(
                    "CROSS_FOOT_FAILURE",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "grand-total cell does not equal the body sum",
                    cell_value=cell_val,
                    body_sum=row_sum,
                )
            )
    return out


def check_formula_claims(book: Workbook, annotations: list[Annotation]) -> list[Finding]:
    out: list[Finding] = []
    for ann in annotations:
        if ann.claim_type != "formula":
            continue
        sheet = book.sheets.get(ann.sheet)
        if sheet is None:
            continue
        cell = sheet.get(ann.cell)
        if cell is None:
            continue
        if not cell.formula:
            out.append(
                _finding(
                    "FORMULA_CLAIM_ON_HARDCODE",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "annotation claims a formula but the cell has no formula",
                    cell_value=cell.value if isinstance(cell.value, (int, float)) else None,
                )
            )
            continue
        result = evaluate(sheet, cell.formula)
        if result.ok and result.value is not None and isinstance(cell.value, (int, float)):
            if abs(result.value - float(cell.value)) > 1e-9:
                out.append(
                    _finding(
                        "STALE_CLAIMED_VALUE",
                        "error",
                        ann.sheet,
                        ann.cell,
                        ann.annotation_id,
                        "cached value does not match the recomputed formula",
                        cached=float(cell.value),
                        recomputed=result.value,
                    )
                )
        if ann.claimed_value is not None and isinstance(cell.value, (int, float)):
            if abs(float(ann.claimed_value) - float(cell.value)) > 1e-9:
                out.append(
                    _finding(
                        "STALE_CLAIMED_VALUE",
                        "warning",
                        ann.sheet,
                        ann.cell,
                        ann.annotation_id,
                        "annotation claimed_value does not match the cell",
                        claimed=float(ann.claimed_value),
                        cell_value=float(cell.value),
                    )
                )
    return out


def check_sign_convention(book: Workbook, annotations: list[Annotation]) -> list[Finding]:
    out: list[Finding] = []
    for ann in annotations:
        if ann.claim_type != "sign" or ann.claimed_range is None:
            continue
        sheet = book.sheets.get(ann.sheet)
        if sheet is None:
            continue
        reconstructed, _, _ = range_sum(sheet, ann.claimed_range)
        net_cell = numeric_value(sheet, ann.cell)
        from fsaslab.addresses import format_address, parse_address

        labels = []
        for addr in expand_range(ann.claimed_range):
            row, _ = parse_address(addr)
            label_cell = sheet.get(format_address(row, 0))
            label = str(label_cell.value).lower() if label_cell and label_cell.value is not None else ""
            labels.append((addr, label, numeric_value(sheet, addr)))
        contra = [
            item
            for item in labels
            if any(w in item[1] for w in ("return", "refund", "discount", "allowance"))
        ]
        if contra and net_cell is not None and abs(net_cell - reconstructed) < 1e-9:
            out.append(
                _finding(
                    "SIGN_CONVENTION",
                    "error",
                    ann.sheet,
                    ann.cell,
                    ann.annotation_id,
                    "contra-revenue line is stored positive and added into the net",
                    contra=",".join(a for a, _, _ in contra),
                    summed=reconstructed,
                    net=net_cell,
                )
            )
    return out


def check_unaudited_material(
    book: Workbook,
    annotations: list[Annotation],
    *,
    threshold: float = 100.0,
) -> list[Finding]:
    annotated = {(a.sheet, a.cell.upper()) for a in annotations}
    out: list[Finding] = []
    for sheet_name, sheet in book.sheets.items():
        for addr, cell in sheet.cells.items():
            if cell.role != "input":
                continue
            val = numeric_value(sheet, addr)
            if val is None or abs(val) < threshold:
                continue
            if (sheet_name, addr.upper()) in annotated:
                continue
            out.append(
                _finding(
                    "UNAUDITED_MATERIAL",
                    "info",
                    sheet_name,
                    addr,
                    None,
                    "numeric input above the materiality threshold has no annotation",
                    value=val,
                    threshold=threshold,
                )
            )
    return out


def audit(book: Workbook, annotations: list[Annotation]) -> list[Finding]:
    findings: list[Finding] = []
    findings.extend(check_orphans(book, annotations))
    findings.extend(check_duplicates(annotations))
    findings.extend(check_total_claims(book, annotations))
    findings.extend(check_cross_foot(book, annotations))
    findings.extend(check_formula_claims(book, annotations))
    findings.extend(check_sign_convention(book, annotations))
    findings.extend(check_unaudited_material(book, annotations))
    return findings
