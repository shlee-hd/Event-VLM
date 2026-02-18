# Event-VLM Paper Changelog

## v18 (2026-02-18)
- Continued stepwise residual-warning cleanup after v17 (`T16`--`T18` in taskboard).
- Text/layout refinements:
  - removed the remaining minor overfull in the method contribution list by tightening Stage-3 wording (`paper/main.tex:84`),
  - refined appendix failure-table phrasing for better narrow-column line behavior (`paper/main.tex:827`).
- Verification:
  - PASS: `bash scripts/build_paper.sh`
  - overfull hbox: `0`
  - underfull warnings: one float-page `vbox` and one appendix-table `hbox` (non-blocking layout warnings)
  - undefined references/citations: none
  - appendix start remains page 19 in `paper/build/main.aux` (main body still within 14 pages excluding references).
- Snapshot artifacts:
  - `paper/versions/v18/main.tex`
  - `paper/versions/v18/main.bib`
  - `paper/versions/v18/Event-VLM-paper-v18.pdf`
  - `paper/Event-VLM-paper-v18.pdf`

## v17 (2026-02-18)
- Completed post-v16 stabilization micro-tasks (`T09`--`T14`) tracked in:
  - `paper/reviews/2026-02-18_main-body-14p_stepwise-taskboard.md`
- Applied targeted wording/layout trims to reduce log noise without changing evidence scope:
  - intro wording split (`paper/main.tex:65`),
  - related-work sentence compression (`paper/main.tex:104`, `paper/main.tex:112`, `paper/main.tex:115`),
  - XD-Violence summary sentence trim (`paper/main.tex:421`),
  - runtime-robustness appendix-reference sentence trim (`paper/main.tex:543`),
  - claim-traceability table row-label tightening (`paper/main.tex:630`).
- Warning delta (baseline at T09 start -> v17):
  - overfull hbox: `7 -> 1` (remaining minor `0.32753pt` at `paper/main.tex:84`),
  - underfull hbox: `5 -> 1` (remaining at `paper/main.tex:827`),
  - underfull vbox: `1 -> 1` (float-page output routine).
- Verification:
  - PASS: `bash scripts/build_paper.sh`
  - no undefined references/citations in `paper/build/main.log`
  - appendix starts at page 19 in `paper/build/main.aux` (main body remains within 14 pages excluding references).
- Snapshot artifacts:
  - `paper/versions/v17/main.tex`
  - `paper/versions/v17/main.bib`
  - `paper/versions/v17/Event-VLM-paper-v17.pdf`
  - `paper/Event-VLM-paper-v17.pdf`

## v16 (2026-02-18)
- Performed stepwise page-budget refinement with micro-task tracking (`paper/reviews/2026-02-18_main-body-14p_stepwise-taskboard.md`).
- Figure/layout updates:
  - regenerated `figure2_components.png` to horizontal aspect for improved readability/footprint,
  - reverted combined frontier/qualitative panel into standalone frontier figure for clearer readability,
  - moved qualitative pruning visualization from main text to appendix.
- Main-text footprint reduction by moving non-headline tables to appendix:
  - `tab:axis_gain`
  - `tab:event_density`
  - `tab:runtime_robustness`
- Rebuilt manuscript PDF with stable local pipeline: `bash scripts/build_paper.sh`.
- Main-body page check (excluding references): 14 pages (appendix starts at page 19 in `build/main.aux` labels).
- Snapshot artifacts:
  - `paper/versions/v16/main.tex`
  - `paper/versions/v16/main.bib`
  - `paper/versions/v16/Event-VLM-paper-v16.pdf`
  - `paper/Event-VLM-paper-v16.pdf`

## v15 (2026-02-18)
- Reduced figure footprint by merging the previous Fig.3/Fig.4 content into a single horizontal two-panel figure:
  - panel (a): speed-quality frontier (`figure4_frontier.png`),
  - panel (b): pruning/sparse-decoding qualitative visualization (`figure3_pruning.png`).
