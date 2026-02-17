#!/usr/bin/env python3
"""Create a publication-ready speed-quality frontier figure for Event-VLM."""

from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'paper' / 'figures' / 'figure4_frontier.png'

plt.rcParams.update({
    'font.family': 'DejaVu Sans',
    'axes.facecolor': 'white',
    'figure.facecolor': 'white',
    'savefig.facecolor': 'white',
    'axes.grid': True,
    'grid.linestyle': '--',
    'grid.alpha': 0.25,
})

METHODS = [
    'Video-LLaMA',
    'LLaVA-1.5',
    'SeViLA',
    'LLaVA+ToMe',
    'LLaVA+SnapKV',
    'Event-VLM-Core',
    'Event-VLM-Full',
]

FPS_UCF = np.array([3.5, 5.2, 12.0, 15.6, 14.2, 48.2, 48.0])
CIDER_UCF = np.array([82.3, 90.1, 88.0, 85.4, 87.8, 89.0, 89.5])
GFLOPS_UCF = np.array([450.2, 180.5, 108.3, 90.2, 95.0, 45.1, 45.1])

FPS_XD = np.array([3.5, 5.2, 12.0, 15.6, 14.2, 47.5, 47.3])
CIDER_XD = np.array([77.9, 86.4, 84.7, 82.6, 84.3, 85.4, 85.9])
GFLOPS_XD = np.array([450.2, 180.5, 108.3, 90.2, 95.0, 45.1, 45.1])

COLORS = {
    'Video-LLaMA': '#8a8a8a',
    'LLaVA-1.5': '#4e79a7',
    'SeViLA': '#59a14f',
    'LLaVA+ToMe': '#f28e2b',
    'LLaVA+SnapKV': '#e15759',
    'Event-VLM-Core': '#1f9e89',
    'Event-VLM-Full': '#2ca02c',
}


def size_from_gflops(g):
    # Smaller GFLOPs -> larger marker (better efficiency)
    return 900 / np.sqrt(g)


def annotate(ax, x, y, label, color):
    dx = 0.55 if 'Event-VLM' in label else 0.35
    dy = 0.18 if label in ('Event-VLM-Core', 'Event-VLM-Full') else 0.08
    ax.text(x + dx, y + dy, label, fontsize=9.5, color=color, fontweight='bold' if 'Event-VLM' in label else 'normal')


fig, axes = plt.subplots(1, 2, figsize=(13.8, 5.6), dpi=180, sharex=True)

datasets = [
    ('UCF-Crime', FPS_UCF, CIDER_UCF, GFLOPS_UCF),
    ('XD-Violence', FPS_XD, CIDER_XD, GFLOPS_XD),
]

for ax, (name, fps, cider, gflops) in zip(axes, datasets):
    for m, x, y, g in zip(METHODS, fps, cider, gflops):
        c = COLORS[m]
        ax.scatter(x, y, s=size_from_gflops(g), color=c, edgecolors='black', linewidths=0.7, alpha=0.9, zorder=3)
        annotate(ax, x, y, m, c)

    # Draw frontier emphasis line for ours
    ax.plot([fps[-2], fps[-1]], [cider[-2], cider[-1]], color='#0a9396', linewidth=2.5, zorder=2)

    ax.set_title(f'{name}', fontsize=15, fontweight='bold')
    ax.set_xlabel('Throughput (FPS)', fontsize=11)
    ax.set_xlim(0, 52)
    ypad = 0.7 if name == 'UCF-Crime' else 0.8
    ax.set_ylim(min(cider) - ypad, max(cider) + ypad)
    ax.tick_params(labelsize=10)

axes[0].set_ylabel('Caption Quality (CIDEr)', fontsize=11)

# Legend-like marker scale note
for g in [450, 180, 90, 45]:
    axes[1].scatter([], [], s=size_from_gflops(g), color='#bbbbbb', edgecolors='black', linewidths=0.7, label=f'{g} GFLOPs')
leg = axes[1].legend(title='Marker size = efficiency', loc='lower right', fontsize=8.5, title_fontsize=9.5, frameon=True)
leg.get_frame().set_alpha(0.92)

fig.suptitle('Speed-Quality Frontier of Explanation-Capable Models', fontsize=19, fontweight='bold', y=1.01)
fig.tight_layout()

OUT.parent.mkdir(parents=True, exist_ok=True)
fig.savefig(OUT, bbox_inches='tight')
print(f'Generated: {OUT}')
