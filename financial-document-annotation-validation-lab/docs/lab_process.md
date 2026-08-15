# How this lab records work

A span is a claim: offsets, a label, and a parsed value. Before changing
a check, write the claim and the mismatch that would falsify it.

If the claim is numerical, add a test that would fail if a subtotal were
accepted as a total, or if a tying invoice were flagged. CI on `main`
means pytest still passes. It is not an extraction quality report.

I keep open questions as issues in this folder. `ROADMAP.md` is the bound
I will not quietly expand.
