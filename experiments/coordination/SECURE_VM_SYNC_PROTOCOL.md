# Secure VM Sync Protocol

Use this protocol when experiments run on a restricted internal VM.

## Goal
- Keep metric provenance and sync integrity even when direct push/pull is constrained.

## Protocol Steps
1. Record run intent in `EXPERIMENT_REQUEST_QUEUE.md`.
2. Execute from pinned commit hash.
3. Save outputs under a deterministic path:
   - `outputs/<date>_<tag>/<dataset>/<variant>/<seed>/`
4. Export the following minimum bundle:
   - `summary.json`
   - `summary.md`
   - run-level `metrics.json`
   - command log text
5. Transfer bundle to main workspace through approved internal channel.
6. Register artifacts in `ARTIFACT_REGISTRY.md`.
7. Append run details to `RUN_LOG.md`.

## Required Metadata
- VM identifier
- commit hash
- configs used
- seeds
- detector/prompt strategy
- start/end time
- failure reasons (if any)

## Non-Negotiables
- no untracked manual metric edits.
- no reporting without command + commit provenance.
