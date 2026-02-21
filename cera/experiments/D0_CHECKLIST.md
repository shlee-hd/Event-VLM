# CERA External Run D-0 Checklist

## A) Protocol freeze check

- [ ] Confirm `CERA-EXP-LOCK-v1` is still active.
- [ ] Confirm target commit hash is recorded.
- [ ] Confirm seeds are fixed to `41,42,43`.

## B) Data and environment check

- [ ] `data/ucf_crime` exists.
- [ ] `data/xd_violence` exists.
- [ ] `python3 -c "import torch, omegaconf"` succeeds.
- [ ] GPU visibility check succeeds (`nvidia-smi`).

## C) Execution check

- [ ] Run main matrix with `run_main.sh`.
- [ ] Run ablation matrix with `run_ablation.sh`.
- [ ] Run stats and table stubs with `run_stats.sh`.
- [ ] Verify no missing `metrics.json` in expected seed folders.

## D) Paper replacement check

- [ ] Replace all `MEASURED_SWAP_*` blocks in `cera/paper/main.tex`.
- [ ] Remove/adjust non-empirical disclaimer text where needed.
- [ ] Rebuild PDF with `make -C cera/paper pdf`.
- [ ] Sanity-check references and tables in output PDF.

## E) Delivery check

- [ ] Save final outputs under `cera/experiments/results/`.
- [ ] Commit measured update files and push.
- [ ] Tag snapshot under `cera/paper/versions/vN/`.

