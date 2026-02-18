# v17 Notes

Date: 2026-02-18

## What changed
- Completed post-v16 warning-stabilization pass with one-task-at-a-time micro execution (`T09`--`T14`).
- Applied small wording/layout edits to reduce overfull/underfull warnings while preserving claim scope:
  - intro sentence split at `paper/main.tex:65`,
  - related-work wording trims at `paper/main.tex:104`, `paper/main.tex:112`, `paper/main.tex:115`,
  - XD-Violence summary trim at `paper/main.tex:421`,
  - runtime-robustness paragraph trim at `paper/main.tex:543`,
  - appendix traceability table row-label tightening around `paper/main.tex:630`.
- Updated taskboard with warning-delta report:
  - `paper/reviews/2026-02-18_main-body-14p_stepwise-taskboard.md`.

## Validation
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`
- Undefined references/citations: none (log grep check).
- Main-body pressure check:
  - appendix starts at page 19 (`paper/build/main.aux`),
  - therefore main text remains within 14 pages excluding references.
- Remaining minor warnings in current log:
  - overfull hbox at `paper/main.tex:84` (0.32753pt),
  - underfull hbox at `paper/main.tex:827` (badness 1259),
  - one underfull vbox during float-page output.

## Scope note
- No new experiments were executed (server unavailable).
