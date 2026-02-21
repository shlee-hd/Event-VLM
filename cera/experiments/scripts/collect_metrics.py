#!/usr/bin/env python3
"""
Collect per-run metrics and emit summary CSV files for CERA experiment handoff.
"""

from __future__ import annotations

import argparse
import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Dict, Iterable, List, Tuple


def is_number(value: object) -> bool:
    return isinstance(value, (int, float)) and not isinstance(value, bool)


def discover_runs(root: Path) -> List[Dict[str, object]]:
    runs: List[Dict[str, object]] = []
    for metrics_path in sorted(root.glob("*/*/seed_*/metrics.json")):
        seed_dir = metrics_path.parent
        if not seed_dir.name.startswith("seed_"):
            continue

        try:
            seed = int(seed_dir.name.replace("seed_", "", 1))
        except ValueError:
            continue

        setting = seed_dir.parent.name
        dataset = seed_dir.parent.parent.name
        metrics = json.loads(metrics_path.read_text(encoding="utf-8"))
        numeric_metrics = {
            key: float(value)
            for key, value in metrics.items()
            if is_number(value)
        }
        runs.append(
            {
                "dataset": dataset,
                "setting": setting,
                "seed": seed,
                "run_dir": str(seed_dir),
                "metrics": numeric_metrics,
            }
        )

    return runs


def write_runs_csv(runs: List[Dict[str, object]], path: Path) -> List[str]:
    metric_keys = sorted(
        {
            key
            for run in runs
            for key in run["metrics"].keys()  # type: ignore[index]
        }
    )
    fieldnames = ["dataset", "setting", "seed", "run_dir"] + metric_keys

    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for run in runs:
            row = {
                "dataset": run["dataset"],
                "setting": run["setting"],
                "seed": run["seed"],
                "run_dir": run["run_dir"],
            }
            row.update(run["metrics"])  # type: ignore[arg-type]
            writer.writerow(row)

    return metric_keys


def summarize(values: Iterable[float]) -> Tuple[float, float, int]:
    vals = list(values)
    n = len(vals)
    if n == 0:
        return float("nan"), float("nan"), 0
    mean = sum(vals) / n
    if n == 1:
        return mean, 0.0, 1
    var = sum((v - mean) ** 2 for v in vals) / (n - 1)
    return mean, math.sqrt(var), n


def write_summary_csv(
    runs: List[Dict[str, object]],
    metric_keys: List[str],
    long_path: Path,
    wide_path: Path,
) -> None:
    grouped: Dict[Tuple[str, str, str], List[float]] = defaultdict(list)
    for run in runs:
        dataset = str(run["dataset"])
        setting = str(run["setting"])
        metrics = run["metrics"]  # type: ignore[assignment]
        for key in metric_keys:
            if key in metrics:
                grouped[(dataset, setting, key)].append(float(metrics[key]))

    long_rows: List[Dict[str, object]] = []
    wide_rows: Dict[Tuple[str, str], Dict[str, object]] = {}

    for dataset, setting, metric in sorted(grouped.keys()):
        mean, std, n = summarize(grouped[(dataset, setting, metric)])
        long_rows.append(
            {
                "dataset": dataset,
                "setting": setting,
                "metric": metric,
                "mean": f"{mean:.6f}",
                "std": f"{std:.6f}",
                "n": n,
            }
        )
        key = (dataset, setting)
        if key not in wide_rows:
            wide_rows[key] = {"dataset": dataset, "setting": setting}
        wide_rows[key][f"{metric}_mean"] = f"{mean:.6f}"
        wide_rows[key][f"{metric}_std"] = f"{std:.6f}"

    long_fieldnames = ["dataset", "setting", "metric", "mean", "std", "n"]
    long_path.parent.mkdir(parents=True, exist_ok=True)
    with long_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=long_fieldnames)
        writer.writeheader()
        writer.writerows(long_rows)

    wide_fieldnames = ["dataset", "setting"]
    for metric in metric_keys:
        wide_fieldnames.append(f"{metric}_mean")
        wide_fieldnames.append(f"{metric}_std")

    with wide_path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=wide_fieldnames)
        writer.writeheader()
        for key in sorted(wide_rows.keys()):
            writer.writerow(wide_rows[key])


def write_summary_json(runs: List[Dict[str, object]], path: Path) -> None:
    payload = {
        "num_runs": len(runs),
        "datasets": sorted({str(run["dataset"]) for run in runs}),
        "settings": sorted({str(run["setting"]) for run in runs}),
    }
    path.write_text(json.dumps(payload, indent=2), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Collect and summarize experiment metrics")
    parser.add_argument("--root", type=str, required=True, help="Root directory of run outputs")
    parser.add_argument(
        "--kind",
        type=str,
        choices=["main", "ablation"],
        required=True,
        help="Prefix used for output file naming",
    )
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    root = Path(args.root)
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    runs = discover_runs(root)
    runs_csv = out_dir / f"{args.kind}_runs.csv"
    metric_keys = write_runs_csv(runs, runs_csv)

    summary_csv = out_dir / f"{args.kind}_summary.csv"
    summary_wide_csv = out_dir / f"{args.kind}_summary_wide.csv"
    write_summary_csv(runs, metric_keys, summary_csv, summary_wide_csv)

    summary_json = out_dir / f"{args.kind}_summary_meta.json"
    write_summary_json(runs, summary_json)

    print(f"Collected runs: {len(runs)}")
    print(f"Saved runs CSV: {runs_csv}")
    print(f"Saved summary CSV: {summary_csv}")
    print(f"Saved wide summary CSV: {summary_wide_csv}")
    print(f"Saved summary meta: {summary_json}")


if __name__ == "__main__":
    main()

