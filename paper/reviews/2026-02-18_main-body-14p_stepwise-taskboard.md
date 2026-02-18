# 2026-02-18 Main Body 14p Stepwise Taskboard

## Ground Rule
- Work on exactly one micro-task at a time.
- After each micro-task: build PDF, verify, commit.

## Micro Tasks
- [x] T01: Fix Fig.3 aspect ratio source asset (`figure2_components.png`) to reduce vertical footprint.
- [x] T02: Fix Fig.2(a) readability by separating combined figure and restoring a readable standalone frontier figure.
- [x] T03: Move `tab:axis_gain` from main text to appendix (keep references valid).
- [x] T04: Move `tab:event_density` from main text to appendix.
- [x] T05: Move `tab:runtime_robustness` from main text to appendix.
- [x] T06: Rebuild and check main-body page pressure (target: <=14 pages excluding references).
- [x] T07: If still over budget, move one additional low-priority item (table/figure) from main to appendix.
- [x] T08: Version snapshot + changelog update.

## Next Micro Tasks (Post-14p Stabilization)
- [ ] T09: Remove overfull line at `paper/main.tex:65` by splitting/simplifying Intro sentence.
- [ ] T10: Remove overfull lines at `paper/main.tex:104`, `paper/main.tex:112`, `paper/main.tex:115` via micro wording trim in Related Work.
- [ ] T11: Remove overfull line at `paper/main.tex:421` (XD-Violence summary sentence).
- [ ] T12: Remove overfull line at `paper/main.tex:543` (runtime-robustness appendix-reference sentence).
- [ ] T13: Reduce appendix traceability-table underfull warnings by tightening row labels at `paper/main.tex:630`.
- [ ] T14: Rebuild, verify no undefined refs, and capture warning delta report in this taskboard.
- [ ] T15: If warning cleanup is stable, create next version snapshot (`v17`) and changelog entry.

## Current Focus
- T09 only: Intro overfull line cleanup at `paper/main.tex:65`.
