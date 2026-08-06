"""Run every constructed workbook and write finding tables."""

from __future__ import annotations

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from fsaslab.checks import audit
from fsaslab.report import summary_lines, write_tables
from fsaslab.workbooks import all_cases


def main() -> None:
    out = ROOT / "outputs" / "tables"
    for book, anns in all_cases():
        findings = audit(book, anns)
        path = write_tables(book, findings, out)
        for line in summary_lines(book, findings):
            print(line)
        print(f"  wrote {path.name}")
        print()


if __name__ == "__main__":
    main()
