"""Ledger lines, reconciling items, and three-way match records."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Literal

Side = Literal["bank", "book"]
Assertion = Literal["completeness", "existence", "cutoff", "classification", "accuracy"]


@dataclass(frozen=True)
class Line:
    line_id: str
    side: Side
    amount: float
    date: str
    period: str
    account: str
    counterparty: str
    ref: str
    description: str = ""


@dataclass(frozen=True)
class ReconcilingItem:
    item_id: str
    side: Side
    amount: float
    reason: str
    ref: str
    status: str = "open"


@dataclass(frozen=True)
class ThreeWay:
    match_id: str
    po_qty: float
    po_price: float
    received_qty: float
    invoice_qty: float
    invoice_price: float
    tolerance: float = 0.0


@dataclass
class Reconciliation:
    recon_id: str
    title: str
    period: str
    bank_balance: float
    book_balance: float
    bank_lines: list[Line] = field(default_factory=list)
    book_lines: list[Line] = field(default_factory=list)
    items: list[ReconcilingItem] = field(default_factory=list)
    matches: list[ThreeWay] = field(default_factory=list)
    materiality: float = 50.0
    notes: str = ""


@dataclass(frozen=True)
class Finding:
    code: str
    severity: str
    recon_id: str
    ref: str | None
    assertion: Assertion | None
    message: str
    evidence: dict[str, object]
