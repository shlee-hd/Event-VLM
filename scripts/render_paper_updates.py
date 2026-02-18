#!/usr/bin/env python3
"""
Render paper-ready LaTeX tables from multi-seed and significance outputs.

Inputs:
- multi_seed summary: <multi-seed-root>/summary.json
- significance files:
  <multi-seed-root>/significance/<dataset>/<candidate>_vs_<baseline>/significance.json

Outputs (default under paper/generated):
- table_multiseed_overview.tex
- table_significance_summary.tex
"""

import argparse
import json
from pathlib import Path
from statistics import median
from typing import Dict, Any, List


def fmt_pm(entry: Dict[str, Any], digits: int = 3) -> str:
    if not entry:
        return "--"
    mean = entry.get("mean")
    ci95 = entry.get("ci95")
    if mean is None or ci95 is None:
        return "--"
    return f"{mean:.{digits}f} $\\pm$ {ci95:.{digits}f}"


def fmt_delta(mean: float, std: float, digits: int = 3) -> str:
    if mean is None or std is None:
        return "--"
    return f"{mean:.{digits}f} $\\pm$ {std:.{digits}f}"


def latex_escape(text: str) -> str:
    return text.replace("_", "\\_")


def load_json(path: Path) -> Dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def render_multiseed_table(summary: Dict[str, Any]) -> str:
    lines: List[str] = []
    lines.append("\\begin{table}[t]")
    lines.append("\\caption{\\textbf{Auto-Generated Multi-Seed Overview.} Mean $\\pm$ 95\\% CI from server-side runs under the unified protocol.}")
    lines.append("\\label{tab:auto_multiseed_overview}")
    lines.append("\\centering")
    lines.append("\\setlength{\\tabcolsep}{4pt}")
    lines.append("\\begin{tabular}{l|lccc}")
    lines.append("\\toprule")
    lines.append("\\textbf{Dataset} & \\textbf{Variant} & \\textbf{AUC} & \\textbf{CIDEr} & \\textbf{FPS} \\\\")
    lines.append("\\midrule")

    dataset_summary = summary.get("summary", {})
    for dataset in sorted(dataset_summary.keys()):
        variants = dataset_summary[dataset]
        if not isinstance(variants, dict):
            continue
        ordered = ["none", "core", "full"]
        seen = set()
        for variant in ordered + sorted(variants.keys()):
            if variant in seen or variant not in variants:
                continue
            seen.add(variant)
            row = variants[variant]
            auc = fmt_pm(row.get("auc", {}))
            cider = fmt_pm(row.get("CIDEr", {}))
            fps = fmt_pm(row.get("fps", {}))
            lines.append(
                f"{latex_escape(dataset)} & {latex_escape(variant)} & {auc} & {cider} & {fps} \\\\"
            )
        lines.append("\\midrule")

    if lines[-1] == "\\midrule":
        lines.pop()

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    lines.append("")
    return "\n".join(lines)


def render_significance_table(
    multi_seed_root: Path,
    datasets: List[str],
    baseline: str,
    candidates: List[str],
) -> str:
    lines: List[str] = []
    lines.append("\\begin{table}[t]")
    lines.append("\\caption{\\textbf{Auto-Generated Paired Significance Summary.} Candidate variants are compared against the baseline using paired bootstrap/permutation analysis on per-video anomaly scores.}")
    lines.append("\\label{tab:auto_significance_summary}")
    lines.append("\\centering")
    lines.append("\\setlength{\\tabcolsep}{4pt}")
    lines.append("\\begin{tabular}{l|lcccc}")
    lines.append("\\toprule")
    lines.append("\\textbf{Dataset} & \\textbf{Compare} & $\\Delta$AUC & $\\Delta$AP & $p_{AUC}$ & $p_{AP}$ \\\\")
    lines.append("\\midrule")

    has_any = False
    for dataset in datasets:
        for candidate in candidates:
            if candidate == baseline:
                continue
            sig_path = (
                multi_seed_root
                / "significance"
                / dataset
                / f"{candidate}_vs_{baseline}"
                / "significance.json"
            )
            if not sig_path.exists():
                lines.append(
                    f"{latex_escape(dataset)} & {latex_escape(candidate)} vs {latex_escape(baseline)} & -- & -- & -- & -- \\\\"
                )
                continue

            payload = load_json(sig_path)
            summary = payload.get("summary", {})
            runs = payload.get("runs", [])
            auc_delta = summary.get("auc_delta", {})
            ap_delta = summary.get("ap_delta", {})

            auc_p_vals = [r.get("auc", {}).get("p_value") for r in runs if r.get("auc", {}).get("p_value") is not None]
            ap_p_vals = [r.get("ap", {}).get("p_value") for r in runs if r.get("ap", {}).get("p_value") is not None]
            auc_p = f"{median(auc_p_vals):.4f}" if auc_p_vals else "--"
            ap_p = f"{median(ap_p_vals):.4f}" if ap_p_vals else "--"

            auc_text = fmt_delta(auc_delta.get("mean"), auc_delta.get("std"))
            ap_text = fmt_delta(ap_delta.get("mean"), ap_delta.get("std"))

            lines.append(
                f"{latex_escape(dataset)} & {latex_escape(candidate)} vs {latex_escape(baseline)} & {auc_text} & {ap_text} & {auc_p} & {ap_p} \\\\"
            )
            has_any = True

    if not has_any:
        lines.append("N/A & N/A & -- & -- & -- & -- \\\\")

    lines.append("\\bottomrule")
    lines.append("\\end{tabular}")
    lines.append("\\end{table}")
    lines.append("")
    return "\n".join(lines)


def parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def main() -> None:
    parser = argparse.ArgumentParser(description="Render paper LaTeX tables from experiment outputs")
    parser.add_argument("--multi-seed-root", type=str, required=True, help="Path containing summary.json and significance/")
    parser.add_argument("--output-dir", type=str, default="paper/generated", help="Output directory for generated .tex files")
    parser.add_argument("--datasets", type=str, default="ucf_crime,xd_violence,shanghaitech", help="Comma-separated dataset names")
    parser.add_argument("--baseline", type=str, default="none", help="Baseline variant used in significance reports")
    parser.add_argument("--candidates", type=str, default="core,full", help="Comma-separated candidate variants")
    args = parser.parse_args()

    multi_seed_root = Path(args.multi_seed_root)
    summary_path = multi_seed_root / "summary.json"
    if not summary_path.exists():
        raise FileNotFoundError(f"Missing summary file: {summary_path}")

    summary = load_json(summary_path)
    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    multiseed_tex = render_multiseed_table(summary)
    sig_tex = render_significance_table(
        multi_seed_root=multi_seed_root,
        datasets=parse_csv(args.datasets),
        baseline=args.baseline,
        candidates=parse_csv(args.candidates),
    )

    table1 = out_dir / "table_multiseed_overview.tex"
    table2 = out_dir / "table_significance_summary.tex"
    table1.write_text(multiseed_tex, encoding="utf-8")
    table2.write_text(sig_tex, encoding="utf-8")

    print(f"Generated: {table1}")
    print(f"Generated: {table2}")


if __name__ == "__main__":
    main()
