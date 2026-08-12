"""Load constructed YAML cases into Document objects."""

from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml

from fdavlab.models import Document, Span

ROOT = Path(__file__).resolve().parents[2]
CASES = ROOT / "cases"

REQUIRED = (
    "id",
    "doc_type",
    "text",
    "currency",
    "gold",
    "candidate",
)


def _span(raw: dict[str, Any], default_rater: str) -> Span:
    return Span(
        annotation_id=str(raw["id"]),
        start=int(raw["start"]),
        end=int(raw["end"]),
        label=raw["label"],
        parsed_value=raw.get("parsed_value"),
        rater=str(raw.get("rater", default_rater)),
    )


def document_from_mapping(raw: dict[str, Any]) -> Document:
    missing = [k for k in REQUIRED if k not in raw]
    if missing:
        raise ValueError(f"case missing keys: {missing}")
    gold = [_span(s, "gold") for s in raw.get("gold") or []]
    candidate = [_span(s, "A") for s in raw.get("candidate") or []]
    rater_b = [_span(s, "B") for s in raw.get("rater_b") or []]
    return Document(
        document_id=str(raw["id"]),
        doc_type=raw["doc_type"],
        text=str(raw["text"]),
        currency=str(raw["currency"]),
        notes=str(raw.get("notes", "")),
        gold=gold,
        candidate=candidate,
        rater_b=rater_b,
    )


def load_case(path: Path) -> Document:
    with path.open(encoding="utf-8") as handle:
        raw = yaml.safe_load(handle)
    if not isinstance(raw, dict):
        raise ValueError(f"case is not a mapping: {path}")
    return document_from_mapping(raw)


def load_all(cases_dir: Path | None = None) -> list[Document]:
    root = cases_dir or CASES
    paths = sorted(root.rglob("*.yaml"))
    return [load_case(p) for p in paths]
