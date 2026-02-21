#!/usr/bin/env python3
"""
Generate deterministic dummy run outputs for offline pipeline verification.
"""

from __future__ import annotations

import argparse
import json
import random
from pathlib import Path
from typing import Dict, List


BASE_METRICS = {
    "yolo": {"auc": 0.782, "ap": 0.635, "fps": 11.5, "token_reduction": 0.64, "recall@trigger": 0.86},
    "detr": {"auc": 0.809, "ap": 0.662, "fps": 6.7, "token_reduction": 0.52, "recall@trigger": 0.88},
}

DATASET_SHIFT = {
    "ucf_crime": 0.0,
    "xd_violence": 0.015,
}


def parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def seeded_rng(*values: object) -> random.Random:
    return random.Random(hash(values) & 0xFFFFFFFF)


def build_metrics(dataset: str, profile: str, seed: int) -> Dict[str, float]:
    base = BASE_METRICS[profile]
    shift = DATASET_SHIFT[dataset]
    rng = seeded_rng("metrics", dataset, profile, seed)
    noise = lambda s: (rng.random() - 0.5) * s
    return {
        "auc": base["auc"] + shift + noise(0.02),
        "ap": base["ap"] + shift + noise(0.02),
        "fps": max(0.1, base["fps"] + noise(0.8)),
        "token_reduction": min(0.99, max(0.01, base["token_reduction"] + noise(0.04))),
        "recall@trigger": min(0.99, max(0.01, base["recall@trigger"] + noise(0.03))),
    }


def build_predictions(dataset: str, profile: str, seed: int, n_videos: int) -> List[Dict[str, object]]:
    label_rng = seeded_rng("labels", dataset, seed)
    score_rng = seeded_rng("scores", dataset, profile, seed)
    preds = []
    for i in range(n_videos):
        label = 1 if label_rng.random() < 0.3 else 0
        base_pos = 0.72 if profile == "detr" else 0.66
        base_neg = 0.34 if profile == "detr" else 0.38
        score = (base_pos if label == 1 else base_neg) + (score_rng.random() - 0.5) * 0.25
        score = min(0.999, max(0.001, score))
        preds.append(
            {
                "id": f"{dataset}_video_{i:04d}",
                "label": label,
                "score": score,
                "triggered": score > 0.5,
                "caption": "",
            }
        )
    return preds


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate deterministic dummy outputs")
    parser.add_argument(
        "--output-root",
        type=str,
        required=True,
        help="Output root (e.g., cera/experiments/results/main_dummy)",
    )
    parser.add_argument("--seeds", type=str, default="41,42,43")
    parser.add_argument("--datasets", type=str, default="ucf_crime,xd_violence")
    parser.add_argument("--profiles", type=str, default="yolo,detr")
    parser.add_argument("--videos", type=int, default=120)
    args = parser.parse_args()

    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    seeds = [int(x) for x in parse_csv(args.seeds)]
    datasets = parse_csv(args.datasets)
    profiles = parse_csv(args.profiles)

    count = 0
    for dataset in datasets:
        for profile in profiles:
            if profile not in BASE_METRICS:
                raise ValueError(f"Unsupported profile: {profile}")
            for seed in seeds:
                run_dir = output_root / dataset / profile / f"seed_{seed}"
                run_dir.mkdir(parents=True, exist_ok=True)
                metrics = build_metrics(dataset, profile, seed)
                predictions = build_predictions(dataset, profile, seed, args.videos)
                (run_dir / "metrics.json").write_text(
                    json.dumps(metrics, indent=2), encoding="utf-8"
                )
                (run_dir / "predictions.json").write_text(
                    json.dumps(predictions, indent=2), encoding="utf-8"
                )
                count += 1

    print(f"Generated dummy runs: {count}")
    print(f"Output root: {output_root}")


if __name__ == "__main__":
    main()

