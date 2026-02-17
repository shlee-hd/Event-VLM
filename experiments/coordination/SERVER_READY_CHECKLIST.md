# Server Ready Checklist

Use this checklist on the first day when experiment infrastructure becomes accessible.

## A. Access and Environment
- [ ] server identity confirmed (`hostname`, OS, GPU model).
- [ ] repo clone path fixed and shared.
- [ ] Python version confirmed.
- [ ] CUDA and driver version recorded.
- [ ] internet/package policy confirmed (online/offline).

## B. Reproducibility Setup
- [ ] current commit hash pinned.
- [ ] seed policy fixed (`41,42,43` by default).
- [ ] output root path fixed.
- [ ] run metadata schema confirmed.

## C. Dry Run
- [ ] quick sanity run succeeds.
- [ ] summary files generated.
- [ ] run log updated in this coordination folder.
- [ ] benchmark config paths validated (`ucf_crime`, `xd_violence`, `shanghaitech`).

## D. Full Run
- [ ] full multi-seed run started via one-click script.
- [ ] run IDs and ETA recorded in `RUN_LOG.md`.
- [ ] artifacts registered in `ARTIFACT_REGISTRY.md`.
- [ ] paired significance scripts executed (`none vs core/full`).

## E. Sync Back to Main Workspace
- [ ] key outputs copied or pushed.
- [ ] result summary posted in `LOCAL_UBUNTU_SYNC_BOARD.md` or secure VM protocol doc.
- [ ] pending issues captured in request queue.
