"""Workbook, annotation, and finding records.

A cell value is the cached number or label stored on the grid. A formula,
when present, is a claim about how that value was produced. The auditor
recomputes a documented subset of formulae; it does not run Excel.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Severity = Literal["error", "warning", "info"]
ClaimType = Literal[
    "total",
    "cross_foot",
    "formula",
    "hardcode",
    "sign",
    "label",
    "audited",
]


@dataclass(frozen=True)
class Cell:
    address: str
    value: float | str | None = None
    formula: str | None = None
    hidden: bool = False
    role: str | None = None


@dataclass
class Sheet:
    name: str
    cells: dict[str, Cell] = field(default_factory=dict)

    def get(self, address: str) -> Cell | None:
        return self.cells.get(address.strip().upper())

    def put(self, cell: Cell) -> None:
        self.cells[cell.address.strip().upper()] = cell


@dataclass
class Workbook:
    workbook_id: str
    title: str
    sheets: dict[str, Sheet] = field(default_factory=dict)
    notes: str = ""

    def sheet(self, name: str) -> Sheet:
        if name not in self.sheets:
            raise KeyError(f"sheet not found: {name!r}")
        return self.sheets[name]


@dataclass(frozen=True)
class Annotation:
    annotation_id: str
    sheet: str
    cell: str
    claim_type: ClaimType
    claimed_range: str | None = None
    claimed_value: float | None = None
    note: str = ""
    author: str = "constructed"


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    sheet: str
    cell: str
    annotation_id: str | None
    message: str
    evidence: dict[str, object]

    def as_row(self) -> dict[str, str | float | int | bool | None]:
        return {
            "code": self.code,
            "severity": self.severity,
            "sheet": self.sheet,
            "cell": self.cell,
            "annotation_id": self.annotation_id or "",
            "message": self.message,
            **{f"ev_{k}": v for k, v in self.evidence.items()},
        }
