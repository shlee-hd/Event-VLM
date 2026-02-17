# Event-VLM

Event-VLM is an ECCV 2026 paper workspace for real-time surveillance video understanding with Vision-Language Models.
This repository is organized for two parallel goals:

1. method and evidence development,
2. paper-quality iteration with strict version tracking.

## Project focus

Event-VLM targets three inference bottlenecks at once:

- temporal redundancy: avoid running heavy VLM inference on non-event frames,
- spatial redundancy: keep only hazard-relevant visual tokens,
- decoding redundancy: reduce KV-cache access cost during generation.

The current draft also separates two evaluation variants:

- `Event-VLM-Core`: stages 1-3,
- `Event-VLM-Full`: Core + prompt adaptation.

## Repository layout

```text
eccv2026/
├── src/                        # model and pipeline implementation
├── experiments/                # training/eval scripts
│   ├── configs/                # dataset/runtime configs
│   └── coordination/           # Ubuntu/secure-VM sync docs
├── scripts/                    # one-click and utility scripts
├── paper/                      # LaTeX manuscript + versioned snapshots
│   ├── reviews/                # review outputs and team deliverables
│   └── versions/               # immutable vN snapshots
└── team/                       # role definitions and operating model
```

## Environment setup

```bash
git clone <repo-url>
cd eccv2026

python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

## Run evaluation

### Single-run evaluation

```bash
python experiments/evaluate.py --config experiments/configs/ucf_crime.yaml
python experiments/evaluate.py --config experiments/configs/xd_violence.yaml
```

### Multi-seed aggregation (recommended for paper numbers)

```bash
python experiments/multi_seed_eval.py \
  --configs experiments/configs/ucf_crime.yaml experiments/configs/xd_violence.yaml \
  --seeds 41,42,43 \
  --variants core,full \
  --detector detr-l \
  --output-dir outputs/multi_seed_eval
```

Expected outputs:

- `outputs/multi_seed_eval/summary.json`
- `outputs/multi_seed_eval/summary.md`

### One-click server execution (when server access is available)

```bash
bash scripts/server_ready_one_click.sh
```

## Paper workflow

### Build manuscript

```bash
export PATH="$(pwd)/.texlive/TinyTeX/bin/universal-darwin:$PATH"
cd paper
latexmk -pdf -interaction=nonstopmode -halt-on-error -output-directory=build main.tex
```

### Versioning policy

- every major paper change produces a new `paper/versions/vN/` snapshot,
- top-level PDF is mirrored as `paper/Event-VLM-paper-vN.pdf`,
- changelog is tracked in `paper/versions/CHANGELOG.md`.

## Team workflow

- team roles: `team/README.md`
- non-experiment immediate action board: `team/09_non-experiment-next-actions-2026-02-17.md`
- reviewer outputs and execution artifacts: `paper/reviews/`

## External environment sync

Use `experiments/coordination/` as the single source of truth for cross-environment handoff:

- `SERVER_READY_CHECKLIST.md`
- `LOCAL_UBUNTU_SYNC_BOARD.md`
- `SECURE_VM_SYNC_PROTOCOL.md`
- `EXPERIMENT_REQUEST_QUEUE.md`
- `RUN_LOG.md`
- `ARTIFACT_REGISTRY.md`

## Current status

This repository currently tracks a draft-phase paper with pilot evidence and active hardening toward submission-grade statistical reporting.
For latest manuscript outputs, check `paper/versions/README.md`.

## Citation

```bibtex
@inproceedings{event_vlm_2026,
  title={Event-VLM: Three-Axis Efficient Inference for Real-time Surveillance Video Understanding},
  author={Anonymous Authors},
  booktitle={European Conference on Computer Vision (ECCV)},
  year={2026}
}
```

## License

MIT. See `LICENSE`.
