#!/usr/bin/env python3
"""
Paired significance analysis for Event-VLM anomaly metrics.

Compares two variants (e.g., none vs core, none vs full) on aligned per-video
predictions from multi-seed runs and reports:
- observed delta (candidate - baseline) for AUC/AP,
- paired bootstrap CI,
- paired permutation p-value.
"""

import argparse
import json
from pathlib import Path
from typing import Dict, List, Tuple, Any

import numpy as np
from sklearn.metrics import average_precision_score, roc_auc_score


def parse_csv(value: str) -> List[str]:
    return [item.strip() for item in value.split(",") if item.strip()]


def safe_auc(labels: np.ndarray, scores: np.ndarray) -> float:
    if labels.size == 0 or len(np.unique(labels)) < 2:
        return float("nan")
    return float(roc_auc_score(labels, scores))


def safe_ap(labels: np.ndarray, scores: np.ndarray) -> float:
    if labels.size == 0 or len(np.unique(labels)) < 2:
        return float("nan")
    return float(average_precision_score(labels, scores))


def load_predictions(path: Path) -> Dict[str, Dict[str, Any]]:
    raw = json.loads(path.read_text(encoding="utf-8"))
    result: Dict[str, Dict[str, Any]] = {}
    for item in raw:
        if "id" not in item:
            continue
        result[str(item["id"])] = item
    return result


def align_seed_predictions(
    base_path: Path,
    cand_path: Path,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray]:
    base = load_predictions(base_path)
    cand = load_predictions(cand_path)
    common_ids = sorted(set(base.keys()) & set(cand.keys()))

    labels = []
    base_scores = []
    cand_scores = []
    for vid in common_ids:
        b = base[vid]
        c = cand[vid]
        if "label" not in b or "score" not in b or "score" not in c:
            continue
        labels.append(int(b["label"]))
        base_scores.append(float(b["score"]))
        cand_scores.append(float(c["score"]))

    return (
        np.asarray(labels, dtype=np.int64),
        np.asarray(base_scores, dtype=np.float64),
        np.asarray(cand_scores, dtype=np.float64),
    )


def bootstrap_delta(
    labels: np.ndarray,
    base_scores: np.ndarray,
    cand_scores: np.ndarray,
    metric_fn,
    n_iter: int,
    seed: int,
) -> Dict[str, float]:
    rng = np.random.default_rng(seed)
    n = labels.shape[0]
    if n == 0:
        return {"mean": float("nan"), "ci_low": float("nan"), "ci_high": float("nan")}

    observed = metric_fn(labels, cand_scores) - metric_fn(labels, base_scores)

    samples = []
    for _ in range(n_iter):
        idx = rng.integers(0, n, size=n)
        lb = labels[idx]
        bs = base_scores[idx]
        cs = cand_scores[idx]
        delta = metric_fn(lb, cs) - metric_fn(lb, bs)
        if np.isnan(delta):
            continue
        samples.append(delta)

    if not samples:
        return {"mean": float(observed), "ci_low": float("nan"), "ci_high": float("nan")}

    arr = np.asarray(samples, dtype=np.float64)
    return {
        "mean": float(observed),
        "ci_low": float(np.percentile(arr, 2.5)),
        "ci_high": float(np.percentile(arr, 97.5)),
    }


def paired_permutation_pvalue(
    labels: np.ndarray,
    base_scores: np.ndarray,
    cand_scores: np.ndarray,
    metric_fn,
    n_iter: int,
    seed: int,
) -> float:
    rng = np.random.default_rng(seed)
    n = labels.shape[0]
    if n == 0:
        return float("nan")

    observed = metric_fn(labels, cand_scores) - metric_fn(labels, base_scores)
    if np.isnan(observed):
        return float("nan")

    extreme = 0
    valid = 0
    for _ in range(n_iter):
        swap = rng.integers(0, 2, size=n, dtype=np.int64).astype(bool)
        perm_base = np.where(swap, cand_scores, base_scores)
        perm_cand = np.where(swap, base_scores, cand_scores)
        delta = metric_fn(labels, perm_cand) - metric_fn(labels, perm_base)
        if np.isnan(delta):
            continue
        valid += 1
        if abs(delta) >= abs(observed):
            extreme += 1

    if valid == 0:
        return float("nan")
    return float((extreme + 1) / (valid + 1))


def summarize_runs(rows: List[Dict[str, Any]]) -> Dict[str, float]:
    auc_deltas = [row["auc"]["delta"] for row in rows if not np.isnan(row["auc"]["delta"])]
    ap_deltas = [row["ap"]["delta"] for row in rows if not np.isnan(row["ap"]["delta"])]

    def _stat(vals: List[float]) -> Dict[str, float]:
        if not vals:
            return {"mean": float("nan"), "std": float("nan"), "n": 0}
        arr = np.asarray(vals, dtype=np.float64)
        std = float(arr.std(ddof=1)) if arr.size > 1 else 0.0
        return {"mean": float(arr.mean()), "std": std, "n": int(arr.size)}

    return {
        "auc_delta": _stat(auc_deltas),
        "ap_delta": _stat(ap_deltas),
    }


