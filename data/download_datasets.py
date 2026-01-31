#!/usr/bin/env python3
"""
Dataset downloader for Event-VLM.
Downloads and preprocesses UCF-Crime and XD-Violence datasets.
"""

import argparse
import os
import subprocess
import zipfile
import tarfile
from pathlib import Path
from typing import Optional
import logging
import json

import requests
from tqdm import tqdm

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


# Dataset URLs (these are placeholders - actual URLs require registration)
DATASET_URLS = {
    "ucf_crime": {
        "url": "https://www.crcv.ucf.edu/projects/real-world/",
        "note": "Requires registration at UCF. Download manually.",
        "size": "~15GB"
    },
    "xd_violence": {
        "url": "https://roc-ng.github.io/XD-Violence/",
        "note": "Available via Google Drive. Request access.",
        "size": "~25GB"
    }
}


def download_file(url: str, output_path: str, desc: str = "Downloading"):
    """Download file with progress bar."""
    response = requests.get(url, stream=True)
    total_size = int(response.headers.get("content-length", 0))
    
    with open(output_path, "wb") as f:
        with tqdm(total=total_size, unit="B", unit_scale=True, desc=desc) as pbar:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                pbar.update(len(chunk))


def extract_archive(archive_path: str, output_dir: str):
    """Extract zip or tar archive."""
    logger.info(f"Extracting {archive_path}...")
    
    if archive_path.endswith(".zip"):
        with zipfile.ZipFile(archive_path, "r") as zf:
            zf.extractall(output_dir)
    elif archive_path.endswith((".tar", ".tar.gz", ".tgz")):
        with tarfile.open(archive_path, "r:*") as tf:
            tf.extractall(output_dir)
    else:
        raise ValueError(f"Unknown archive format: {archive_path}")


def setup_ucf_crime(data_dir: Path, manual_path: Optional[str] = None):
    """
    Setup UCF-Crime dataset.
    
    UCF-Crime contains 1,900 untrimmed real-world surveillance videos
    with 13 anomaly classes.
    
    Args:
        data_dir: Target data directory
        manual_path: Path to manually downloaded archive
    """
    ucf_dir = data_dir / "ucf_crime"
    ucf_dir.mkdir(parents=True, exist_ok=True)
    
    if manual_path:
        logger.info(f"Using manually downloaded archive: {manual_path}")
        extract_archive(manual_path, str(ucf_dir))
    else:
        logger.info("UCF-Crime requires manual registration and download.")
        logger.info("Please follow these steps:")
        logger.info("1. Go to: https://www.crcv.ucf.edu/projects/real-world/")
        logger.info("2. Fill out the registration form")
        logger.info("3. Download the dataset")
        logger.info(f"4. Run: python download_datasets.py --dataset ucf_crime --manual-path <path_to_zip>")
        return False
    
    # Create splits
    create_splits(ucf_dir)
    
    # Create annotations template
    create_annotation_template(ucf_dir, "ucf_crime")
    
    logger.info(f"UCF-Crime setup complete at {ucf_dir}")
    return True


def setup_xd_violence(data_dir: Path, manual_path: Optional[str] = None):
    """
    Setup XD-Violence dataset.
    
    XD-Violence contains 4,754 untrimmed videos with audio-visual information
    and 6 violence categories.
    
    Args:
        data_dir: Target data directory
        manual_path: Path to manually downloaded archive
    """
    xd_dir = data_dir / "xd_violence"
    xd_dir.mkdir(parents=True, exist_ok=True)
    
    if manual_path:
        logger.info(f"Using manually downloaded archive: {manual_path}")
        extract_archive(manual_path, str(xd_dir))
    else:
        logger.info("XD-Violence requires requesting access.")
        logger.info("Please follow these steps:")
        logger.info("1. Go to: https://roc-ng.github.io/XD-Violence/")
        logger.info("2. Request access via the provided form")
        logger.info("3. Download via Google Drive")
        logger.info(f"4. Run: python download_datasets.py --dataset xd_violence --manual-path <path_to_archive>")
        return False
    
    # Create splits
    create_splits(xd_dir)
    
    # Create annotations template
    create_annotation_template(xd_dir, "xd_violence")
    
    logger.info(f"XD-Violence setup complete at {xd_dir}")
    return True


