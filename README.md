# Event-VLM: Efficient Vision-Language Models for Real-Time Surveillance

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)
[![PyTorch 2.0+](https://img.shields.io/badge/pytorch-2.0+-ee4c2c.svg)](https://pytorch.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Official implementation of **"Event-VLM: Scalable Vision-Language Models for Real-Time Industrial Surveillance"** (ECCV 2026).

## 🚀 Highlights

- **9× speedup** compared to standard VLM baselines
- **75% FLOPs reduction** via knowledge-guided token pruning
- **Training-free** spatial pruning with semantic awareness
- **Hazard-aware** optimization for safety-critical applications

## 📦 Installation

```bash
# Clone repository
git clone https://github.com/YOUR_USERNAME/event-vlm.git
cd event-vlm

# Create conda environment
conda create -n event-vlm python=3.10 -y
conda activate event-vlm

# Install dependencies
pip install -r requirements.txt

# Install package
pip install -e .
```

## 🏗️ Project Structure

```
event-vlm/
├── src/                    # Core implementation
│   ├── detector/           # Stage 1: Event-Triggered Gating
│   ├── pruning/            # Stage 2: Knowledge-Guided Token Pruning
│   ├── vlm/                # Stage 3: VLM with Hazard-Priority Prompting
│   └── pipeline/           # End-to-end inference
├── experiments/            # Training & evaluation scripts
├── data/                   # Dataset management
└── paper/                  # LaTeX source
```

## 🎯 Quick Start

### Inference

```python
from src.pipeline import EventVLM

# Initialize pipeline
model = EventVLM(
    detector="detr-l",      # or "yolov8s"
    vlm="llava-1.5-7b",
    device="cuda"
)

# Process video
result = model.process_video("path/to/video.mp4")
print(result.captions)
```

### Training Detector with Risk-Sensitive Loss

```bash
python experiments/train_detector.py \
    --config experiments/configs/ucf_crime.yaml \
    --detector detr-l \
    --lambda_crit 3.0 \
    --lambda_high 2.0
```

### Evaluation

```bash
# UCF-Crime benchmark
python experiments/evaluate.py --config experiments/configs/ucf_crime.yaml

# XD-Violence benchmark
python experiments/evaluate.py --config experiments/configs/xd_violence.yaml
```

### Auto-Tuning with Optuna

```bash
python experiments/auto_tune.py \
    --config experiments/configs/base.yaml \
    --n_trials 100 \
    --study_name event_vlm_tuning
```

## 📊 Benchmarks

### UCF-Crime

| Method | AUC (%) | FPS | Speedup |
|--------|---------|-----|---------|
| LLaVA-1.5 (baseline) | 85.2 | 5.4 | 1.0× |
| Video-LLaMA | 83.8 | 4.2 | 0.8× |
| **Event-VLM (Ours)** | **85.6** | **48.2** | **9.0×** |

### XD-Violence

| Method | AP (%) | FPS | Speedup |
|--------|--------|-----|---------|
| LLaVA-1.5 (baseline) | 78.4 | 5.1 | 1.0× |
| Video-LLaMA | 76.9 | 3.8 | 0.7× |
| **Event-VLM (Ours)** | **79.1** | **45.8** | **9.0×** |

## 🔧 Configuration

Key hyperparameters in `experiments/configs/base.yaml`:

```yaml
detector:
  model: "detr-l"           # detr-l, yolov8s, yolov8n
  conf_threshold: 0.5
  risk_weights:
    critical: 3.0           # fire, smoke, collapse
    high: 2.0               # forklift, machinery
    standard: 1.0           # person, vehicle

pruning:
  alpha_base: 1.2           # Base dilation factor
  beta: 0.5                 # Adaptive dilation coefficient
  
vlm:
  model: "llava-1.5-7b"
  quantization: "4bit"
  prompt_strategy: "hazard_priority"
```

## 📝 Citation

```bibtex
@inproceedings{event-vlm,
  title={Event-VLM: Scalable Vision-Language Models for Real-Time Industrial Surveillance},
  author={Your Name},
  booktitle={European Conference on Computer Vision (ECCV)},
  year={2026}
}
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
