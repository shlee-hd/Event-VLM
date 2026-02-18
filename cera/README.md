# CERA Workspace

This directory is an isolated workspace for the CERA line of work, separate from the existing Event-VLM artifacts.

## Naming lock

- Official method name: `CERA`
- Expansion: `Causal Event Reasoning and Attribution`
- Internal shorthand for modules/objectives: `CER`

## Structure

- `paper/`: ECCV paper draft and version snapshots for CERA
- `experiments/`: CERA-specific experiment config seeds
- `notes/`: kickoff and decision notes
- `scripts/`: workspace guardrails (e.g., naming checks)

## Next immediate tasks

1. Re-generate figures/tables under CERA naming and update captions.
2. Link CERA configs to dedicated run scripts (instead of shared legacy entry points).
3. Decide whether to keep `CERA-Core` / `CERA-Full` variant names or move to CER-based variant labels.
