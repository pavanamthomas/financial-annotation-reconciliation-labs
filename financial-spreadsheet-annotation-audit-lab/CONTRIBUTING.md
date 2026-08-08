# Contributing to the spreadsheet annotation lab

This is a personal research repository. Useful work is a tighter claim
about a range, a planted miss the checks currently skip, or a clean
case that a check falsely flags.

1. Open an issue that names the cell, the range, and the mismatch.
2. If the claim is numerical, add a test that fails on `main` before the change.
3. Keep commits narrow. Do not mix formatting with a check change.
4. Comment adjacency and coverage limits, not obvious syntax.

Recorded failures live in `docs/failures_and_corrections.md`. Remaining
bounds are in `ROADMAP.md`. Checks: `pytest` and `.github/workflows/ci.yml`.
