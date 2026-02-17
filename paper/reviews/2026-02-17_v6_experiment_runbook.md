# Event-VLM v6 Experiment Runbook (2026-02-17)

## Goal
- Convert Draft V1 pilot tables into submission-grade evidence with multi-seed statistics.

## Mandatory Run Matrix (3 seeds each)
1. LLaVA-1.5 baseline (full frame)
2. Event-VLM-Core (Stages 1--3)
3. Event-VLM-Full (Core + prompt)

Datasets:
- UCF-Crime
- XD-Violence

## Metrics to Collect
- AUC
- CIDEr
- End-to-end FPS
- Trigger recall/precision
- Per-module latency (vision/prune, decode)

## Tables to Update in main.tex
- `tab:main_results`
- `tab:main_results_xd`
- `tab:quality_retention`
- `tab:latency_stream`
- `tab:event_density`
- `tab:runtime_robustness`

## Statistical Outputs
- mean +- std over 3 seeds
- 95% bootstrap CI (video-level)
- paired significance test vs baseline

## Acceptance Criteria
- Core/FulI claims in abstract and conclusion must be backed by CI-aware values.
- Any difference within overlap range should be described as directional.
- Main and appendix numbers must be internally consistent after update.
