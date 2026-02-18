# v23 Notes

Date: 2026-02-18

## What changed
- Improved Fig.2(a) readability by regenerating `figure4_frontier.png` with larger internal typography (axis labels/ticks, method annotations, legend) and larger markers.
- Kept in-paper figure footprint unchanged (`fig:frontier` width/placement unchanged in `main.tex`).
- Preserved prior table/figure footprint tuning from v22.

## Validation
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`
- Warning status:
  - overfull hbox: none
  - underfull hbox: none
  - underfull vbox: none
  - float-only-page warning: none
- Undefined references/citations: none
- Main-body budget check:
  - appendix starts at page 19 (`paper/build/main.aux`)
  - main text remains within 14 pages excluding references.

## Scope note
- No new experiments were executed (server unavailable).
