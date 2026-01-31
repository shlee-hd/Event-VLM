#!/bin/bash
# Setup script for Event-VLM environment

set -e

echo "Setting up Event-VLM environment..."

# Check Python version
python_version=$(python3 --version 2>&1 | awk '{print $2}')
echo "Python version: $python_version"

# Create conda environment if it doesn't exist
if ! conda env list | grep -q "event-vlm"; then
    echo "Creating conda environment 'event-vlm'..."
    conda create -n event-vlm python=3.10 -y
fi

echo "Activating environment..."
source "$(conda info --base)/etc/profile.d/conda.sh"
conda activate event-vlm

# Install PyTorch with CUDA
echo "Installing PyTorch..."
pip install torch torchvision --index-url https://download.pytorch.org/whl/cu118

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt

# Install package in development mode
echo "Installing event-vlm package..."
pip install -e .

# Download pretrained models
echo "Downloading pretrained models..."
python -c "from ultralytics import RTDETR; RTDETR('rtdetr-l.pt')" || echo "DETR download requires manual setup"
python -c "from ultralytics import YOLO; YOLO('yolov8s.pt')"

# Setup data directories
echo "Setting up data directories..."
mkdir -p data/ucf_crime data/xd_violence

# Create mini test dataset
echo "Creating mini test dataset..."
python data/download_datasets.py --dataset mini

echo ""
echo "Setup complete!"
echo "Activate environment with: conda activate event-vlm"
echo ""
echo "Next steps:"
echo "1. Download UCF-Crime and XD-Violence datasets"
echo "2. Run evaluation: python experiments/evaluate.py --quick"
echo "3. Run auto-tuning: python experiments/auto_tune.py --n-trials 10 --quick"
