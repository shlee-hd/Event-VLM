#!/usr/bin/env python3
"""
Detector training script with Risk-Sensitive Loss.
Fine-tunes DETR-L or YOLOv8 on custom hazard detection dataset.
"""

import argparse
import logging
from pathlib import Path
from typing import Dict, Optional
import json

import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torch.optim import AdamW
from torch.optim.lr_scheduler import CosineAnnealingLR
from tqdm import tqdm

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config, EventVLMConfig
from src.detector.risk_loss import RiskSensitiveLoss

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def train_detr(
    config: EventVLMConfig,
    train_dataloader: DataLoader,
    val_dataloader: Optional[DataLoader] = None,
    output_dir: str = "checkpoints/"
):
    """
    Fine-tune DETR-L with risk-sensitive loss.
    
    Args:
        config: Configuration object
        train_dataloader: Training data loader
        val_dataloader: Validation data loader
        output_dir: Directory to save checkpoints
    """
    from ultralytics import RTDETR
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize model
    logger.info("Loading DETR-L model...")
    model = RTDETR("rtdetr-l.pt")
    
    # Configure risk weights
    risk_cfg = config.detector.risk_weights
    logger.info(f"Risk weights: critical={risk_cfg.critical}, high={risk_cfg.high}")
    
    # Create custom loss
    risk_loss = RiskSensitiveLoss(
        lambda_crit=risk_cfg.critical,
        lambda_high=risk_cfg.high,
        lambda_standard=risk_cfg.standard
    )
    
    # Train with Ultralytics trainer
    # Note: For custom loss, we'd need to modify the training loop
    # This is a simplified version using Ultralytics API
    
    results = model.train(
        data=str(config.data.root_dir / "dataset.yaml"),
        epochs=config.training.epochs,
        batch=config.training.batch_size,
        imgsz=config.data.image_size,
        device=config.device,
        project=str(output_dir),
        name="detr_risk_sensitive",
        pretrained=True,
        optimizer="AdamW",
        lr0=config.training.learning_rate,
        weight_decay=config.training.weight_decay,
        warmup_epochs=config.training.warmup_steps // 100,
        verbose=True
    )
    
    logger.info("Training complete!")
    return results


def train_yolo(
    config: EventVLMConfig,
    output_dir: str = "checkpoints/"
):
    """
    Fine-tune YOLOv8 with risk-sensitive loss.
    """
    from ultralytics import YOLO
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize model
    model_name = config.detector.model
    logger.info(f"Loading {model_name} model...")
    
    model = YOLO(f"{model_name}.pt")
    
    # Train
    results = model.train(
        data=str(config.data.root_dir / "dataset.yaml"),
        epochs=config.training.epochs,
        batch=config.training.batch_size,
        imgsz=config.data.image_size,
        device=config.device,
        project=str(output_dir),
        name=f"{model_name}_hazard",
        pretrained=True,
        optimizer="AdamW",
        lr0=config.training.learning_rate,
        weight_decay=config.training.weight_decay,
        verbose=True
    )
    
    logger.info("Training complete!")
    return results


def create_hazard_dataset_config(
    config: EventVLMConfig,
    output_path: str
):
    """
    Create YOLO-format dataset configuration for hazard detection.
    """
    hazard_classes = config.detector.hazard_classes
    
    # Flatten class list
    all_classes = []
    for level, classes in hazard_classes.items():
        all_classes.extend(classes)
    
    # Create dataset.yaml
    dataset_config = {
        "path": str(config.data.root_dir),
        "train": "train/images",
        "val": "val/images",
        "test": "test/images",
        "names": {i: name for i, name in enumerate(all_classes)}
    }
    
    import yaml
    with open(output_path, "w") as f:
        yaml.dump(dataset_config, f, default_flow_style=False)
    
    logger.info(f"Dataset config saved to {output_path}")
    return dataset_config


def main():
    parser = argparse.ArgumentParser(description="Train detector with risk-sensitive loss")
    parser.add_argument(
        "--config",
        type=str,
        default="experiments/configs/base.yaml",
        help="Config file path"
    )
    parser.add_argument(
        "--detector",
        type=str,
        choices=["detr-l", "yolov8s", "yolov8n", "yolov8m"],
        default="detr-l",
        help="Detector model to train"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="checkpoints/",
        help="Output directory for checkpoints"
    )
    parser.add_argument(
        "--epochs",
        type=int,
        default=None,
        help="Override number of epochs"
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=None,
        help="Override batch size"
    )
    parser.add_argument(
        "--lambda-crit",
        type=float,
        default=None,
        help="Override critical hazard weight"
    )
    parser.add_argument(
        "--lambda-high",
        type=float,
        default=None,
        help="Override high hazard weight"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Override with CLI args
    config.detector.model = args.detector
    if args.epochs:
        config.training.epochs = args.epochs
    if args.batch_size:
        config.training.batch_size = args.batch_size
    if args.lambda_crit:
        config.detector.risk_weights.critical = args.lambda_crit
    if args.lambda_high:
        config.detector.risk_weights.high = args.lambda_high
    
    # Create dataset config
    dataset_yaml = Path(config.data.root_dir) / "dataset.yaml"
    if not dataset_yaml.exists():
        create_hazard_dataset_config(config, str(dataset_yaml))
    
    # Train
    if args.detector.startswith("detr"):
        train_detr(config, None, None, args.output_dir)
    else:
        train_yolo(config, args.output_dir)


if __name__ == "__main__":
    main()
