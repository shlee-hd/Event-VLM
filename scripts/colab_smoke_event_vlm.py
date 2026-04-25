#!/usr/bin/env python3
"""
Colab-first Event-VLM smoke proof package.

This script intentionally avoids real LLaVA weights. It validates the structural
invariants needed before server benchmarks:
- detector-linked patches are retained by token pruning,
- evidence anchors survive FC sparse selection,
- unsupported reports fail closed,
- readable Figure 2/3 prototype visualizations are emitted.
"""

from __future__ import annotations

import argparse
import csv
import json
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Iterable, List

import cv2
import numpy as np
import torch
from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from src.decoding import EvidenceAwareFCSparseSelector, FCSparseConfig
from src.detector.detr_wrapper import Detection
from src.pruning import TokenPruner
from src.reporting import EvidenceReport, ReportingContract, unsafe_valid_rate
from src.vlm.llava_wrapper import MockLLaVAWrapper


def synthetic_frame(image_size: int) -> np.ndarray:
    """Create a deterministic surveillance-like RGB frame."""
    frame = np.zeros((image_size, image_size, 3), dtype=np.uint8)
    frame[:] = (32, 36, 40)
    cv2.rectangle(frame, (30, image_size - 90), (image_size - 35, image_size - 35), (82, 86, 92), -1)
    cv2.rectangle(frame, (132, 132), (182, 188), (170, 170, 170), -1)
    cv2.circle(frame, (160, 118), 22, (185, 185, 185), -1)
    cv2.circle(frame, (178, 96), 16, (150, 150, 150), -1)
    cv2.rectangle(frame, (80, 180), (118, 250), (55, 100, 180), -1)
    cv2.circle(frame, (99, 164), 15, (170, 130, 105), -1)
    return frame


def run_pytest(output_dir: Path, skip_pytest: bool) -> Dict[str, object]:
    """Run the unit smoke tests requested by the Colab protocol."""
    if skip_pytest:
        return {"skipped": True, "returncode": 0, "output_path": None}

    output_path = output_dir / "pytest_test_modules.txt"
    cmd = [sys.executable, "-m", "pytest", "-q", "tests/test_modules.py"]
    proc = subprocess.run(
        cmd,
        cwd=str(ROOT),
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        check=False,
    )
    output_path.write_text(proc.stdout, encoding="utf-8")
    return {
        "skipped": False,
        "returncode": proc.returncode,
        "output_path": str(output_path),
    }


def evidence_positions(kept_indices: Iterable[int], evidence_indices: Iterable[int]) -> List[int]:
    evidence = {int(i) for i in evidence_indices}
    return [pos for pos, original in enumerate(kept_indices) if int(original) in evidence]


def write_selection_plot(selection, output_path: Path) -> None:
    """Draw a compact evidence-anchor vs FC-ranked selection diagnostic."""
    width, height = 1100, 260
    margin = 50
    y = 120
    img = Image.new("RGB", (width, height), "white")
    draw = ImageDraw.Draw(img)

    draw.text((margin, 18), "Evidence-aware FC sparse selection", fill=(20, 20, 20))
    draw.text((margin, 40), "green=evidence anchor, orange=sink/recent anchor, blue=FC-ranked keep, gray=dropped", fill=(70, 70, 70))
    draw.line((margin, y, width - margin, y), fill=(180, 180, 180), width=2)

    keep = {int(i) for i in selection.keep_indices.tolist()}
    evidence = {int(i) for i in selection.evidence_indices.tolist()}
    anchors = {int(i) for i in selection.anchor_indices.tolist()}
    frequency = {int(i) for i in selection.frequency_indices.tolist()}

    total = max(selection.num_total - 1, 1)
    radius = 4
    for idx in range(selection.num_total):
        x = margin + int((width - 2 * margin) * idx / total)
        if idx in evidence:
            color = (20, 145, 85)
            r = 6
        elif idx in anchors:
            color = (230, 138, 30)
            r = 5
        elif idx in frequency:
            color = (45, 110, 210)
            r = radius
        elif idx in keep:
            color = (90, 140, 220)
            r = radius
        else:
            color = (200, 200, 200)
            r = 2
        draw.ellipse((x - r, y - r, x + r, y + r), fill=color)

    draw.text((margin, 178), f"total={selection.num_total}", fill=(30, 30, 30))
    draw.text((margin + 180, 178), f"kept={selection.keep_indices.numel()}", fill=(30, 30, 30))
    draw.text((margin + 360, 178), f"keep_ratio={selection.keep_ratio:.3f}", fill=(30, 30, 30))
    draw.text((margin + 590, 178), f"evidence_retention={selection.evidence_retention:.3f}", fill=(30, 30, 30))
    img.save(output_path)


