# Ready-to-Run Packet (2026-02-18)

Status: READY (execution blocked by server availability only)  
Owner: MLE & Infra Team  
Request Link: `REQ-004`

## Goal
- Execute the full multi-seed + significance + paper-table rendering path without changing protocol knobs.

## Frozen Command
```bash
BENCHMARK_CONFIGS=experiments/configs/ucf_crime.yaml,experiments/configs/xd_violence.yaml,experiments/configs/shanghaitech.yaml \
VARIANTS=none,core,full \
SIGNIFICANCE=1 \
SIGNIFICANCE_BASELINE=none \
SIGNIFICANCE_CANDIDATES=core,full \
RENDER_PAPER_TABLES=1 \
bash scripts/server_ready_one_click.sh
```

## Expected Output Artifacts
- `outputs/multi_seed_eval_*/summary.json`
- `outputs/multi_seed_eval_*/summary.md`
- `outputs/multi_seed_eval_*/significance/<dataset>/<candidate>_vs_none/significance.json`
- `paper/generated/table_multiseed_overview.tex`
- `paper/generated/table_significance_summary.tex`

## Post-Run Validation Checklist
1. `summary.json` includes datasets: `ucf_crime`, `xd_violence`, `shanghaitech`.
2. Each dataset contains variants: `none`, `core`, `full`.
3. Significance JSON exists for each `(dataset, candidate)` pair where candidate is `core` or `full`.
4. Generated TeX tables compile in `paper/main.tex` without missing-file placeholders.
5. All reported headline numbers in the manuscript map to generated artifacts.

## Failure Triage
- Missing dataset rows:
  - check `BENCHMARK_CONFIGS` and config filename spelling.
- Missing significance outputs:
  - verify `SIGNIFICANCE=1`, baseline/candidate variant names, and seed alignment.
- Missing generated TeX:
  - verify `RENDER_PAPER_TABLES=1` and `scripts/render_paper_updates.py` completion.

## Handoff Protocol
1. Append run metadata to `experiments/coordination/RUN_LOG.md`.
2. Register output paths in `experiments/coordination/ARTIFACT_REGISTRY.md`.
3. Notify Reviewer + Release teams with exact artifact paths before any manuscript number update.