def create_splits(dataset_dir: Path):
    """Create train/val/test split directories."""
    for split in ["train", "val", "test"]:
        (dataset_dir / split).mkdir(exist_ok=True)
    
    # Create split info file
    split_info = {
        "train": 0.8,
        "val": 0.1,
        "test": 0.1,
        "note": "Videos should be distributed according to these ratios"
    }
    
    with open(dataset_dir / "split_info.json", "w") as f:
        json.dump(split_info, f, indent=2)


def create_annotation_template(dataset_dir: Path, dataset_name: str):
    """Create annotation template file."""
    
    # Template for annotations
    if dataset_name == "ucf_crime":
        classes = [
            "Abuse", "Arrest", "Arson", "Assault", "Burglary",
            "Explosion", "Fighting", "RoadAccidents", "Robbery",
            "Shooting", "Shoplifting", "Stealing", "Vandalism", "Normal"
        ]
    else:  # xd_violence
        classes = [
            "Fighting", "Shooting", "Riot", "Abuse",
            "CarAccident", "Explosion", "Normal"
        ]
    
    template = {
        "dataset": dataset_name,
        "classes": classes,
        "num_classes": len(classes),
        "annotations": {
            "example_video_id": {
                "label": 1,
                "class_name": classes[0] if len(classes) > 0 else "unknown",
                "anomaly_frames": [100, 200],  # [start, end]
                "caption": "Description of the anomaly event"
            }
        },
        "note": "Fill in annotations for each video"
    }
    
    with open(dataset_dir / "annotations_template.json", "w") as f:
        json.dump(template, f, indent=2)
    
    logger.info(f"Annotation template created at {dataset_dir / 'annotations_template.json'}")


def setup_mini_dataset(data_dir: Path):
    """
    Create a mini synthetic dataset for testing.
    Uses sample videos or generates dummy data.
    """
    mini_dir = data_dir / "mini_test"
    mini_dir.mkdir(parents=True, exist_ok=True)
    
    for split in ["train", "val", "test"]:
        split_dir = mini_dir / split
        split_dir.mkdir(exist_ok=True)
    
    # Create dummy annotation
    annotations = {
        "video_001": {"label": 1, "class_name": "Fighting", "caption": "Two people fighting"},
        "video_002": {"label": 0, "class_name": "Normal", "caption": "Normal activity"},
        "video_003": {"label": 1, "class_name": "Fire", "caption": "Fire in building"}
    }
    
    with open(mini_dir / "test_annotations.json", "w") as f:
        json.dump(annotations, f, indent=2)
    
    logger.info(f"Mini test dataset created at {mini_dir}")
    logger.info("Note: Add actual video files to test/ directory for testing")
    
    return True


def main():
    parser = argparse.ArgumentParser(description="Download and setup datasets")
    parser.add_argument(
        "--dataset",
        type=str,
        choices=["ucf_crime", "xd_violence", "mini", "all"],
        default="mini",
        help="Dataset to download"
    )
    parser.add_argument(
        "--data-dir",
        type=str,
        default="data/",
        help="Data directory"
    )
    parser.add_argument(
        "--manual-path",
        type=str,
        default=None,
        help="Path to manually downloaded archive"
    )
    
    args = parser.parse_args()
    data_dir = Path(args.data_dir)
    data_dir.mkdir(parents=True, exist_ok=True)
    
    if args.dataset == "ucf_crime" or args.dataset == "all":
        setup_ucf_crime(data_dir, args.manual_path)
    
    if args.dataset == "xd_violence" or args.dataset == "all":
        setup_xd_violence(data_dir, args.manual_path)
    
    if args.dataset == "mini":
        setup_mini_dataset(data_dir)
    
    logger.info("Dataset setup complete!")


if __name__ == "__main__":
    main()
