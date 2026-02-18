# v19 Notes

Date: 2026-02-18

## What changed
- Closed residual-warning cleanup sequence after v18 (`T19`--`T21`).
- Removed the remaining underfull hbox warning in appendix failure-table wording (`paper/main.tex:827`).
- Kept document-level layout policy unchanged (no template-level flush/ragged bottom override).

## Validation
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`
- Warning state:
  - overfull hbox: none,
  - underfull hbox: none,
  - underfull vbox: 1 (`while \output is active`, float-output page boundary).
- Undefined references/citations: none.
- Main-body budget check:
  - appendix starts at page 19 (`paper/build/main.aux`),
  - main text remains within 14 pages excluding references.

## Scope note
- No new experiments were executed (server unavailable).
