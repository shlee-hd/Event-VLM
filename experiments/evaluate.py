#!/usr/bin/env python3
"""
Evaluation script for Event-VLM.
Evaluates on UCF-Crime or XD-Violence benchmarks.
"""

import argparse
import json
import logging
import time
import random
from pathlib import Path
from typing import Dict, Any, List, Optional

import torch
import numpy as np
from tqdm import tqdm
from omegaconf import OmegaConf

# Add src to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import load_config, EventVLMConfig
from src.pipeline import EventVLM
from src.utils.metrics import (
    AUCMeter, TriggerReliabilityMeter, CaptionMetrics,
    compute_efficiency_metrics
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def set_global_seed(seed: int) -> None:
    """Set global RNG seed for reproducible evaluation runs."""
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


class VideoDataset:
    """Simple video dataset loader."""
    
    def __init__(
        self,
        root_dir: str,
        split: str = "test",
        annotation_file: Optional[str] = None
    ):
        self.root_dir = Path(root_dir)
        self.split = split
        
        # Load annotations if available
        if annotation_file:
            with open(annotation_file) as f:
                self.annotations = json.load(f)
        else:
            self.annotations = self._load_default_annotations()
        
        self.video_list = self._get_video_list()
    
    def _load_default_annotations(self) -> Dict:
        """Load default annotations from standard location."""
        ann_path = self.root_dir / f"{self.split}_annotations.json"
        if ann_path.exists():
            with open(ann_path) as f:
                return json.load(f)
        return {}
    
    def _get_video_list(self) -> List[Dict]:
        """Get list of videos for split."""
        videos = []
        
        video_dir = self.root_dir / self.split
        if video_dir.exists():
            for video_path in video_dir.glob("*.mp4"):
                video_id = video_path.stem
                videos.append({
                    "id": video_id,
                    "path": str(video_path),
                    "label": self.annotations.get(video_id, {}).get("label", 0),
                    "caption": self.annotations.get(video_id, {}).get("caption", ""),
                    "anomaly_frames": self.annotations.get(video_id, {}).get("anomaly_frames", [])
                })
        
        return videos
    
    def __len__(self) -> int:
        return len(self.video_list)
    
    def __getitem__(self, idx: int) -> Dict:
        return self.video_list[idx]


def evaluate(
    config: EventVLMConfig,
    output_dir: Optional[str] = None,
    quick: bool = False,
    max_videos: Optional[int] = None
) -> Dict[str, float]:
    """
    Run evaluation on dataset.
    
    Args:
        config: Configuration object
        output_dir: Directory to save results
        quick: Quick mode with fewer samples
        max_videos: Maximum videos to evaluate
        
    Returns:
        Dict of metric name to value
    """
    set_global_seed(config.seed)
    logger.info(f"Using evaluation seed: {config.seed}")

    # Initialize model
    logger.info("Initializing Event-VLM...")
    model = EventVLM(config=config, device=config.device)
    
    # Load dataset
    logger.info(f"Loading dataset: {config.data.name}")
    dataset = VideoDataset(
        root_dir=config.data.root_dir,
        split="test"
    )
    
    if quick:
        max_videos = min(10, len(dataset))
    elif max_videos:
        max_videos = min(max_videos, len(dataset))
    else:
        max_videos = len(dataset)
    
    logger.info(f"Evaluating on {max_videos} videos")
    
    # Meters
    auc_meter = AUCMeter()
    trigger_meter = TriggerReliabilityMeter()
    caption_metrics = CaptionMetrics()
    
    # Efficiency tracking
    all_tokens_used = []
    tokens_total = (config.data.image_size // 14) ** 2
    total_time = 0
    total_frames = 0
    event_frames = 0
    
    # Process videos
    predictions = []
    
    for idx in tqdm(range(max_videos), desc="Evaluating"):
        video_info = dataset[idx]
        
        try:
            result = model.process_video(
                video_path=video_info["path"],
                frame_rate=config.data.frame_rate,
                max_frames=config.data.max_frames if not quick else 50
            )
            
            # Aggregate frame-level results
            video_pred = {
                "id": video_info["id"],
                "score": 0.0,
                "triggered": any(r.is_event for r in result.frame_results),
                "caption": "",
                "fps": result.fps
            }
            
            # Get max confidence as video score
            for frame_result in result.frame_results:
                if frame_result.is_event:
                    score = max(d.confidence for d in frame_result.detections) if frame_result.detections else 0
                    video_pred["score"] = max(video_pred["score"], score)
                    
                    if frame_result.caption:
                        video_pred["caption"] = frame_result.caption
                    
                    all_tokens_used.append(frame_result.tokens_used)
                    event_frames += 1
            
            total_frames += result.processed_frames
            total_time += result.total_time
            
            predictions.append(video_pred)
            
            # Update meters
            auc_meter.update(
                np.array([video_pred["score"]]),
                np.array([video_info["label"]])
            )
            
            trigger_meter.update(
                video_pred["triggered"],
                video_info["label"] > 0
            )
            
            if video_pred["caption"] and video_info["caption"]:
                caption_metrics.update(
                    video_pred["caption"],
                    video_info["caption"]
                )
                
        except Exception as e:
            logger.error(f"Error processing {video_info['id']}: {e}")
            continue
    
    # Compute metrics
    metrics = {}
    
    # Detection metrics
    det_metrics = auc_meter.compute()
    metrics.update(det_metrics)
    
    # Trigger reliability
    trigger_metrics = trigger_meter.compute()
    metrics.update(trigger_metrics)
    
    # Caption metrics (if available)
    if caption_metrics.hypotheses:
        cap_metrics = caption_metrics.compute()
        metrics.update(cap_metrics)
    
    # Efficiency metrics
    eff_metrics = compute_efficiency_metrics(
        total_frames=total_frames,
        processed_frames=total_frames,
        event_frames=event_frames,
        tokens_used=all_tokens_used,
        tokens_total=tokens_total,
        processing_time=total_time
    )
    metrics.update(eff_metrics)
    
    # Log results
    logger.info("=" * 50)
    logger.info("Evaluation Results")
    logger.info("=" * 50)
    for key, value in sorted(metrics.items()):
        logger.info(f"{key}: {value:.4f}")
    
    # Save results
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
        
        with open(output_dir / "metrics.json", "w") as f:
            json.dump(metrics, f, indent=2)
        
        with open(output_dir / "predictions.json", "w") as f:
            json.dump(predictions, f, indent=2)
        
        logger.info(f"Results saved to {output_dir}")
    
    return metrics


def main():
    parser = argparse.ArgumentParser(description="Evaluate Event-VLM")
    parser.add_argument(
        "--config",
        type=str,
        default="experiments/configs/ucf_crime.yaml",
        help="Path to config file"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/evaluation",
        help="Output directory for results"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick evaluation with fewer samples"
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Maximum number of videos to evaluate"
    )
    parser.add_argument(
        "--detector",
        type=str,
        choices=["detr-l", "yolov8s", "yolov8n"],
        default=None,
        help="Override detector model"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Device to use"
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=None,
        help="Override random seed for reproducible evaluation"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config)
    
    # Override with CLI args
    if args.detector:
        config.detector.model = args.detector
    config.device = args.device
    if args.seed is not None:
        config.seed = args.seed
    
    # Run evaluation
    metrics = evaluate(
        config=config,
        output_dir=args.output_dir,
        quick=args.quick,
        max_videos=args.max_videos
    )
    
    print(f"\nFinal AUC: {metrics.get('auc', 0):.4f}")
    print(f"Final FPS: {metrics.get('fps', 0):.2f}")


if __name__ == "__main__":
    main()
