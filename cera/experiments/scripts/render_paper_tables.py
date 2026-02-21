#!/usr/bin/env python3
"""
Render paper-table stubs from summary CSV artifacts.
"""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from typing import Dict


def read_summary_csv(path: Path) -> Dict[str, Dict[str, Dict[str, float]]]:
    data: Dict[str, Dict[str, Dict[str, float]]] = defaultdict(lambda: defaultdict(dict))
    if not path.exists():
        return data

    with path.open("r", encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        for row in reader:
            dataset = row["dataset"]
            setting = row["setting"]
            metric = row["metric"]
            mean = float(row["mean"])
            data[dataset][setting][metric] = mean
    return data


def main() -> None:
    parser = argparse.ArgumentParser(description="Render paper table stubs from summary CSV")
    parser.add_argument("--main-summary", type=str, required=True, help="Path to main_summary.csv")
    parser.add_argument(
        "--ablation-summary",
        type=str,
        default=None,
        help="Path to ablation_summary.csv (optional)",
    )
    parser.add_argument("--out-dir", type=str, required=True, help="Output directory")
    args = parser.parse_args()

    main_data = read_summary_csv(Path(args.main_summary))
    ablation_data = (
        read_summary_csv(Path(args.ablation_summary))
        if args.ablation_summary
        else defaultdict(lambda: defaultdict(dict))
    )

    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    md_lines = []
    md_lines.append("# Paper Table Stub (Measured Replacement)")
    md_lines.append("")
    md_lines.append("## Main comparison stub")
    md_lines.append("")
    md_lines.append("| Dataset | Setting | AUC | AP | FPS | Token Reduction |")
    md_lines.append("|---|---|---:|---:|---:|---:|")

    tex_lines = []
    tex_lines.append("% Auto-generated table stub from measured summaries")
    tex_lines.append("\\begin{tabular}{llcccc}")
    tex_lines.append("\\toprule")
    tex_lines.append("Dataset & Setting & AUC & AP & FPS & TokenRed \\\\")
    tex_lines.append("\\midrule")

    for dataset in sorted(main_data.keys()):
        for setting in sorted(main_data[dataset].keys()):
            metrics = main_data[dataset][setting]
            auc = metrics.get("auc", float("nan"))
            ap = metrics.get("ap", float("nan"))
            fps = metrics.get("fps", float("nan"))
            tr = metrics.get("token_reduction", float("nan"))
            md_lines.append(
                f"| {dataset} | {setting} | {auc:.4f} | {ap:.4f} | {fps:.4f} | {tr:.4f} |"
            )
            tex_lines.append(
                f"{dataset} & {setting} & {auc:.4f} & {ap:.4f} & {fps:.4f} & {tr:.4f} \\\\"
            )

    tex_lines.append("\\bottomrule")
    tex_lines.append("\\end{tabular}")

    if ablation_data:
        md_lines.append("")
        md_lines.append("## Ablation stub")
        md_lines.append("")
        md_lines.append("| Dataset | Ablation | AUC | AP | FPS |")
        md_lines.append("|---|---|---:|---:|---:|")
        for dataset in sorted(ablation_data.keys()):
            for setting in sorted(ablation_data[dataset].keys()):
                metrics = ablation_data[dataset][setting]
                auc = metrics.get("auc", float("nan"))
                ap = metrics.get("ap", float("nan"))
                fps = metrics.get("fps", float("nan"))
                md_lines.append(
                    f"| {dataset} | {setting} | {auc:.4f} | {ap:.4f} | {fps:.4f} |"
                )

    md_path = out_dir / "paper_table_stub.md"
    tex_path = out_dir / "paper_table_stub.tex"
    md_path.write_text("\n".join(md_lines) + "\n", encoding="utf-8")
    tex_path.write_text("\n".join(tex_lines) + "\n", encoding="utf-8")

    print(f"Saved markdown stub: {md_path}")
    print(f"Saved latex stub: {tex_path}")


if __name__ == "__main__":
    main()

