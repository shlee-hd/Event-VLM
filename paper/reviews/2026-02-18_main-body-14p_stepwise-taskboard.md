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
- [x] T09: Remove overfull line at `paper/main.tex:65` by splitting/simplifying Intro sentence.
- [x] T10: Remove overfull lines at `paper/main.tex:104`, `paper/main.tex:112`, `paper/main.tex:115` via micro wording trim in Related Work.
- [x] T11: Remove overfull line at `paper/main.tex:421` (XD-Violence summary sentence).
- [x] T12: Remove overfull line at `paper/main.tex:543` (runtime-robustness appendix-reference sentence).
- [x] T13: Reduce appendix traceability-table underfull warnings by tightening row labels at `paper/main.tex:630`.
- [x] T14: Rebuild, verify no undefined refs, and capture warning delta report in this taskboard.
- [x] T15: If warning cleanup is stable, create next version snapshot (`v17`) and changelog entry.
- [x] T16: Remove residual minor overfull at `paper/main.tex:84`.
- [ ] T17: Reduce residual underfull hbox at `paper/main.tex:827` in appendix failure table.
- [ ] T18: Rebuild + warning check; if stable, create `v18` snapshot and changelog entry.

## Current Focus
- T17 only: Reduce residual underfull hbox at `paper/main.tex:827` in appendix failure table.

## T14 Warning Delta Report
- Baseline (start of T09 stabilization): overfull hbox 7, underfull hbox 5, underfull vbox 1.
- Current (after T14 rebuild): overfull hbox 1 (`paper/main.tex:84`, 0.32753pt), underfull hbox 1 (`paper/main.tex:827`, badness 1259), underfull vbox 1 (output routine around float page).
- Undefined references/citations: none (`grep -i "undefined"` in `paper/build/main.log` returns empty).
- Page-budget checkpoint: appendix still starts at page 19 (`paper/build/main.aux`), keeping main body (excluding references) within the 14-page target.
