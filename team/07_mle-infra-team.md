# MLE and Infra Team

## Mission
- Make experiment execution reproducible, automatable, and environment-portable.

## Responsibilities
- maintain one-click scripts and run orchestration.
- harden config management and seed control.
- standardize output schemas and artifact locations.
- keep runbooks current for local Ubuntu and secure VM.

## Must-Have Controls
- deterministic seed plumbing.
- environment preflight checks.
- consistent output directory patterns.
- command logging and commit hash traceability.

## Deliverables
- executable scripts in `scripts/`.
- orchestration scripts in `experiments/`.
- environment sync docs in `experiments/coordination/`.
