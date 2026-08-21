# How this lab records work

A reconciling item is a claim: a side, an amount, a reason, and a ref.
Before changing a check, write the assertion (completeness, existence,
cutoff, classification, accuracy) and the mismatch that would falsify it.

If the claim is numerical, add a test that would fail if a stale
outstanding check were treated as a clean tie-out. CI on `main` means
pytest still passes. It is not an audit opinion.

File an issue if a reconciling-item reason should be treated as stale
the way outstanding checks are. Do not treat a green CI run as a SOX
memo.