- Replaced separate full-width floats with a minipage-based side-by-side layout and updated manuscript references to `Fig.~X(a)` / `Fig.~X(b)`.
- Rebuilt manuscript PDF with stable local pipeline: `bash scripts/build_paper.sh`.
- Snapshot artifacts:
  - `paper/versions/v15/main.tex`
  - `paper/versions/v15/main.bib`
  - `paper/versions/v15/Event-VLM-paper-v15.pdf`
  - `paper/Event-VLM-paper-v15.pdf`

## v14 (2026-02-18)
- Applied claim-conservative manuscript polish after reviewer-reset request while preserving existing evidence scope:
  - tightened introductory wording to avoid overstatement and keep pilot framing explicit,
  - softened throughput/quality narrative language without changing measured numbers,
  - simplified related-work sentences for readability while preserving citation intent,
  - clarified contextual boundaries in XD-Violence main-result interpretation (`explanation-capable models in this setting`),
  - refined appendix qualitative example phrasing for concise safety-risk wording.
- Rebuilt manuscript PDF with stable local pipeline: `bash scripts/build_paper.sh`.
- No new server experiments were executed in this version (execution deferred due to unavailable experiment server).
- Snapshot artifacts:
  - `paper/versions/v14/main.tex`
  - `paper/versions/v14/main.bib`
  - `paper/versions/v14/Event-VLM-paper-v14.pdf`
  - `paper/Event-VLM-paper-v14.pdf`

## v13 (2026-02-18)
- Added automated paper-table rendering stage to close the last manual gap between server experiments and manuscript updates:
  - new renderer script: `scripts/render_paper_updates.py`,
  - generated outputs: `paper/generated/table_multiseed_overview.tex` and `paper/generated/table_significance_summary.tex`.
- Extended experiment entry scripts to invoke renderer after multi-seed/significance phases:
  - `scripts/server_ready_one_click.sh` (default `RENDER_PAPER_TABLES=1`),
  - `scripts/run_experiments.sh` (new `--render-paper` and `--paper-table-dir` flags).
- Added appendix hooks in `paper/main.tex`:
  - `\\IfFileExists`-based inclusion of generated statistical tables with safe placeholders when artifacts are not yet available.
- Updated execution/reviewer docs to include generated-table handoff flow:
  - `experiments/coordination/README.md`
  - `experiments/coordination/SERVER_READY_CHECKLIST.md`
  - `paper/reviews/2026-02-18_benchmark-expansion-plan.md`
- Snapshot artifacts:
  - `paper/versions/v13/main.tex`
  - `paper/versions/v13/main.bib`
  - `paper/versions/v13/Event-VLM-paper-v13.pdf`
  - `paper/Event-VLM-paper-v13.pdf`

## v12 (2026-02-18)
- Added ready-to-run benchmark/statistical expansion infrastructure (non-execution phase):
  - new third-benchmark config template: `experiments/configs/shanghaitech.yaml`,
  - new paired significance runner for anomaly metrics: `experiments/paired_significance.py`,
  - extended experiment entry scripts to accept configurable benchmark sets and optional significance phase:
    - `scripts/run_experiments.sh`
    - `scripts/server_ready_one_click.sh`.
- Updated `experiments/evaluate.py` prediction export schema to include per-video `label` and `reference_caption` for paired post-hoc analysis.
- Upgraded coordination artifacts for immediate server execution:
  - request queue, local sync board, server checklist, and coordination README now include 3-benchmark + significance workflow.
- Updated benchmark expansion review doc to READY-TO-EXECUTE state:
  - `paper/reviews/2026-02-18_benchmark-expansion-plan.md`.
