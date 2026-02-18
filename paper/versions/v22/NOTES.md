# v22 Notes

Date: 2026-02-18

## What changed
- Compacted `tab:quality_retention` styling to reduce table footprint while keeping the same evidence values.
- Tuned Fig.3 (`fig:component_breakdown`) layout with `width=0.95\textwidth` and float placement `[!b]` to reduce page occupancy.
- No claim, benchmark, or metric changes.

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
