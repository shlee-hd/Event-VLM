# v13 Notes

Date: 2026-02-18

## What changed
- Added automated paper-table rendering pipeline for post-server experiment integration:
  - `scripts/render_paper_updates.py`
  - generates:
    - `paper/generated/table_multiseed_overview.tex`
    - `paper/generated/table_significance_summary.tex`
- Extended execution scripts to call renderer after multi-seed/significance runs:
  - `scripts/server_ready_one_click.sh` (`RENDER_PAPER_TABLES=1` default)
  - `scripts/run_experiments.sh` (`--render-paper` option)
- Added appendix-level auto-input hooks in manuscript:
  - `main.tex` now uses `\IfFileExists` for generated table blocks with safe placeholders.
- Updated benchmark expansion and coordination docs to include auto-rendered paper table handoff.

## Validation
- Shell syntax check passed for updated scripts.
- Python compile check passed for new/updated Python scripts.
- LaTeX build passed: `bash scripts/build_paper.sh`.

## Server execution outcome expectation
- After one-click run with significance enabled, paper-ready statistical tables are automatically produced under `paper/generated/` and can be included without manual copy/edit.
