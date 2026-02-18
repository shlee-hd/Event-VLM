# v20 Notes

Date: 2026-02-18

## What changed
- Performed a minimal float-placement polish around the frontier figure.
- Updated `fig:frontier` placement from `[t]` to `[!b]` in `paper/main.tex`.
- No claim, experiment, or table/figure content changes.

## Validation
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`
- Warning status:
  - overfull hbox: none
  - underfull hbox: none
  - underfull vbox: one non-blocking float-output boundary warning
  - residual vbox badness improved from 4492 to 1097
- Undefined references/citations: none
- Main-body budget check:
  - appendix starts at page 19 (`paper/build/main.aux`)
  - main text remains within 14 pages excluding references.

## Scope note
- No new experiments were executed (server unavailable).
