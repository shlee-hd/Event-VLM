#!/usr/bin/env python3
"""
Run multi-seed evaluation and aggregate mean/std/CI outputs.

Example:
python experiments/multi_seed_eval.py \
  --configs experiments/configs/ucf_crime.yaml experiments/configs/xd_violence.yaml \
  --seeds 41,42,43 \
  --variants core,full \
  --output-dir outputs/multi_seed_eval
"""

import argparse
import json
import math
from pathlib import Path
from typing import Dict, List, Any

import numpy as np

# Add project root to path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))


PROMPT_STRATEGY_MAP = {
    "core": "standard",
    "full": "hazard_priority",
    "none": "none",
    "standard": "standard",
    "hazard_priority": "hazard_priority",
}


def parse_csv(value: str) -> List[str]:
    """Parse comma-separated argument into a clean list."""
    return [item.strip() for item in value.split(",") if item.strip()]


def summarize(values: List[float]) -> Dict[str, float]:
    """Return mean/std/95% normal CI radius for a scalar metric."""
    n = len(values)
    if n == 0:
        return {"mean": 0.0, "std": 0.0, "ci95": 0.0, "n": 0}

    arr = np.array(values, dtype=float)
    mean = float(arr.mean())
    std = float(arr.std(ddof=1)) if n > 1 else 0.0
    ci95 = float(1.96 * std / math.sqrt(n)) if n > 1 else 0.0
    return {"mean": mean, "std": std, "ci95": ci95, "n": n}


def aggregate_metrics(run_metrics: List[Dict[str, float]]) -> Dict[str, Dict[str, float]]:
    """Aggregate numeric metrics across seed runs."""
    keys = set()
    for metrics in run_metrics:
        for key, value in metrics.items():
            if isinstance(value, (int, float)):
                keys.add(key)

    summary = {}
    for key in sorted(keys):
        values = [float(metrics[key]) for metrics in run_metrics if key in metrics]
        summary[key] = summarize(values)
    return summary


def format_ci(entry: Dict[str, float]) -> str:
    """Format mean ± CI display string."""
    return f"{entry['mean']:.4f} +/- {entry['ci95']:.4f}"


def write_markdown_report(
    summary_payload: Dict[str, Any],
    report_path: Path,
    focus_metrics: List[str]
) -> None:
    """Write compact markdown summary for paper-table updates."""
    lines = []
    lines.append("# Multi-seed Evaluation Summary")
    lines.append("")
    lines.append("## Settings")
    lines.append(f"- Seeds: {summary_payload['meta']['seeds']}")
    lines.append(f"- Variants: {summary_payload['meta']['variants']}")
    lines.append(f"- Detector: {summary_payload['meta']['detector']}")
    lines.append(f"- Device: {summary_payload['meta']['device']}")
    lines.append("")

    for dataset, variant_dict in summary_payload["summary"].items():
        lines.append(f"## {dataset}")
        lines.append("")
        lines.append("| Variant | " + " | ".join(focus_metrics) + " |")
        lines.append("|---|" + "|".join(["---"] * len(focus_metrics)) + "|")
        for variant, stats in variant_dict.items():
            row = [variant]
            for metric in focus_metrics:
                if metric in stats:
                    row.append(format_ci(stats[metric]))
                else:
                    row.append("-")
            lines.append("| " + " | ".join(row) + " |")
        lines.append("")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Run multi-seed Event-VLM evaluation")
    parser.add_argument(
        "--configs",
        nargs="+",
        default=["experiments/configs/ucf_crime.yaml", "experiments/configs/xd_violence.yaml"],
        help="List of dataset config files"
    )
    parser.add_argument(
        "--seeds",
        type=str,
        default="41,42,43",
        help="Comma-separated seed list"
    )
    parser.add_argument(
        "--variants",
        type=str,
        default="core,full",
        help="Comma-separated variant list (core/full/none)"
    )
    parser.add_argument(
        "--detector",
        type=str,
        default="detr-l",
        help="Detector override (detr-l/yolov8s/yolov8n)"
    )
    parser.add_argument(
        "--device",
        type=str,
        default="cuda",
        help="Device to run on"
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="outputs/multi_seed_eval",
        help="Output directory"
    )
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode with fewer videos"
    )
    parser.add_argument(
        "--max-videos",
        type=int,
        default=None,
        help="Maximum videos to evaluate"
    )
    args = parser.parse_args()

    # Lazy import so `--help` works even before heavy ML deps are installed.
    from src.config import load_config
    from experiments.evaluate import evaluate

    seeds = [int(seed) for seed in parse_csv(args.seeds)]
    variants = parse_csv(args.variants)
    output_root = Path(args.output_dir)
    output_root.mkdir(parents=True, exist_ok=True)

    summary_payload: Dict[str, Any] = {
        "meta": {
            "seeds": seeds,
            "variants": variants,
            "detector": args.detector,
            "device": args.device,
            "quick": args.quick,
            "max_videos": args.max_videos,
        },
        "runs": [],
        "summary": {},
    }

    for config_path in args.configs:
        dataset_name = Path(config_path).stem
        summary_payload["summary"][dataset_name] = {}

        for variant in variants:
            if variant not in PROMPT_STRATEGY_MAP:
                raise ValueError(
                    f"Unknown variant '{variant}'. "
                    f"Supported: {sorted(PROMPT_STRATEGY_MAP.keys())}"
                )

            variant_runs = []
            for seed in seeds:
                config = load_config(config_path)
                config.device = args.device
                config.seed = seed
                config.detector.model = args.detector
                config.vlm.prompt_strategy = PROMPT_STRATEGY_MAP[variant]

                run_dir = output_root / dataset_name / variant / f"seed_{seed}"
                run_dir.mkdir(parents=True, exist_ok=True)

                metrics = evaluate(
                    config=config,
                    output_dir=str(run_dir),
                    quick=args.quick,
                    max_videos=args.max_videos
                )
                variant_runs.append(metrics)
                summary_payload["runs"].append(
                    {
                        "dataset": dataset_name,
                        "variant": variant,
                        "seed": seed,
                        "metrics": metrics,
                        "output_dir": str(run_dir),
                    }
                )

            summary_payload["summary"][dataset_name][variant] = aggregate_metrics(variant_runs)

    summary_path = output_root / "summary.json"
    summary_path.write_text(json.dumps(summary_payload, indent=2), encoding="utf-8")

    report_path = output_root / "summary.md"
    write_markdown_report(
        summary_payload=summary_payload,
        report_path=report_path,
        focus_metrics=["auc", "CIDEr", "fps", "recall@trigger"],
    )

    print(f"Saved summary JSON: {summary_path}")
    print(f"Saved summary report: {report_path}")


if __name__ == "__main__":
    main()
