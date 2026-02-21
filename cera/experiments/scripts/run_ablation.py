#!/usr/bin/env python3
"""
Run CERA ablation matrix for supported settings and emit a manifest for pending ones.
"""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Callable, Dict, List

# Add project root to path.
import sys

REPO_ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(REPO_ROOT))


def apply_full(config: object) -> None:
    return


def apply_no_event_gating(config: object) -> None:
    # Proxy for removing gating in current runtime.
    # typing note: config is runtime-loaded structured object.
    config.detector.conf_threshold = 0.0


def apply_no_token_compaction(config: object) -> None:
    config.pruning.enabled = False


def apply_no_budgeted_decoding(config: object) -> None:
    # Proxy for denser decoding in the current runtime.
    config.vlm.max_new_tokens = max(config.vlm.max_new_tokens, 512)
    config.vlm.prompt_strategy = "standard"


SUPPORTED_ABLATIONS: Dict[str, Callable[[object], None]] = {
    "full": apply_full,
    "no_event_gating": apply_no_event_gating,
    "no_token_compaction": apply_no_token_compaction,
    "no_budgeted_decoding": apply_no_budgeted_decoding,
}

UNSUPPORTED_ABLATIONS: Dict[str, str] = {
    "no_evidence_gate": "pending_runtime_support",
}

DATASET_CONFIG_MAP = {
    "ucf_crime": "experiments/configs/ucf_crime.yaml",
    "xd_violence": "experiments/configs/xd_violence.yaml",
}


def parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def run(args: argparse.Namespace) -> None:
    output_root = Path(args.output_root)
    output_root.mkdir(parents=True, exist_ok=True)

    seeds = [int(seed) for seed in parse_csv(args.seeds)]
    datasets = parse_csv(args.datasets)
    run_rows: List[Dict[str, str]] = []

    evaluate = None
    load_config = None
    if args.execute_supported:
        # Lazy imports: allow manifest-only mode without full ML dependencies.
        from experiments.evaluate import evaluate as _evaluate  # noqa: WPS433
        from src.config import load_config as _load_config  # noqa: WPS433

        evaluate = _evaluate
        load_config = _load_config

    for dataset in datasets:
        if dataset not in DATASET_CONFIG_MAP:
            raise ValueError(f"Unsupported dataset: {dataset}")
        config_path = REPO_ROOT / DATASET_CONFIG_MAP[dataset]

        for ablation_name, mutator in SUPPORTED_ABLATIONS.items():
            for seed in seeds:
                run_dir = output_root / dataset / ablation_name / f"seed_{seed}"
                run_dir.mkdir(parents=True, exist_ok=True)
                row = {
                    "dataset": dataset,
                    "ablation": ablation_name,
                    "seed": str(seed),
                    "status": "completed",
                    "reason": "",
                    "output_dir": str(run_dir),
                }

                if args.execute_supported:
                    try:
                        assert load_config is not None
                        assert evaluate is not None
                        config = load_config(str(config_path))
                        config.device = args.device
                        config.seed = seed
                        # Keep ablation baseline anchored to YOLO profile.
                        config.detector.model = "yolov8n"
                        mutator(config)
                        evaluate(
                            config=config,
                            output_dir=str(run_dir),
                            quick=args.quick,
                            max_videos=args.max_videos,
                        )
                    except Exception as exc:  # pragma: no cover (runtime failure path)
                        row["status"] = "failed"
                        row["reason"] = str(exc)
                else:
                    row["status"] = "planned"
                    row["reason"] = "execute_supported=0"

                run_rows.append(row)

        for ablation_name, reason in UNSUPPORTED_ABLATIONS.items():
            for seed in seeds:
                run_dir = output_root / dataset / ablation_name / f"seed_{seed}"
                run_dir.mkdir(parents=True, exist_ok=True)
                run_rows.append(
                    {
                        "dataset": dataset,
                        "ablation": ablation_name,
                        "seed": str(seed),
                        "status": "pending_runtime_support",
                        "reason": reason,
                        "output_dir": str(run_dir),
                    }
                )

    manifest_csv = output_root / "ablation_manifest.csv"
    fieldnames = ["dataset", "ablation", "seed", "status", "reason", "output_dir"]
    with manifest_csv.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(run_rows)

    manifest_json = output_root / "ablation_manifest.json"
    manifest_json.write_text(json.dumps(run_rows, indent=2), encoding="utf-8")

    print(f"Saved ablation manifest: {manifest_csv}")
    print(f"Saved ablation manifest: {manifest_json}")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run CERA ablation matrix")
    parser.add_argument(
        "--output-root",
        type=str,
        default=str(REPO_ROOT / "cera/experiments/results/ablation"),
        help="Output root directory",
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default="41,42,43",
        help="Comma-separated seeds",
    )
    parser.add_argument(
        "--datasets",
        type=str,
        default="ucf_crime,xd_violence",
        help="Comma-separated datasets",
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Device override",
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode for evaluate()",
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Max videos per run",
    )
    parser.add_argument(
        "--execute-supported",
        type=int,
        choices=[0, 1],
        default=1,
        help="Whether to execute supported ablations (1) or write plan only (0)",
    )
    args = parser.parse_args()
    args.execute_supported = bool(args.execute_supported)
    run(args)


if __name__ == "__main__":
    main()
