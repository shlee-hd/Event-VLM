# v16 Notes

Date: 2026-02-18

## What changed
- Executed stepwise page-control pass with one-task-at-a-time workflow.
- Improved figure readability/footprint:
  - regenerated `figure2_components.png` to a horizontal aspect source,
  - restored standalone frontier figure (resolved prior Fig.2(a) readability issue),
  - moved qualitative pruning visualization from main text to appendix.
- Reduced main-text footprint by moving low-priority tables to appendix while keeping references valid:
  - `tab:axis_gain`,
  - `tab:event_density`,
  - `tab:runtime_robustness`.
- Added and maintained micro-task board:
  - `paper/reviews/2026-02-18_main-body-14p_stepwise-taskboard.md`.

## Validation
- PASS: `bash scripts/build_paper.sh`
- Output: `/Users/shlee/codex/2026/eccv2026/paper/build/main.pdf`
- Main-body pressure check (from `build/main.aux` labels):
  - appendix starts at page 19,
  - therefore main text occupies pages 1--14 when references are excluded.

## Scope note
- No new experiments were executed (server unavailable).
