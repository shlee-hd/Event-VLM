# v18 Notes

Date: 2026-02-18

## What changed
- Executed residual-warning polish tasks after v17 (`T16`--`T18`).
- Removed the last overfull hbox warning by tightening Stage-3 contribution wording (`paper/main.tex:84`).
- Refined appendix failure-table wording to improve line behavior in narrow cells (`paper/main.tex:827`).
- Updated stepwise taskboard and advanced status to v18 snapshot completion.

## Validation
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`
- Warnings in current build:
  - overfull hbox: none,
  - underfull vbox: 1 (float-page output routine),
  - underfull hbox: 1 (appendix failure table row at `paper/main.tex:827`).
- Undefined references/citations: none.
- Main-body budget check:
  - appendix starts at page 19 (`paper/build/main.aux`),
  - main text remains within 14 pages excluding references.

## Scope note
- No new experiments were executed (server unavailable).
