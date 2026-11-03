"""Compara todos los modelos evaluados (results/*/metrics.json) con las referencias de [6].

Salida: results/comparison.md y results/risk_coverage_all.png
Uso:    python experiments/compare.py
"""
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]
RES = ROOT / "results"

# Barbieri et al. (2022), Tabla 4: macro-F1 en el test español, entrenamiento solo en español.
PUBLISHED = [("FastText [6]", 50.06), ("XLM-R [6]", 65.87), ("XLM-T [6]", 68.52)]


def main():
    runs = []
    for f in sorted(RES.glob("*/metrics.json")):
        m = json.loads(f.read_text(encoding="utf-8"))
        if "macro_f1" in m:
            runs.append((f.parent, m))

    lines = ["# Model comparison — UMSAB Spanish test (n = 870)\n",
             "| Model | Macro-F1 (95% CI) | Recall NEG | T | ECE before → after | AURC | τ | Coverage | Sel. risk | Missed complaints (no abst. → policy) |",
             "|---|---|---|---|---|---|---|---|---|---|"]
    for _, m in runs:
        s = m["selective_test"]; lo, hi = m["macro_f1_ci95"]
        lines.append(f"| {m['model']} | {100*m['macro_f1']:.1f} ({100*lo:.1f}–{100*hi:.1f}) | "
                     f"{m['recall_negative']:.3f} | {m['temperature']:.2f} | "
                     f"{m['ece_test_before']:.3f} → {m['ece_test_after']:.3f} | {m['aurc_test']:.3f} | "
                     f"{s['tau']:.3f} | {s['coverage']:.2f} | {s['selective_risk']:.2f} | "
                     f"{m['missed_negatives_without_abstention']} → {m['missed_negatives_with_policy']} |")
    lines.append("\nPublished references (macro-F1, Spanish-only training): " +
                 ", ".join(f"{n} {v:.1f}" for n, v in PUBLISHED))
    (RES / "comparison.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))

    fig, ax = plt.subplots(figsize=(5, 3.8), dpi=200)
    for d, m in runs:
        c = np.load(d / "curves.npz")
        ax.plot(c["coverage"], c["risk"], lw=1.5, label=f"{m['model']} (AURC {m['aurc_test']:.3f})")
        s = m["selective_test"]
        ax.scatter([s["coverage"]], [s["selective_risk"]], s=18, zorder=3)
    ax.set_xlabel("Coverage"); ax.set_ylabel("Selective risk (error rate)")
    ax.set_xlim(0, 1); ax.set_ylim(0, 0.6); ax.legend(fontsize=7)
    ax.set_title("Risk–coverage on UMSAB Spanish test (dots = operating point τ)", fontsize=8)
    fig.tight_layout(); fig.savefig(RES / "risk_coverage_all.png"); plt.close(fig)


if __name__ == "__main__":
    main()
