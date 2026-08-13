"""Write finding tables for every constructed document case."""

from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fdavlab.checks import validate
from fdavlab.loader import load_all


def main() -> None:
    out = ROOT / "outputs" / "tables"
    out.mkdir(parents=True, exist_ok=True)
    rows: list[dict] = []
    for doc in load_all():
        findings = validate(doc)
        codes: dict[str, int] = {}
        for f in findings:
            codes[f.code] = codes.get(f.code, 0) + 1
            rows.append(f.as_row())
        print(f"{doc.document_id} ({doc.doc_type}): {len(findings)} findings")
        for code in sorted(codes):
            print(f"  {code}: {codes[code]}")
        if not findings:
            print("  (none)")
        print()
    frame = pd.DataFrame(rows)
    path = out / "findings.csv"
    frame.to_csv(path, index=False)
    print("wrote", path)


if __name__ == "__main__":
    main()
