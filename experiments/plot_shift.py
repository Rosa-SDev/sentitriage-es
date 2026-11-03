"""Figuras del cambio de dominio (tuits -> comentarios colombianos).

Salida: results/colombia/<set>/shift_f1.png y shift_risk_coverage.png
Uso:    python experiments/plot_shift.py [weak|gold]
"""
import json
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
NICE = {"baseline-tfidf-lr": "TF-IDF + LR", "beto-sentitriage": "BETO", "xlmr-sentitriage": "XLM-R"}


def main(set_name: str):
    base = ROOT / "results" / "colombia" / set_name
    runs = [d for d in sorted(base.iterdir()) if (d / "metrics.json").exists()]
    classes = ["negative", "neutral", "positive"]

    fig, axes = plt.subplots(1, len(runs), figsize=(4.2 * len(runs), 3.4), dpi=200, sharey=True)
    axes = np.atleast_1d(axes)
    for ax, d in zip(axes, runs):
        col = json.loads((d / "metrics.json").read_text(encoding="utf-8"))
        tw = json.loads((ROOT / "results" / d.name / "metrics.json").read_text(encoding="utf-8"))
        x = np.arange(4)
        a = [tw["per_class"][c]["f1-score"] for c in classes] + [tw["macro_f1"]]
        b = [col["per_class"][c]["f1-score"] for c in classes] + [col["macro_f1"]]
        ax.bar(x - 0.2, a, 0.4, label="Spanish tweets (test)", color="#9aa7bd")
        ax.bar(x + 0.2, b, 0.4, label="Colombian comments", color="#2f4b7c")
        for xi, v in zip(x + 0.2, b):
            ax.text(xi, v + 0.01, f"{v:.2f}", ha="center", fontsize=7)
        ax.set_xticks(x, classes + ["macro"])
        ax.set_title(NICE.get(d.name, d.name), fontsize=9)
        ax.set_ylim(0, 1)
    axes[0].set_ylabel("F1")
    axes[0].legend(fontsize=7, loc="upper left")
    fig.tight_layout(); fig.savefig(base / "shift_f1.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(4.8, 3.6), dpi=200)
    for d in runs:
        tw = np.load(ROOT / "results" / d.name / "curves.npz")
        co = np.load(d / "curves.npz")
        line, = ax.plot(co["coverage"], co["risk"], lw=1.6, label=f"{NICE.get(d.name)} — Colombia")
        ax.plot(tw["coverage"], tw["risk"], lw=1.1, ls="--", color=line.get_color(), label=f"{NICE.get(d.name)} — tweets")
    ax.set_xlabel("Coverage"); ax.set_ylabel("Selective risk (error rate)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 0.6); ax.legend(fontsize=7)
    ax.set_title("Risk–coverage: tweets vs. Colombian comments (same T and τ)", fontsize=8)
    fig.tight_layout(); fig.savefig(base / "shift_risk_coverage.png"); plt.close(fig)
    print("->", base)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "weak")