def write_markdown(report: Dict[str, Any], path: Path) -> None:
    lines: List[str] = []
    meta = report["meta"]

    lines.append("# Paired Significance Report")
    lines.append("")
    lines.append("## Settings")
    lines.append(f"- Dataset: {meta['dataset']}")
    lines.append(f"- Baseline variant: {meta['baseline_variant']}")
    lines.append(f"- Candidate variant: {meta['candidate_variant']}")
    lines.append(f"- Seeds: {meta['seeds']}")
    lines.append(f"- Bootstrap iters: {meta['bootstrap_iters']}")
    lines.append(f"- Permutation iters: {meta['perm_iters']}")
    lines.append("")

    lines.append("## Per-seed Results")
    lines.append("")
    lines.append("| Seed | N | AUC Delta | AUC 95% CI | AUC p-value | AP Delta | AP 95% CI | AP p-value |")
    lines.append("|---|---:|---:|---|---:|---:|---|---:|")
    for row in report["runs"]:
        auc_ci = f"[{row['auc']['ci_low']:.4f}, {row['auc']['ci_high']:.4f}]"
        ap_ci = f"[{row['ap']['ci_low']:.4f}, {row['ap']['ci_high']:.4f}]"
        lines.append(
            "| "
            f"{row['seed']} | {row['n_samples']} | "
            f"{row['auc']['delta']:.4f} | {auc_ci} | {row['auc']['p_value']:.4f} | "
            f"{row['ap']['delta']:.4f} | {ap_ci} | {row['ap']['p_value']:.4f} |"
        )

    lines.append("")
    lines.append("## Aggregated Delta Across Seeds")
    lines.append("")
    lines.append(
        f"- AUC delta mean/std (n={report['summary']['auc_delta']['n']}): "
        f"{report['summary']['auc_delta']['mean']:.4f} / {report['summary']['auc_delta']['std']:.4f}"
    )
    lines.append(
        f"- AP delta mean/std (n={report['summary']['ap_delta']['n']}): "
        f"{report['summary']['ap_delta']['mean']:.4f} / {report['summary']['ap_delta']['std']:.4f}"
    )
    lines.append("")

    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Paired significance for Event-VLM metrics")
    parser.add_argument("--multi-seed-root", type=str, required=True, help="Root of multi-seed output")
    parser.add_argument("--dataset", type=str, required=True, help="Dataset folder name (e.g., ucf_crime)")
    parser.add_argument("--baseline-variant", type=str, default="none", help="Baseline variant folder")
    parser.add_argument("--candidate-variant", type=str, default="core", help="Candidate variant folder")
    parser.add_argument("--seeds", type=str, default="41,42,43", help="Comma-separated seed list")
    parser.add_argument("--bootstrap-iters", type=int, default=5000, help="Bootstrap iterations")
    parser.add_argument("--perm-iters", type=int, default=5000, help="Permutation iterations")
    parser.add_argument("--output-dir", type=str, default=None, help="Output dir for report files")
    args = parser.parse_args()

    root = Path(args.multi_seed_root)
    seeds = [int(s) for s in parse_csv(args.seeds)]

    if args.output_dir:
        out_dir = Path(args.output_dir)
    else:
        out_dir = root / "significance" / args.dataset / f"{args.candidate_variant}_vs_{args.baseline_variant}"
    out_dir.mkdir(parents=True, exist_ok=True)

    runs: List[Dict[str, Any]] = []
    for seed in seeds:
        base_path = root / args.dataset / args.baseline_variant / f"seed_{seed}" / "predictions.json"
        cand_path = root / args.dataset / args.candidate_variant / f"seed_{seed}" / "predictions.json"
        if not base_path.exists() or not cand_path.exists():
            raise FileNotFoundError(
                f"Missing predictions for seed={seed}: "
                f"{base_path} or {cand_path}"
            )

        labels, base_scores, cand_scores = align_seed_predictions(base_path, cand_path)

        auc_delta = safe_auc(labels, cand_scores) - safe_auc(labels, base_scores)
        auc_boot = bootstrap_delta(
            labels,
            base_scores,
            cand_scores,
            metric_fn=safe_auc,
            n_iter=args.bootstrap_iters,
            seed=seed + 1000,
        )
        auc_p = paired_permutation_pvalue(
            labels,
            base_scores,
            cand_scores,
            metric_fn=safe_auc,
            n_iter=args.perm_iters,
            seed=seed + 2000,
        )

        ap_delta = safe_ap(labels, cand_scores) - safe_ap(labels, base_scores)
        ap_boot = bootstrap_delta(
            labels,
            base_scores,
            cand_scores,
            metric_fn=safe_ap,
            n_iter=args.bootstrap_iters,
            seed=seed + 3000,
        )
        ap_p = paired_permutation_pvalue(
            labels,
            base_scores,
            cand_scores,
            metric_fn=safe_ap,
            n_iter=args.perm_iters,
            seed=seed + 4000,
        )

        runs.append(
            {
                "seed": seed,
                "n_samples": int(labels.size),
                "auc": {
                    "delta": float(auc_delta),
                    "ci_low": float(auc_boot["ci_low"]),
                    "ci_high": float(auc_boot["ci_high"]),
                    "p_value": float(auc_p),
                },
                "ap": {
                    "delta": float(ap_delta),
                    "ci_low": float(ap_boot["ci_low"]),
                    "ci_high": float(ap_boot["ci_high"]),
                    "p_value": float(ap_p),
                },
            }
        )

    report = {
        "meta": {
            "multi_seed_root": str(root),
            "dataset": args.dataset,
            "baseline_variant": args.baseline_variant,
            "candidate_variant": args.candidate_variant,
            "seeds": seeds,
            "bootstrap_iters": args.bootstrap_iters,
            "perm_iters": args.perm_iters,
        },
        "runs": runs,
        "summary": summarize_runs(runs),
    }

    json_path = out_dir / "significance.json"
    md_path = out_dir / "significance.md"
    json_path.write_text(json.dumps(report, indent=2), encoding="utf-8")
    write_markdown(report, md_path)

    print(f"Saved significance JSON: {json_path}")
    print(f"Saved significance report: {md_path}")


if __name__ == "__main__":
    main()
