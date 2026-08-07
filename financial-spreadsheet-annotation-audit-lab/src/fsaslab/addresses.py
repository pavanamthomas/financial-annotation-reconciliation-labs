"""A1 addresses and rectangular ranges.

Only the A1 grammar used by the constructed workbooks is implemented.
Whole-column references and structured tables are out of scope.
"""

from __future__ import annotations

import re

_ADDR = re.compile(r"^([A-Z]+)([1-9][0-9]*)$")
_RANGE = re.compile(r"^([A-Z]+[1-9][0-9]*):([A-Z]+[1-9][0-9]*)$")


def col_letters_to_index(letters: str) -> int:
    n = 0
    for ch in letters.upper():
        if not ("A" <= ch <= "Z"):
            raise ValueError(f"not a column letter: {letters!r}")
        n = n * 26 + (ord(ch) - ord("A") + 1)
    return n - 1


def index_to_col_letters(index: int) -> str:
    if index < 0:
        raise ValueError("column index must be non-negative")
    n = index + 1
    letters: list[str] = []
    while n:
        n, rem = divmod(n - 1, 26)
        letters.append(chr(ord("A") + rem))
    return "".join(reversed(letters))


def parse_address(address: str) -> tuple[int, int]:
    """Return (row_index_0, col_index_0) for an A1 address."""
    m = _ADDR.fullmatch(address.strip().upper())
    if m is None:
        raise ValueError(f"not an A1 address: {address!r}")
    col = col_letters_to_index(m.group(1))
    row = int(m.group(2)) - 1
    return row, col


def format_address(row: int, col: int) -> str:
    if row < 0 or col < 0:
        raise ValueError("row and column must be non-negative")
    return f"{index_to_col_letters(col)}{row + 1}"


def expand_range(spec: str) -> list[str]:
    """Expand a rectangular A1 range into addresses in row-major order.

    A single address is treated as a one-cell range.
    """
    text = spec.strip().upper()
    if _ADDR.fullmatch(text):
        return [text]
    m = _RANGE.fullmatch(text)
    if m is None:
        raise ValueError(f"not an A1 range: {spec!r}")
    r1, c1 = parse_address(m.group(1))
    r2, c2 = parse_address(m.group(2))
    r_lo, r_hi = min(r1, r2), max(r1, r2)
    c_lo, c_hi = min(c1, c2), max(c1, c2)
    return [
        format_address(r, c)
        for r in range(r_lo, r_hi + 1)
        for c in range(c_lo, c_hi + 1)
    ]


def neighbours(address: str) -> list[str]:
    """Four-adjacent cells (up, down, left, right)."""
    row, col = parse_address(address)
    out: list[str] = []
    if row > 0:
        out.append(format_address(row - 1, col))
    out.append(format_address(row + 1, col))
    if col > 0:
        out.append(format_address(row, col - 1))
    out.append(format_address(row, col + 1))
    return out
