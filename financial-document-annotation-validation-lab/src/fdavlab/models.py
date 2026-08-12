"""Document, span annotation, and finding records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

DocType = Literal["invoice", "statement", "extract"]
Label = Literal[
    "amount",
    "date",
    "account",
    "counterparty",
    "currency",
    "invoice_id",
    "line_item",
    "tax",
    "subtotal",
    "total",
]
Severity = Literal["error", "warning", "info"]


@dataclass(frozen=True)
class Span:
    annotation_id: str
    start: int
    end: int
    label: Label
    parsed_value: str | float | None = None
    rater: str = "A"


@dataclass
class Document:
    document_id: str
    doc_type: DocType
    text: str
    currency: str = "USD"
    notes: str = ""
    gold: list[Span] = field(default_factory=list)
    candidate: list[Span] = field(default_factory=list)
    rater_b: list[Span] = field(default_factory=list)


@dataclass(frozen=True)
class Finding:
    code: str
    severity: Severity
    document_id: str
    annotation_id: str | None
    message: str
    evidence: dict[str, object]

    def as_row(self) -> dict[str, str | float | int | bool | None]:
        row: dict[str, str | float | int | bool | None] = {
            "code": self.code,
            "severity": self.severity,
            "document_id": self.document_id,
            "annotation_id": self.annotation_id or "",
            "message": self.message,
        }
        row.update(self.evidence)
        return row
