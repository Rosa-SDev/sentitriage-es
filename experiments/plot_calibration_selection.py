"""Figura: la calibración cambia la calidad de la confianza, no la selección.

Lee solo resultados ya guardados (no ejecuta modelos):
- ECE antes y después de temperature scaling: results/beto-sentitriage/metrics.json y
  results/colombia/{gold,weak}/beto-sentitriage/metrics.json
- AURC con confianza sin calibrar y calibrada: results/policy_ablation/beto-sentitriage/metrics.json

Uso:  python experiments/plot_calibration_selection.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"
OUT = RES / "policy_ablation" / "calibration_vs_selection.png"
SETS = [("Tweets\n(test)", "tweets_test"), ("Colombia\nhuman labels", "colombia_gold"),
        ("Colombia\nrating labels", "colombia_weak")]


def load(p):
    return json.loads(Path(p).read_text(encoding="utf-8"))


def main():
    tw = load(RES / "beto-sentitriage" / "metrics.json")
    gold = load(RES / "colombia" / "gold" / "beto-sentitriage" / "metrics.json")
    weak = load(RES / "colombia" / "weak" / "beto-sentitriage" / "metrics.json")
    abl = load(RES / "policy_ablation" / "beto-sentitriage" / "metrics.json")["confidence"]

    ece = {"tweets_test": (tw["ece_test_before"], tw["ece_test_after"]),
           "colombia_gold": (gold["ece_before"], gold["ece_after"]),
           "colombia_weak": (weak["ece_before"], weak["ece_after"])}
    aurc = {k: (abl["uncalibrated"]["sets"][k]["aurc"], abl["calibrated"]["sets"][k]["aurc"]) for _, k in SETS}

    x = np.arange(len(SETS)); w = 0.36
    fig, axes = plt.subplots(2, 1, figsize=(3.6, 4.6), dpi=250)
    panels = [(axes[0], ece, "(a) Calibration error (ECE, lower is better)"),
              (axes[1], aurc, "(b) Selection quality (AURC, lower is better)")]
    for ax, data, title in panels:
        raw = [data[k][0] for _, k in SETS]
        cal = [data[k][1] for _, k in SETS]
        ax.bar(x - w / 2, raw, w, label="uncalibrated (T = 1)", color="#9aa5b1")
        ax.bar(x + w / 2, cal, w, label="calibrated (T = 1.92)", color="#2f4b7c")
        for xi, v in zip(np.r_[x - w / 2, x + w / 2], raw + cal):
            ax.text(xi, v + 0.004, f"{v:.3f}", ha="center", fontsize=6)
        ax.set_xticks(x, [s for s, _ in SETS], fontsize=7)
        ax.tick_params(axis="y", labelsize=7)
        ax.set_title(title, fontsize=8)
        ax.set_ylim(0, max(raw + cal) * 1.3)
        ax.grid(axis="y", alpha=0.3)
    axes[0].legend(fontsize=6.5, loc="upper left")
    fig.tight_layout()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(OUT)
    print(f"Figura guardada en {OUT}")


if __name__ == "__main__":
    main()
