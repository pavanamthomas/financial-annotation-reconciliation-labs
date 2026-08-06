"""Markdown/CSV report of audit findings."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from fsaslab.models import Finding, Workbook


def to_frame(findings: list[Finding]) -> pd.DataFrame:
    if not findings:
        return pd.DataFrame(
            columns=["code", "severity", "sheet", "cell", "annotation_id", "message"]
        )
    rows = []
    for f in findings:
        row = {
            "code": f.code,
            "severity": f.severity,
            "sheet": f.sheet,
            "cell": f.cell,
            "annotation_id": f.annotation_id or "",
            "message": f.message,
        }
        for k, v in f.evidence.items():
            row[k] = v
        rows.append(row)
    return pd.DataFrame(rows)


def write_tables(
    workbook: Workbook,
    findings: list[Finding],
    directory: Path,
) -> Path:
    directory.mkdir(parents=True, exist_ok=True)
    frame = to_frame(findings)
    frame.insert(0, "workbook_id", workbook.workbook_id)
    path = directory / f"{workbook.workbook_id}.csv"
    frame.to_csv(path, index=False)
    return path


def summary_lines(workbook: Workbook, findings: list[Finding]) -> list[str]:
    counts: dict[str, int] = {}
    for f in findings:
        counts[f.code] = counts.get(f.code, 0) + 1
    lines = [f"{workbook.workbook_id}: {workbook.title}", f"  findings: {len(findings)}"]
    for code in sorted(counts):
        lines.append(f"  {code}: {counts[code]}")
    if not findings:
        lines.append("  (none)")
    return lines
