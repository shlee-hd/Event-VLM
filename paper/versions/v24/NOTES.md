# v24 Notes

Date: 2026-02-18

## What changed
- Improved Fig.3 inner-label readability by regenerating `figure2_components.png` with larger internal typography and function-local higher render DPI.
- Kept manuscript-side layout controls unchanged (`fig:component_breakdown` stays `width=0.95\textwidth` and `[!b]`).
- Preserved v23 improvements for Fig.2(a) typography and clean page-layout state.

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
