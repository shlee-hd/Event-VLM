# v21 Notes

Date: 2026-02-18

## What changed
- Increased the frontier figure display width from `0.96\textwidth` to `\textwidth` in `paper/main.tex` (`fig:frontier`).
- Kept float placement at `[!b]` to preserve stable page-flow behavior.
- No claim, experiment, or table content changes.

## Validation
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`
- Warning status:
  - overfull hbox: none
  - underfull hbox: none
  - underfull vbox: one non-blocking float-output boundary warning
- Undefined references/citations: none
- Main-body budget check:
  - appendix starts at page 19 (`paper/build/main.aux`)
  - main text remains within 14 pages excluding references.

## Scope note
- No new experiments were executed (server unavailable).
