"""Protocolo de evaluación común a todos los modelos.

Entrada: logits de validación y prueba. Pasos:
1. Ajustar T en validación (temperature scaling).
2. Elegir τ en validación para un riesgo selectivo objetivo.
3. Medir en prueba: accuracy, macro-F1 (+ IC 95 % por bootstrap), recall NEG,
   ECE antes y después de calibrar, AURC, cobertura y riesgo con el τ elegido.
4. Guardar métricas, predicciones y figuras.

Así el baseline (ejecutado localmente) y BETO / XLM-R (ejecutados en Colab) se
comparan exactamente con el mismo código.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.metrics import (accuracy_score, classification_report, confusion_matrix,
                             f1_score, recall_score)

from . import LABELS, NEGATIVE
from .agent import decide
from .calibration import (expected_calibration_error, fit_temperature, nll,
                          reliability_bins, softmax)
from .selective import aurc, choose_threshold, risk_coverage_curve, selective_stats

DEFAULT_TARGET_RISK = 0.25
SWEEP_TARGETS = (0.20, 0.25, 0.30, 0.35)


def bootstrap_macro_f1(y, pred, n: int = 1000, seed: int = 42):
    rng = np.random.default_rng(seed)
    idx = np.arange(len(y))
    scores = []
    for _ in range(n):
        s = rng.choice(idx, size=len(idx), replace=True)
        scores.append(f1_score(y[s], pred[s], average="macro"))
    return float(np.percentile(scores, 2.5)), float(np.percentile(scores, 97.5))


def evaluate(name: str, logits_val, y_val, logits_test, y_test, texts_test,
             outdir: Path, target_risk: float = DEFAULT_TARGET_RISK) -> dict:
    outdir = Path(outdir)
    outdir.mkdir(parents=True, exist_ok=True)
    y_val, y_test = np.asarray(y_val), np.asarray(y_test)

    T = fit_temperature(logits_val, y_val)
    p_val = softmax(logits_val, T)
    p_test_raw = softmax(logits_test, 1.0)
    p_test = softmax(logits_test, T)

    pred = p_test.argmax(1)
    conf = p_test.max(1)
    correct = (pred == y_test)

    tau = choose_threshold(p_val.max(1), p_val.argmax(1) == y_val, target_risk)
    sel = selective_stats(conf, correct, tau)

    # Recall negativo entre las aceptadas, y qué pasa con las negativas reales
    accepted = conf >= tau
    neg = y_test == NEGATIVE
    actions = [decide(p, tau).action for p in p_test]
    neg_actions = pd.Series(np.array(actions)[neg]).value_counts().to_dict()

    # Sensibilidad de la política: τ elegido en validación para varios riesgos objetivo
    sweep = []
    for t in SWEEP_TARGETS:
        tau_t = choose_threshold(p_val.max(1), p_val.argmax(1) == y_val, t)
        val_t = selective_stats(p_val.max(1), p_val.argmax(1) == y_val, tau_t)
        sweep.append({"target_risk": t, "tau": tau_t, "val_coverage": val_t["coverage"],
                      **{f"test_{k}": v for k, v in selective_stats(conf, correct, tau_t).items()
                         if k in ("coverage", "selective_risk")}})

    lo, hi = bootstrap_macro_f1(y_test, pred)
    metrics = {
        "model": name,
        "n_val": int(len(y_val)), "n_test": int(len(y_test)),
        "accuracy": float(accuracy_score(y_test, pred)),
        "macro_f1": float(f1_score(y_test, pred, average="macro")),
        "macro_f1_ci95": [lo, hi],
        "recall_negative": float(recall_score(y_test, pred, labels=[NEGATIVE], average="macro")),
        "temperature": T,
        "nll_test_before": nll(logits_test, y_test, 1.0),
        "nll_test_after": nll(logits_test, y_test, T),
        "ece_test_before": expected_calibration_error(p_test_raw, y_test),
        "ece_test_after": expected_calibration_error(p_test, y_test),
        "aurc_test": aurc(conf, correct),
        "error_rate_full_coverage": float(1 - correct.mean()),
        "target_risk_val": target_risk,
        "selective_test": sel,
        "policy_sweep": sweep,
        "accepted_recall_negative": float((pred[accepted & neg] == NEGATIVE).mean()) if (accepted & neg).any() else None,
        "true_negatives_by_action": {k: int(v) for k, v in neg_actions.items()},
        # Quejas que pasarían sin que nadie las lea (negativa real -> PASS)
        "missed_negatives_without_abstention": int((neg & (pred != NEGATIVE)).sum()),
        "missed_negatives_with_policy": int(neg_actions.get("PASS", 0)),
        "per_class": classification_report(y_test, pred, target_names=list(LABELS),
                                           output_dict=True, zero_division=0),
        "confusion_matrix": confusion_matrix(y_test, pred, labels=[0, 1, 2]).tolist(),
    }
    (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    df = pd.DataFrame({
        "text": list(texts_test), "gold": [LABELS[i] for i in y_test],
        "pred": [LABELS[i] for i in pred], "confidence": conf.round(4),
        "action": actions, "correct": correct,
        **{f"p_{l}": p_test[:, i].round(4) for i, l in enumerate(LABELS)},
    })
    df.to_csv(outdir / "test_predictions.csv", index=False, encoding="utf-8")

    cov, risk, _ = risk_coverage_curve(conf, correct)
    np.savez(outdir / "curves.npz", coverage=cov, risk=risk,
             reliability_before=np.array(reliability_bins(p_test_raw, y_test)),
             reliability_after=np.array(reliability_bins(p_test, y_test)))
    _plots(name, metrics, cov, risk, p_test_raw, p_test, y_test, outdir)
    return metrics


def _plots(name, m, cov, risk, p_raw, p_cal, y, outdir: Path):
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    # Matriz de confusión
    cm = np.array(m["confusion_matrix"])
    fig, ax = plt.subplots(figsize=(4, 3.6), dpi=200)
    ax.imshow(cm, cmap="Blues")
    for i in range(3):
        for j in range(3):
            ax.text(j, i, cm[i, j], ha="center", va="center",
                    color="white" if cm[i, j] > cm.max() / 2 else "black", fontsize=10)
    ax.set_xticks(range(3), LABELS); ax.set_yticks(range(3), LABELS)
    ax.set_xlabel("Predicted"); ax.set_ylabel("Gold")
    ax.set_title(f"{name} — confusion matrix (test)", fontsize=9)
    fig.tight_layout(); fig.savefig(outdir / "confusion_matrix.png"); plt.close(fig)

    # Diagrama de fiabilidad antes / después
    fig, ax = plt.subplots(figsize=(4, 3.6), dpi=200)
    ax.plot([0, 1], [0, 1], ls="--", color="grey", lw=1, label="Perfect calibration")
    for probs, lab, mk in [(p_raw, f"Uncalibrated (ECE {m['ece_test_before']:.3f})", "o"),
                           (p_cal, f"T = {m['temperature']:.2f} (ECE {m['ece_test_after']:.3f})", "s")]:
        rows = reliability_bins(probs, y)
        ax.plot([r[1] for r in rows], [r[2] for r in rows], marker=mk, lw=1.2, label=lab)
    ax.set_xlabel("Mean confidence"); ax.set_ylabel("Accuracy")
    ax.set_xlim(0, 1); ax.set_ylim(0, 1); ax.legend(fontsize=7)
    ax.set_title(f"{name} — reliability (test)", fontsize=9)
    fig.tight_layout(); fig.savefig(outdir / "reliability.png"); plt.close(fig)

    # Curva risk–coverage con el punto de operación
    s = m["selective_test"]
    fig, ax = plt.subplots(figsize=(4.4, 3.6), dpi=200)
    ax.plot(cov, risk, lw=1.5, label=f"{name} (AURC {m['aurc_test']:.3f})")
    ax.axhline(m["error_rate_full_coverage"], ls=":", color="grey", lw=1, label="No abstention")
    ax.scatter([s["coverage"]], [s["selective_risk"]], color="crimson", zorder=3,
               label=f"τ = {s['tau']:.2f}: cov {s['coverage']:.2f}, risk {s['selective_risk']:.2f}")
    ax.set_xlabel("Coverage"); ax.set_ylabel("Selective risk (error rate)")
    ax.set_xlim(0, 1); ax.set_ylim(0, max(0.6, float(risk.max()) + 0.05)); ax.legend(fontsize=7)
    ax.set_title("Risk–coverage (test)", fontsize=9)
    fig.tight_layout(); fig.savefig(outdir / "risk_coverage.png"); plt.close(fig)
