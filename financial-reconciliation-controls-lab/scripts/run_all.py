"""Run every constructed reconciliation and write finding tables."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from frclab.controls import adjusted_bank, adjusted_book, evaluate_controls, unexplained
from frclab.ledgers import all_cases


def main() -> None:
    out = ROOT / "outputs" / "tables"
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for rec in all_cases():
        findings = evaluate_controls(rec)
        print(
            f"{rec.recon_id}: unexplained={unexplained(rec):.2f} "
            f"adj_bank={adjusted_bank(rec):.2f} adj_book={adjusted_book(rec):.2f} "
            f"findings={len(findings)}"
        )
        counts: dict[str, int] = {}
        for f in findings:
            counts[f.code] = counts.get(f.code, 0) + 1
            rows.append(
                {
                    "recon_id": rec.recon_id,
                    "code": f.code,
                    "severity": f.severity,
                    "ref": f.ref or "",
                    "assertion": f.assertion or "",
                    "message": f.message,
                    **f.evidence,
                }
            )
        for code in sorted(counts):
            print(f"  {code}: {counts[code]}")
        if not findings:
            print("  (none)")
        print()
    path = out / "findings.csv"
    pd.DataFrame(rows).to_csv(path, index=False)
    print("wrote", path)


if __name__ == "__main__":
    main()
