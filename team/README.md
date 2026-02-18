# Research Team Structure

This directory defines team roles, ownership, handoff interfaces, and quality gates.

## Team Map
- `01_team-operating-model.md`: overall operating model and cadence
- `02_experiment-team.md`: experiment execution ownership (local Ubuntu + secure VM)
- `03_reviewer-team.md`: deep review ownership (literature, logic, visuals, equations, impact)
- `04_model-method-team.md`: method and ablation design ownership
- `05_data-benchmark-team.md`: dataset and benchmark strategy ownership
- `06_writing-figure-team.md`: manuscript clarity and visual communication ownership
- `07_mle-infra-team.md`: reproducibility, automation, and environment reliability ownership
- `08_release-risk-team.md`: submission quality gate and risk control ownership
- `09_non-experiment-next-actions-2026-02-17.md`: immediate action board for all non-experiment teams
- `10_non-experiment-command-board-2026-02-18.md`: v13 remediation command board (all teams, server-unavailable mode)

## Primary Principle
- Every claim in the paper must map to at least one reproducible artifact (table, figure, or log).

## Single Source of Truth for Remote Experiment Sync
- Use `experiments/coordination/` as the canonical sync area between this workspace and external execution environments.
