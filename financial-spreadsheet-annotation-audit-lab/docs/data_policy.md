# Data policy

This repository is constructed so that every numerical illustration can be
reproduced from the source code. It does not ship, download, or parse
third-party spreadsheet files.

## What is permitted

- Python `Workbook` / `Sheet` / `Cell` objects assembled in
  `src/fsaslab/workbooks.py`.
- Closed-form range sums and two-cell `+`/`−` recomputation.
- Finding tables written under `outputs/tables/` from those objects.

## What is excluded

- `.xlsx`, `.xls`, `.ods`, or vendor exports.
- Scraped reporting packs and undocumented CSV dumps of live books.
- Any pipeline that would require Excel, LibreOffice, or a market-data
  client.

If you apply the same checks to a live workbook, keep that work out of this
tree. I will not commit `.xlsx` files here.

## Reproducibility

There is no random seed. Changing a planted number changes the finding
table; it does not change the arithmetic identities under test (a range
sum, a cross-foot, a two-cell difference).

## Interpretation

A quiet check on a constructed grid is a laboratory result, not evidence
that a live spreadsheet is free of off-by-one totals.