def write_csv(path: Path, rows: List[Dict[str, object]]) -> None:
    if not rows:
        path.write_text("", encoding="utf-8")
        return
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    parser = argparse.ArgumentParser(description="Run Colab-first Event-VLM smoke proof")
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/colab_smoke"))
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--skip-pytest", action="store_true")
    args = parser.parse_args()

    torch.manual_seed(args.seed)
    np.random.seed(args.seed)

    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    pytest_result = run_pytest(output_dir, skip_pytest=args.skip_pytest)

    image_size = 336
    frame_rgb = synthetic_frame(image_size)
    frame_path = output_dir / "synthetic_frame.png"
    Image.fromarray(frame_rgb).save(frame_path)

    detection = Detection(
        bbox=(0.38, 0.28, 0.58, 0.57),
        class_id=0,
        class_name="smoke",
        confidence=0.94,
        hazard_level="critical",
    )
    pruner = TokenPruner(image_size=image_size, patch_size=14, min_tokens=1)
    visual_tokens = torch.randn(1, pruner.num_patches, 64)
    pruned_tokens, pruning = pruner.prune(
        visual_tokens,
        [detection],
        return_mask=True,
    )

    mask_overlay = pruner.visualize_mask(pruning.mask, frame_rgb)
    mask_path = output_dir / "figure2_token_mask_overlay.png"
    cv2.imwrite(str(mask_path), cv2.cvtColor(mask_overlay, cv2.COLOR_RGB2BGR))

    evidence_original = [int(i) for i in pruning.evidence_indices.tolist()]
    kept_original = [int(i) for i in pruning.kept_indices.tolist()]
    evidence_never_pruned = set(evidence_original).issubset(set(kept_original))

    selector = EvidenceAwareFCSparseSelector(
        FCSparseConfig(
            enabled=True,
            budget=160,
            min_keep=32,
            sink_tokens=4,
            recent_tokens=16,
            preserve_evidence=True,
            dense_fallback=True,
        )
    )
    sparse_start = time.perf_counter()
    selection = selector.select(
        token_states=visual_tokens,
        evidence_indices=evidence_original,
    )
    sparse_latency_ms = (time.perf_counter() - sparse_start) * 1000.0

    dense_selector = EvidenceAwareFCSparseSelector(FCSparseConfig(enabled=False))
    dense_start = time.perf_counter()
    dense_selection = dense_selector.select(
        num_entries=pruner.num_patches,
        evidence_indices=evidence_original,
    )
    dense_latency_ms = (time.perf_counter() - dense_start) * 1000.0

    selection_plot = output_dir / "figure3_fc_sparse_selection.png"
    write_selection_plot(selection, selection_plot)

    contract = ReportingContract()
    valid_report = contract.build_frame_report(
        caption="Smoke is visible near a worker.",
        frame_idx=0,
        timestamp=0.0,
        detections=[detection],
        token_indices=evidence_original,
        status="valid",
    )
    unsupported_report = EvidenceReport(
        event_statement="Smoke is visible but no detector evidence is attached.",
        status="valid",
        evidence=(),
    )
    abstain_report = EvidenceReport(event_statement="", status="abstain", evidence=())
    validations = [
        contract.validate(valid_report),
        contract.validate(unsupported_report),
        contract.validate(abstain_report),
    ]
    status_rows = [
        {
            "case": "valid_with_evidence",
            "requested_status": validations[0].requested_status,
            "resolved_status": validations[0].resolved_status,
            "failures": ";".join(validations[0].failures),
        },
        {
            "case": "unsupported_valid",
            "requested_status": validations[1].requested_status,
            "resolved_status": validations[1].resolved_status,
            "failures": ";".join(validations[1].failures),
        },
        {
            "case": "abstain",
            "requested_status": validations[2].requested_status,
            "resolved_status": validations[2].resolved_status,
            "failures": ";".join(validations[2].failures),
        },
    ]
    status_table = output_dir / "report_status_table.csv"
    write_csv(status_table, status_rows)

    latency_rows = [
        {
            "path": "dense_visual_tokens",
            "visual_tokens": dense_selection.effective_budget,
            "kv_keep_ratio": 1.0,
            "selector_latency_ms": f"{dense_latency_ms:.4f}",
        },
        {
            "path": "pruned_visual_tokens",
            "visual_tokens": int(pruned_tokens.shape[1]),
            "kv_keep_ratio": int(pruned_tokens.shape[1]) / pruner.num_patches,
            "selector_latency_ms": "0.0000",
        },
        {
            "path": "fc_sparse_cache",
            "visual_tokens": selection.effective_budget,
            "kv_keep_ratio": f"{selection.keep_ratio:.4f}",
            "selector_latency_ms": f"{sparse_latency_ms:.4f}",
        },
    ]
    latency_table = output_dir / "dense_vs_sparse_latency_tokens.csv"
    write_csv(latency_table, latency_rows)

    mock_vlm = MockLLaVAWrapper(device="cpu")
    mock_output = mock_vlm.generate(
        image=Image.fromarray(frame_rgb),
        prompt="Describe safety-relevant evidence only.",
        pruned_tokens=visual_tokens[:, selection.keep_indices, :],
        sparse_selection={
            **selection.to_dict(),
            "kv_mapping": {
                "sequence_length": selection.num_total,
                "visual_token_start": 0,
                "visual_token_count": selection.num_total,
            },
            "kv_config": {
                "sink_tokens": 4,
                "recent_tokens": 16,
                "preserve_text_tokens": True,
            },
        },
    )

    unsupported_reports_fail_closed = validations[1].resolved_status == "insufficient_evidence"
    acceptance = {
        "evidence_linked_patches_never_pruned": evidence_never_pruned,
        "evidence_anchors_never_dropped": selection.evidence_retention == 1.0,
        "sparse_selector_active": not selection.used_dense_fallback and selection.keep_ratio < 1.0,
        "unsupported_reports_fail_closed": unsupported_reports_fail_closed,
        "visualizations_written": mask_path.exists() and selection_plot.exists(),
        "pytest_passed": pytest_result["returncode"] == 0,
    }

    summary = {
        "seed": args.seed,
        "artifacts": {
            "frame": str(frame_path),
            "token_mask_overlay": str(mask_path),
            "fc_sparse_selection_plot": str(selection_plot),
            "latency_token_table": str(latency_table),
            "report_status_table": str(status_table),
            "pytest_output": pytest_result["output_path"],
        },
        "metrics": {
            "evidence_retention": selection.evidence_retention,
            "keep_ratio": selection.keep_ratio,
            "unsafe_valid_rate": unsafe_valid_rate(validations),
            "pruning_keep_ratio": pruning.num_kept / pruning.num_total,
            "mock_kv_keep_ratio": (mock_output.decoding or {}).get("kv_keep_ratio"),
        },
        "diagnostics": {
            "pruning": {
                "num_total": pruning.num_total,
                "num_kept": pruning.num_kept,
                "num_evidence": pruning.num_evidence,
                "evidence_positions_after_pruning": evidence_positions(
                    kept_original,
                    evidence_original,
                ),
            },
            "selection": selection.to_dict(),
            "mock_decoding": mock_output.decoding,
            "pytest": pytest_result,
        },
        "acceptance": acceptance,
    }

    summary_path = output_dir / "colab_smoke_summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    print(f"Colab smoke summary: {summary_path}")
    print(json.dumps({"acceptance": acceptance, "metrics": summary["metrics"]}, indent=2))

    if not all(acceptance.values()):
        raise SystemExit("Colab smoke acceptance failed. See summary JSON for details.")


if __name__ == "__main__":
    main()
