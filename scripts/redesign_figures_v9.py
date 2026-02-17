#!/usr/bin/env python3
"""Generate horizontal, publication-ready figures for Event-VLM v9."""

from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, Rectangle, Circle
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
FIG_DIR = ROOT / "paper" / "figures"
FIGSIZE = (14, 7.875)  # 16:9
DPI = 120

plt.rcParams.update(
    {
        "font.family": "DejaVu Sans",
        "figure.facecolor": "#ffffff",
        "axes.facecolor": "#ffffff",
        "savefig.facecolor": "#ffffff",
        "savefig.edgecolor": "#ffffff",
    }
)


def save_figure(fig, path: Path):
    tmp = path.with_suffix(".tmp.png")
    fig.savefig(tmp, dpi=DPI, bbox_inches="tight", facecolor="white", edgecolor="none")
    with Image.open(tmp).convert("RGB") as im:
        im.save(path, format="PNG", optimize=True)
    tmp.unlink(missing_ok=True)


def style_axes(ax):
    ax.set_xticks([])
    ax.set_yticks([])
    for s in ax.spines.values():
        s.set_visible(False)


def rounded_panel(ax, x, y, w, h, face, edge="#2f2f2f", lw=2.0, r=0.03):
    box = FancyBboxPatch(
        (x, y),
        w,
        h,
        boxstyle=f"round,pad=0.01,rounding_size={r}",
        linewidth=lw,
        edgecolor=edge,
        facecolor=face,
        transform=ax.transAxes,
    )
    ax.add_patch(box)
    return box


