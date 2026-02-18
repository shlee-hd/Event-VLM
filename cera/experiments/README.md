# CERA Experiment Workspace

This folder stores CERA-specific experiment configuration seeds, isolated from legacy `experiments/configs`.

## Config files

- `configs/base.yaml`: CERA baseline defaults
- `configs/ucf_crime.yaml`: UCF-Crime focused override seed
- `configs/xd_violence.yaml`: XD-Violence focused override seed

## Usage

Use existing evaluation scripts with explicit config path:

```bash
python3 experiments/evaluate.py --config cera/experiments/configs/base.yaml
python3 experiments/evaluate.py --config cera/experiments/configs/ucf_crime.yaml
python3 experiments/evaluate.py --config cera/experiments/configs/xd_violence.yaml
```

Note: runtime dependencies (e.g., `omegaconf`, model/runtime packages) must be installed in the active environment.
