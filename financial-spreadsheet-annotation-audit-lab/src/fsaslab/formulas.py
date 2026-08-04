"""Recompute the formula subset used in the constructed workbooks.

Supported forms:

- ``SUM(A1:B3)``
- ``A1-B1`` or ``A1+B1`` of two cell references
- a numeric literal

Anything else is reported as unsupported. Unsupported is a coverage
limit, not a finding against the workbook.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from fsaslab.addresses import expand_range
from fsaslab.models import Sheet

_SUM = re.compile(r"^SUM\(([^)]+)\)$", re.IGNORECASE)
_BINOP = re.compile(r"^([A-Z]+[1-9][0-9]*)\s*([+-])\s*([A-Z]+[1-9][0-9]*)$")
_NUMBER = re.compile(r"^[+-]?(?:\d+\.?\d*|\.\d+)$")


@dataclass(frozen=True)
class FormulaResult:
    ok: bool
    value: float | None
    unsupported: bool
    components: tuple[str, ...]
    detail: str


def numeric_value(sheet: Sheet, address: str) -> float | None:
    cell = sheet.get(address)
    if cell is None:
        return None
    if isinstance(cell.value, (int, float)) and not isinstance(cell.value, bool):
        return float(cell.value)
    return None


def range_sum(sheet: Sheet, spec: str) -> tuple[float, tuple[str, ...], tuple[str, ...]]:
    addresses = tuple(expand_range(spec))
    total = 0.0
    missing: list[str] = []
    for addr in addresses:
        val = numeric_value(sheet, addr)
        if val is None:
            missing.append(addr)
        else:
            total += val
    return total, addresses, tuple(missing)


def evaluate(sheet: Sheet, formula: str) -> FormulaResult:
    text = formula.strip()
    if text.startswith("="):
        text = text[1:].strip()
    m_sum = _SUM.fullmatch(text)
    if m_sum:
        total, addresses, missing = range_sum(sheet, m_sum.group(1))
        return FormulaResult(
            ok=True,
            value=total,
            unsupported=False,
            components=addresses,
            detail="" if not missing else f"non-numeric in range: {','.join(missing)}",
        )
    m_bin = _BINOP.fullmatch(text.upper())
    if m_bin:
        left = numeric_value(sheet, m_bin.group(1))
        right = numeric_value(sheet, m_bin.group(3))
        if left is None or right is None:
            return FormulaResult(
                False, None, False, (m_bin.group(1), m_bin.group(3)), "operand not numeric"
            )
        value = left + right if m_bin.group(2) == "+" else left - right
        return FormulaResult(True, value, False, (m_bin.group(1), m_bin.group(3)), "")
    if _NUMBER.fullmatch(text):
        return FormulaResult(True, float(text), False, (), "literal")
    return FormulaResult(False, None, True, (), "unsupported formula")