- Added manuscript scope line for final statistical release to explicitly include one additional surveillance benchmark.
- Snapshot artifacts:
  - `paper/versions/v12/main.tex`
  - `paper/versions/v12/main.bib`
  - `paper/versions/v12/Event-VLM-paper-v12.pdf`
  - `paper/Event-VLM-paper-v12.pdf`

## v11 (2026-02-18)
- Reframed figure storyline to improve paper-level communication quality:
  - kept high-detail method figures (Fig.1/2/3),
  - added a new quantitative frontier visualization (`figure4_frontier.png`) and integrated it into the main results narrative.
- Fixed the primary figure layout issue by cropping `figure1_architecture.png` to horizontal ratio (removing large embedded top/bottom whitespace that previously made the figure look underscaled in PDF pages).
- Applied reviewer-driven writing polish in title/abstract/introduction/related-work language.
- Expanded cited literature breadth in `main.tex` from 46 to 61 unique citation keys (targeting broader reviewer expectations).
- Added reviewer follow-up memo:
  - `paper/reviews/2026-02-18_reviewer-followup-v11_figures-benchmarks.md`
- Rebuilt with stable pipeline (`scripts/build_paper.sh`) and captured snapshot artifacts:
  - `paper/versions/v11/main.tex`
  - `paper/versions/v11/main.bib`
  - `paper/versions/v11/Event-VLM-paper-v11.pdf`
  - `paper/Event-VLM-paper-v11.pdf`

## v10 (2026-02-18)
- Introduced publication-style horizontal figure redesign across all main figures:
  - unified tone and visual language for Fig.1/2/3 with cleaner typography and consistent palette,
  - switched figure assets from square layouts to horizontal rectangular compositions for better page integration.
- Updated manuscript figure includes to width-driven placement (removed aggressive trim pipeline).
- Fixed LaTeX build reliability by adding `scripts/build_paper.sh`:
  - auto-detects local TinyTeX path,
  - falls back to `pdftex + bibtex + 2x rerun` when `latexmk` is unavailable in `PATH`.
- Updated root README build instructions to use the stable build script.
- Snapshot artifacts:
  - `paper/versions/v10/main.tex`
  - `paper/versions/v10/main.bib`
  - `paper/versions/v10/Event-VLM-paper-v10.pdf`
  - `paper/Event-VLM-paper-v10.pdf`

## v9 (2026-02-18)
- Finalized figure readability/scale corrections after v8 PDF inspection:
  - enlarged Fig.1 by removing restrictive height cap and correcting trim to avoid left/right clipping,
  - aligned Fig.2 semantic role with its actual content (hazard-aware components) and removed in-image title duplication,
  - tightened Fig.3 framing with conservative trim while preserving content boundaries.
- Updated method-analysis prose to match Fig.2 semantics (design-details support, not axis ablation chart).
- Recompiled with local TinyTeX pipeline (`pdftex -fmt=pdflatex`, `bibtex`, double rerun) and confirmed successful PDF generation.
- Snapshot artifacts:
  - `paper/versions/v9/main.tex`
  - `paper/versions/v9/main.bib`
  - `paper/versions/v9/Event-VLM-paper-v9.pdf`
  - `paper/Event-VLM-paper-v9.pdf`

## v8 (2026-02-17)
- Applied post-v7 readability/layout polish:
  - refined related-work and results prose for tighter reviewer readability,
  - simplified traceability table labels to reduce layout fragility,
  - recompiled and validated clean layout warning state in `build/main.log`.
- Snapshot artifacts:
  - `paper/versions/v8/main.tex`
  - `paper/versions/v8/main.bib`
  - `paper/versions/v8/Event-VLM-paper-v8.pdf`
  - `paper/Event-VLM-paper-v8.pdf`

## v7 (2026-02-17)
- Integrated reviewer-team full audit and applied targeted manuscript hardening:
  - added stress-test protocol details for event-density and runtime-shift analyses,
  - clarified decoding speedup equation with exact form and asymptotic interpretation,
  - added explicit stream-capacity computation formula in experiments,
  - added appendix derivation note for decoding complexity assumptions,
  - added claim-to-evidence traceability table for faster reviewer verification.