def fig1_architecture(path: Path):
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    ax = fig.add_axes([0, 0, 1, 1])
    style_axes(ax)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)

    ax.text(0.03, 0.94, "Event-VLM: Tri-Axis Efficient Inference Pipeline", fontsize=26, fontweight="bold")
    ax.text(0.03, 0.90, "Allocate compute only when needed, where needed, and to what matters.", fontsize=16, color="#4a4a4a")

    colors = ["#eaf3ff", "#edf8ea", "#fff3dc", "#f4f4f4"]
    headers = [
        ("Stage 1", "Temporal Axis", "Event-Triggered\nGating", "~99% background frames skipped", "#2b6cb0"),
        ("Stage 2", "Spatial Axis", "Knowledge-Guided\nToken Pruning", "75% tokens pruned", "#2f855a"),
        ("Stage 3", "Decoding Axis", "Frequency-Aware\nSparse Decoding", "~8x KV bandwidth reduction", "#dd6b20"),
        ("Stage 4", "Adaptation", "Hazard-Priority\nPrompting", "Quality recovery with minimal overhead", "#4a5568"),
    ]

    x0, w, gap = 0.04, 0.22, 0.02
    y0, h = 0.20, 0.62

    for i, (s, axis_name, title, kpi, color) in enumerate(headers):
        x = x0 + i * (w + gap)
        rounded_panel(ax, x, y0, w, h, colors[i], edge="#333333", lw=2, r=0.02)
        ax.add_patch(Rectangle((x, y0 + h + 0.02), w, 0.012, transform=ax.transAxes, color=color, ec="none"))
        ax.text(x + 0.01, y0 + h + 0.045, s, fontsize=14, fontweight="bold", color="#222222")
        ax.text(x + 0.01, y0 + h + 0.018, axis_name, fontsize=11, color="#4a4a4a")
        ax.text(x + 0.015, y0 + h - 0.06, title, fontsize=16, fontweight="bold", va="top")

        if i == 0:
            frame_y = np.linspace(y0 + 0.14, y0 + 0.46, 5)
            for j, fy in enumerate(frame_y):
                ax.add_patch(Rectangle((x + 0.03 + 0.006 * j, fy), 0.052, 0.045, transform=ax.transAxes, fc="#d9d9d9", ec="#888", lw=1))
                if j != 2:
                    ax.text(x + 0.055, fy + 0.022, "x", color="#d62728", fontsize=16, ha="center", va="center", fontweight="bold")
                else:
                    ax.text(x + 0.055, fy + 0.022, "ok", color="#2ca02c", fontsize=14, ha="center", va="center", fontweight="bold")
            ax.text(x + 0.095, y0 + 0.28, "Hazard\ntrigger", fontsize=12, color="#333")
            ax.text(x + 0.01, y0 + 0.04, "Risk-sensitive loss", fontsize=12, color="#333")

        elif i == 1:
            gx, gy = np.meshgrid(np.arange(10), np.arange(6))
            for px, py in zip(gx.ravel(), gy.ravel()):
                cx = x + 0.03 + px * 0.018
                cy = y0 + 0.19 + py * 0.06
                col = "#a3a3a3"
                if (py in [0, 1]) and (px in [2, 3, 4]):
                    col = "#65c466"
                ax.add_patch(Rectangle((cx, cy), 0.014, 0.045, transform=ax.transAxes, fc=col, ec="white", lw=0.6))
            ax.text(x + 0.02, y0 + 0.07, "Adaptive dilation around hazard regions", fontsize=12, color="#333")

        elif i == 2:
            base_x = x + 0.04
            for k in range(16):
                yy = y0 + 0.12 + k * 0.027
                fc = "#f28e2b" if k in [3, 6, 9, 13] else "#bdbdbd"
                ax.add_patch(FancyBboxPatch((base_x + 0.10, yy), 0.08, 0.02,
                                            boxstyle="round,pad=0.003,rounding_size=0.004",
                                            transform=ax.transAxes, fc=fc, ec="#666", lw=0.7))
            ax.add_patch(FancyBboxPatch((base_x, y0 + 0.25), 0.08, 0.18,
                                        boxstyle="round,pad=0.01,rounding_size=0.01",
                                        transform=ax.transAxes, fc="#f2f2f2", ec="#777", lw=1.2))
            ax.text(base_x + 0.04, y0 + 0.22, "Vicuna-7B", fontsize=11, ha="center")
            ax.annotate("TIP -> FAC", xy=(base_x + 0.14, y0 + 0.56), xytext=(base_x + 0.08, y0 + 0.60),
                        textcoords=ax.transAxes, xycoords=ax.transAxes,
                        arrowprops=dict(arrowstyle="->", color="#333", lw=1.5), fontsize=11)
            ax.text(x + 0.02, y0 + 0.05, "Dominant FCs only (~12.5%)", fontsize=12, color="#333")

        else:
            rounded_panel(ax, x + 0.03, y0 + 0.38, 0.16, 0.12, "#ffffff", edge="#777", lw=1.5, r=0.01)
            ax.text(x + 0.11, y0 + 0.44, "Prompt\nBank", ha="center", va="center", fontsize=12)
            rounded_panel(ax, x + 0.03, y0 + 0.20, 0.16, 0.12, "#fff8f1", edge="#d66", lw=1.5, r=0.01)
            ax.text(x + 0.11, y0 + 0.26, "Safety Alert\nOutput", ha="center", va="center", fontsize=12)
            ax.annotate("", xy=(x + 0.11, y0 + 0.33), xytext=(x + 0.11, y0 + 0.38),
                        xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", lw=1.8, color="#444"))
            ax.text(x + 0.01, y0 + 0.08, "Context routing for critical hazards", fontsize=11, color="#333")

        ax.text(x + 0.01, 0.13, kpi, fontsize=12, fontweight="bold", color="#222")

        if i < 3:
            ax.annotate("", xy=(x + w + 0.012, y0 + 0.32), xytext=(x + w - 0.002, y0 + 0.32),
                        xycoords=ax.transAxes, arrowprops=dict(arrowstyle="->", lw=2.0, color="#333"))

    save_figure(fig, path)
    plt.close(fig)


def fig2_components(path: Path):
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    gs = fig.add_gridspec(1, 3, left=0.04, right=0.98, top=0.90, bottom=0.10, wspace=0.18)

    # Panel 1: risk-sensitive loss
    ax1 = fig.add_subplot(gs[0, 0])
    classes = ["Fire", "Smoke", "Collapse", "Forklift", "Machine", "Person", "Vehicle"]
    weights = [3.0, 3.0, 3.0, 2.0, 2.0, 1.0, 1.0]
    cols = ["#d62728", "#d62728", "#d62728", "#f39c34", "#f39c34", "#2f80c1", "#2f80c1"]
    ax1.bar(classes, weights, color=cols, edgecolor="#333", linewidth=1)
    ax1.set_ylim(0, 3.4)
    ax1.set_ylabel("Class Weight (lambda)", fontsize=14, fontweight="bold")
    ax1.set_title("Risk-Sensitive Loss", fontsize=18, fontweight="bold", pad=10)
    ax1.grid(axis="y", linestyle="--", alpha=0.35)
    ax1.tick_params(axis="x", rotation=45, labelsize=12)
    ax1.tick_params(axis="y", labelsize=12)
    for s in ax1.spines.values():
        s.set_linewidth(1.4)
    ax1.text(0.1, 3.16, "CRITICAL", color="#d62728", fontsize=12, fontweight="bold")
    ax1.text(2.8, 3.16, "HIGH", color="#f39c34", fontsize=12, fontweight="bold")
    ax1.text(4.8, 3.16, "STANDARD", color="#2f80c1", fontsize=12, fontweight="bold")

    # Panel 2: adaptive dilation
    ax2 = fig.add_subplot(gs[0, 1])
    style_axes(ax2)
    ax2.set_xlim(0, 1)
    ax2.set_ylim(0, 1)
    ax2.set_title("Adaptive Dilation", fontsize=18, fontweight="bold", pad=10)

    rounded_panel(ax2, 0.22, 0.60, 0.18, 0.28, "#eff7ff", edge="#2f80c1", lw=2)
    rounded_panel(ax2, 0.56, 0.20, 0.30, 0.42, "#fff5f2", edge="#d62728", lw=2)
    rounded_panel(ax2, 0.62, 0.30, 0.18, 0.22, "#ffffff", edge="#d62728", lw=1.8)
    ax2.text(0.31, 0.74, "small\nexpansion\ns=0.12", ha="center", va="center", fontsize=12)
    ax2.text(0.71, 0.40, "large\nexpansion\ns=0.42", ha="center", va="center", fontsize=12)
    ax2.text(0.49, 0.53, "adaptive\nfactor s", ha="center", va="center", fontsize=13, fontweight="bold")

    ax2.annotate("", xy=(0.56, 0.42), xytext=(0.40, 0.72), xycoords=ax2.transAxes,
                 arrowprops=dict(arrowstyle="->", lw=2, color="#333"))

    # simple person/fire icons with circles
    ax2.add_patch(Circle((0.30, 0.78), 0.035, transform=ax2.transAxes, fc="#5dade2", ec="#333", lw=1))
    ax2.add_patch(Rectangle((0.27, 0.67), 0.06, 0.10, transform=ax2.transAxes, fc="#5dade2", ec="#333", lw=1))
    ax2.add_patch(Circle((0.71, 0.41), 0.08, transform=ax2.transAxes, fc="#ff8c42", ec="#b22222", lw=1.8, alpha=0.9))
    ax2.add_patch(Circle((0.69, 0.46), 0.06, transform=ax2.transAxes, fc="#ffc14d", ec="none", alpha=0.95))

    # Panel 3: prompt selection
    ax3 = fig.add_subplot(gs[0, 2])
    style_axes(ax3)
    ax3.set_xlim(0, 1)
    ax3.set_ylim(0, 1)
    ax3.set_title("Priority Prompt Routing", fontsize=18, fontweight="bold", pad=10)

    rounded_panel(ax3, 0.34, 0.78, 0.32, 0.11, "#eaf3ff", edge="#2f80c1", lw=1.8)
    ax3.text(0.50, 0.835, "Hazard Detection", ha="center", va="center", fontsize=12, fontweight="bold")

    rounded_panel(ax3, 0.38, 0.58, 0.24, 0.12, "#ffffff", edge="#2f80c1", lw=1.8)
    ax3.text(0.50, 0.64, "Critical\nHazard?", ha="center", va="center", fontsize=12, fontweight="bold")

    rounded_panel(ax3, 0.08, 0.34, 0.34, 0.20, "#fff0ee", edge="#d62728", lw=1.8)
    rounded_panel(ax3, 0.58, 0.34, 0.34, 0.20, "#eef6ff", edge="#2f80c1", lw=1.8)
    ax3.text(0.25, 0.44, "Critical\nPrompt Bank", ha="center", va="center", fontsize=12, fontweight="bold", color="#b22222")
    ax3.text(0.75, 0.44, "Standard\nPrompt Bank", ha="center", va="center", fontsize=12, fontweight="bold", color="#2f80c1")

    rounded_panel(ax3, 0.35, 0.14, 0.30, 0.11, "#f5f5f5", edge="#4a5568", lw=1.8)
    ax3.text(0.50, 0.195, "VLM Output", ha="center", va="center", fontsize=12, fontweight="bold")

    ax3.annotate("", xy=(0.50, 0.70), xytext=(0.50, 0.78), xycoords=ax3.transAxes,
                 arrowprops=dict(arrowstyle="->", lw=1.8, color="#333"))
    ax3.annotate("", xy=(0.25, 0.54), xytext=(0.44, 0.63), xycoords=ax3.transAxes,
                 arrowprops=dict(arrowstyle="->", lw=1.8, color="#d62728"))
    ax3.annotate("", xy=(0.75, 0.54), xytext=(0.56, 0.63), xycoords=ax3.transAxes,
                 arrowprops=dict(arrowstyle="->", lw=1.8, color="#2f80c1"))
    ax3.annotate("", xy=(0.50, 0.25), xytext=(0.25, 0.34), xycoords=ax3.transAxes,
                 arrowprops=dict(arrowstyle="->", lw=1.8, color="#d62728"))
    ax3.annotate("", xy=(0.50, 0.25), xytext=(0.75, 0.34), xycoords=ax3.transAxes,
                 arrowprops=dict(arrowstyle="->", lw=1.8, color="#2f80c1"))

    save_figure(fig, path)
    plt.close(fig)


def fig3_pruning(path: Path):
    rng = np.random.default_rng(7)
    fig = plt.figure(figsize=FIGSIZE, dpi=DPI)
    gs = fig.add_gridspec(1, 2, left=0.04, right=0.98, top=0.90, bottom=0.10, wspace=0.12)

    # Left panel: spatial token pruning
    axl = fig.add_subplot(gs[0, 0])
    style_axes(axl)
    axl.set_xlim(0, 1)
    axl.set_ylim(0, 1)
    rounded_panel(axl, 0.00, 0.00, 1.0, 1.0, "#f9f9f9", edge="#333", lw=2, r=0.02)
    axl.text(0.03, 0.95, "Spatial Token Pruning", fontsize=20, fontweight="bold")

    # background scene mock
    axl.add_patch(Rectangle((0.06, 0.10), 0.88, 0.78, transform=axl.transAxes, fc="#d9dde0", ec="#666", lw=1.2))
    for k in range(12):
        x = 0.08 + k * 0.07
        axl.plot([x, x], [0.10, 0.88], color="white", lw=1, alpha=0.6)
    for k in range(10):
        y = 0.12 + k * 0.07
        axl.plot([0.06, 0.94], [y, y], color="white", lw=1, alpha=0.6)

    # worker and hazard boxes
    rounded_panel(axl, 0.57, 0.34, 0.24, 0.26, "none", edge="#2f855a", lw=2.2, r=0.01)
    rounded_panel(axl, 0.19, 0.21, 0.18, 0.20, "none", edge="#dd6b20", lw=2.2, r=0.01)
    rounded_panel(axl, 0.40, 0.30, 0.07, 0.20, "none", edge="#2f855a", lw=2.0, r=0.01)

    # kept tokens
    for gx in range(4):
        for gy in range(5):
            axl.add_patch(Rectangle((0.60 + gx * 0.05, 0.36 + gy * 0.045), 0.038, 0.032,
                                    transform=axl.transAxes, fc="#65c466", ec="#1d4", lw=0.6))
    for gx in range(4):
        for gy in range(4):
            axl.add_patch(Rectangle((0.22 + gx * 0.04, 0.23 + gy * 0.04), 0.03, 0.026,
                                    transform=axl.transAxes, fc="#ff8c42", ec="#d35400", lw=0.6))

    axl.text(0.58, 0.27, "Fixed dilation (a=1.20)", fontsize=12, bbox=dict(fc="white", ec="#999", boxstyle="round,pad=0.3"))
    axl.text(0.26, 0.14, "Adaptive dilation (a=1.50)", fontsize=12, bbox=dict(fc="white", ec="#999", boxstyle="round,pad=0.3"))
    axl.text(0.06, 0.04, "576 -> 142 tokens (75% reduction)", fontsize=16, fontweight="bold")

    # Right panel: decoding visualization
    axr = fig.add_subplot(gs[0, 1])
    style_axes(axr)
    axr.set_xlim(0, 1)
    axr.set_ylim(0, 1)
    rounded_panel(axr, 0.00, 0.00, 1.0, 1.0, "#f9f9f9", edge="#333", lw=2, r=0.02)
    axr.text(0.03, 0.95, "Frequency-Aware Sparse Decoding", fontsize=20, fontweight="bold")

    axr.text(0.05, 0.87, "Only 12.5% of FCs are dominant", fontsize=13, fontweight="bold")
    axr.add_patch(Rectangle((0.05, 0.81), 0.90, 0.05, transform=axr.transAxes, fc="#ededed", ec="#666", lw=1.0))
    for i in range(64):
        x = 0.05 + i * (0.90 / 64)
        c = "#f28e2b" if i in [1, 6, 10, 21, 37, 44, 52, 60] else "#c7c7c7"
        axr.add_patch(Rectangle((x, 0.812), 0.90 / 64 - 0.001, 0.046, transform=axr.transAxes, fc=c, ec="none"))

    heat1 = rng.normal(0.5, 0.2, size=(28, 28))
    heat1 = np.clip(heat1 + np.eye(28) * 0.35, 0, 1)
    heat2 = np.zeros((28, 28))
    for k in range(6):
        s = 4 * k
        heat2[s : s + 6, s : s + 6] = rng.uniform(0.4, 1.0)
    heat2 = np.clip(heat2, 0, 1)

    axh1 = axr.inset_axes([0.08, 0.46, 0.38, 0.28])
    axh2 = axr.inset_axes([0.54, 0.46, 0.38, 0.28])
    axh1.imshow(heat1, cmap="turbo", vmin=0, vmax=1)
    axh2.imshow(heat2, cmap="turbo", vmin=0, vmax=1)
    axh1.set_title("Full Attention", fontsize=12)
    axh2.set_title("FC-Sparse Attention", fontsize=12)
    for a in (axh1, axh2):
        a.set_xticks([])
        a.set_yticks([])

    axb = axr.inset_axes([0.08, 0.12, 0.84, 0.24])
    axb.bar([0, 1], [100, 12.5], color=["#bdbdbd", "#f28e2b"], edgecolor="#444")
    axb.set_xticks([0, 1], ["Full KV", "FASA-Sparse"])
    axb.set_ylim(0, 110)
    axb.set_ylabel("Relative KV BW", fontsize=11)
    axb.grid(axis="y", linestyle="--", alpha=0.35)
    axb.tick_params(axis="both", labelsize=11)
    for s in axb.spines.values():
        s.set_linewidth(1)
    axb.annotate("8x reduction", xy=(1, 12.5), xytext=(1, 72),
                 arrowprops=dict(arrowstyle="->", lw=1.8), ha="center", fontsize=13, fontweight="bold")

    save_figure(fig, path)
    plt.close(fig)


def main():
    FIG_DIR.mkdir(parents=True, exist_ok=True)
    fig1_architecture(FIG_DIR / "figure1_architecture.png")
    fig2_components(FIG_DIR / "figure2_components.png")
    fig3_pruning(FIG_DIR / "figure3_pruning.png")
    print("Generated:")
    print(FIG_DIR / "figure1_architecture.png")
    print(FIG_DIR / "figure2_components.png")
    print(FIG_DIR / "figure3_pruning.png")


if __name__ == "__main__":
    main()
