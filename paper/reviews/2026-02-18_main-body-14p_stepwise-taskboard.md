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
- [x] T17: Reduce residual underfull hbox at `paper/main.tex:827` in appendix failure table.
- [x] T18: Rebuild + warning check; if stable, create `v18` snapshot and changelog entry.
- [x] T19: Eliminate remaining underfull hbox at `paper/main.tex:827` (appendix failure table).
- [x] T20: Diagnose residual underfull vbox warning and apply minimal safe fix if possible.
- [x] T21: Final rebuild/warning report and create `v19` snapshot if stable.
- [x] T22: Try minimal float-placement tweak around `fig:frontier` to remove residual underfull vbox.
- [x] T23: Rebuild and verify page-budget/refs unchanged after T22.
- [x] T24: If stable, create `v20` snapshot + changelog update.
- [x] T25: Increase `fig:frontier` display width (`0.96\textwidth` -> `\textwidth`) for readability and float-page stability.
- [x] T26: Rebuild and verify warning/page-budget impact of T25.
- [x] T27: If T25/T26 are stable, create `v21` snapshot + changelog update.
- [x] T28: Audit main-text tables for vertical whitespace inefficiency and list merge/appendix candidates (no edits).
- [ ] T29: Apply exactly one table compaction action from T28 (merge or appendix move), then rebuild.
- [ ] T30: Reduce Fig.3 (`fig:component_breakdown`) footprint with minimal readability-safe scale/aspect adjustment.
- [ ] T31: Rebuild and verify warning/page-budget impact after T29/T30.
- [ ] T32: If stable, create `v22` snapshot + changelog update.

## Current Focus
- T29 only: Apply exactly one table compaction action from T28 (merge or appendix move), then rebuild.

## T28 Audit Findings (No Edits)
- Scope audited (main text only): `tab:method_comparison`, `tab:eval_protocol`, `tab:main_results`, `tab:main_results_xd`, `tab:quality_retention`, `tab:ablation_component`, `tab:decoding_comparison`, `tab:latency_stream`.
- Candidate A (highest savings / lowest claim risk): move `tab:eval_protocol` (`paper/main.tex:331`) to appendix and keep a 1--2 sentence fairness summary in main text.
- Candidate B (high savings / moderate claim risk): move `tab:latency_stream` (`paper/main.tex:515`) to appendix and keep the stream-capacity formula + one headline number in main text.
- Candidate C (moderate savings / low risk): tighten vertical whitespace of `tab:quality_retention` (`paper/main.tex:425`) by reducing caption/body padding and converting to a compact table style.
- Excluded for now (core evidence in main narrative): `tab:main_results`, `tab:main_results_xd`, `tab:ablation_component`, `tab:decoding_comparison`, `tab:method_comparison`.

## T14 Warning Delta Report
- Baseline (start of T09 stabilization): overfull hbox 7, underfull hbox 5, underfull vbox 1.
- Current (after T14 rebuild): overfull hbox 1 (`paper/main.tex:84`, 0.32753pt), underfull hbox 1 (`paper/main.tex:827`, badness 1259), underfull vbox 1 (output routine around float page).
- Post-T18 update: overfull hbox 0, underfull hbox 1 (`paper/main.tex:827`, badness 1117), underfull vbox 1.
- Post-T19 update: overfull hbox 0, underfull hbox 0, underfull vbox 1.
- Post-T21 final update: overfull hbox 0, underfull hbox 0, underfull vbox 1 (float-output boundary only).
- Post-T23 update: underfull vbox persists but badness is reduced (4492 -> 1097) with `fig:frontier` placement tuned to `[!b]`; page-budget and references remain unchanged.
- Post-T26 update: after widening `fig:frontier` to `\textwidth`, warnings remain stable (overfull 0 / underfull hbox 0 / underfull vbox 1), no undefined refs/citations, and appendix still starts at page 19.
- Post-T27 update: `v21` snapshot created and version docs updated.
- Undefined references/citations: none (`grep -i "undefined"` in `paper/build/main.log` returns empty).
- Page-budget checkpoint: appendix still starts at page 19 (`paper/build/main.aux`), keeping main body (excluding references) within the 14-page target.
- T20 note: the remaining warning is `Underfull \vbox ... while \output is active`, observed at a float-output page boundary (around Fig.2/Fig.4 placement); no safe local text/line fix was identified without template-level layout policy changes.
