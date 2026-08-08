# How this lab records work

An annotation is a claim: a cell, a range, a number, and a claim type.
Before changing a check, write the claim and the mismatch that would
falsify it.

If the claim is numerical, add a test that would fail if the annotated
range were completed, or if a tying range were treated as a miss. CI on
`main` means pytest still passes and `scripts/run_all.py` still writes
tables. It is not an audit opinion on a client file.

Open an issue before widening the formula grammar. A passing `pytest`
run is a laboratory lock, not a tick mark on a client workbook.