- Added reviewer audit report:
  - `paper/reviews/2026-02-17_reviewer-team_full-audit_v6.md`
- Snapshot artifacts:
  - `paper/versions/v7/main.tex`
  - `paper/versions/v7/main.bib`
  - `paper/versions/v7/Event-VLM-paper-v7.pdf`
  - `paper/Event-VLM-paper-v7.pdf`

## v6 (2026-02-17)
- Added more validity-focused experiments in main text and appendix:
  - latency decomposition + stream-capacity table,
  - event-density stress test table,
  - runtime robustness table across resolution/decode-length settings,
  - trigger-threshold sensitivity table,
  - calibration overhead/amortization table.
- Snapshot artifacts:
  - `paper/versions/v6/main.tex`
  - `paper/versions/v6/main.bib`
  - `paper/versions/v6/Event-VLM-paper-v6.pdf`
  - `paper/Event-VLM-paper-v6.pdf`

## v5 (2026-02-17)
- Applied post-v4 formatting and readability polish:
  - removed title line-break token that caused hyperref PDF-string warnings,
  - reduced major table-width overflow by resizing wide comparison tables,
  - simplified long Related Work / Results / Conclusion sentences to reduce overfull lines,
  - standardized appendix table float specifiers from `[h]` to `[ht]`.
- Snapshot artifacts:
  - `paper/versions/v5/main.tex`
  - `paper/versions/v5/main.bib`
  - `paper/versions/v5/Event-VLM-paper-v5.pdf`
  - `paper/Event-VLM-paper-v5.pdf`

## v4 (2026-02-17)
- Applied claim-beautification and evidence-coverage edits on top of v3:
  - added cross-dataset main-results table on XD-Violence under unified protocol,
  - added explicit quality-retention table quantifying near-99\% caption preservation with 9$\times$ throughput gains,
  - added statistical-sufficiency scope statement in experiments and final-release protocol in appendix,
  - resolved major table-width formatting issues and recompiled with local TinyTeX toolchain.
- Snapshot artifacts:
  - `paper/versions/v4/main.tex`
  - `paper/versions/v4/main.bib`
  - `paper/versions/v4/Event-VLM-paper-v4.pdf`
  - `paper/Event-VLM-paper-v4.pdf`

## v3 (2026-02-17)
- Applied evidence-hardening edits on top of v2:
  - anonymized review metadata block (year/alignment with ECCV 2026 review mode),
  - added explicit evaluation protocol and fairness subsection,
  - resolved main/ablation model-definition ambiguity via `Event-VLM-Core` and `Event-VLM-Full`,
  - integrated `figure2_components.png` into main text as component-wise efficiency breakdown,
  - unified Stage-3 operator notation (`TopK-I`),
  - added reproducibility checklist and failure-case taxonomy in appendix.
- Snapshot artifacts:
  - `paper/versions/v3/main.tex`
  - `paper/versions/v3/main.bib`
  - `paper/versions/v3/Event-VLM-paper-v3.pdf`
  - `paper/Event-VLM-paper-v3.pdf`

## v2 (2026-02-17)
- Reframed core narrative around three-axis compute allocation (when/where/which).
- Strengthened abstract, introduction, contributions, Stage-3 framing, and conclusion.
- Clarified adaptation module as optional quality booster.
- Fixed FC ratio consistency (`F=16` => `25% of d/2=64`).
- Updated method comparison label for FASA to `arXiv'26`.
- Snapshot artifacts:
  - `paper/versions/v2/main.tex`
  - `paper/versions/v2/main.bib`
  - `paper/versions/v2/Event-VLM-paper-v2.pdf`
  - `paper/Event-VLM-paper-v2.pdf`

## v1
- First full-draft PDF baseline.

## v0
- Initial early draft PDF.
