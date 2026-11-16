"""Experimento 5: dos preguntas que el artículo dejó abiertas en la Fase II.

(a) ¿Aporta la calibración a la abstención?
    Se compara la confianza calibrada c(x) = max softmax(z / T) con la softmax sin
    calibrar (T = 1). Para cada variante, τ se elige en validación de tuits con el mismo
    riesgo objetivo (0,25) y se aplica sin cambios a tuits de prueba y a los comentarios
    colombianos. Se reportan AURC, cobertura y riesgo selectivo.

(b) ¿Se reducen las quejas que pasan sin revisión si se escalan los neutrales dudosos?
    Política extendida: una predicción neutral con c(x) ≥ τ pasa a QUEUE (en vez de PASS)
    cuando p_negative ≥ δ. δ se elige solo en validación de tuits: el menor valor de la
    rejilla para el que al menos la mitad de las reseñas escaladas son realmente
    negativas. Se reportan las quejas que pasan sin revisión y la carga extra de la cola.

Nada se reentrena: se usan los modelos exportados en models/ y las etiquetas existentes.

Uso:  python experiments/policy_ablation.py
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import matplotlib  # noqa: E402
matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

from sentitriage import LABELS, NEGATIVE  # noqa: E402
from sentitriage.calibration import softmax  # noqa: E402
from sentitriage.data import load_split  # noqa: E402
from sentitriage.evaluate import DEFAULT_TARGET_RISK  # noqa: E402
from sentitriage.models import Predictor  # noqa: E402
from sentitriage.selective import aurc, choose_threshold, risk_coverage_curve, selective_stats  # noqa: E402

NEUTRAL = 1
MODELS = ["beto-sentitriage", "baseline-tfidf-lr"]
DELTAS = np.round(np.arange(0.10, 0.51, 0.05), 2)
OUT = ROOT / "results" / "policy_ablation"


def load_gold_labels():
    """Lee la etiqueta final acordada (results/colombia/gold_annotations.csv) sin escribir nada."""
    f = ROOT / "results" / "colombia" / "gold_annotations.csv"
    if not f.exists():
        return None
    g = pd.read_csv(f).dropna(subset=["final"])
    return pd.DataFrame({"text": g["text"], "label": g["final"].map({l: i for i, l in enumerate(LABELS)})})


def load_sets():
    sets = {"tweets_val": load_split("val"), "tweets_test": load_split("test")}
    gold = load_gold_labels()
    if gold is not None:
        sets["colombia_gold"] = gold
    sets["colombia_weak"] = pd.read_csv(ROOT / "data" / "colombia" / "delivery_weak.csv")[["text", "label"]]
    return sets


def actions(p, tau, delta=None):
    """PASS / QUEUE / ABSTAIN; con delta, los neutrales con p_neg ≥ delta van a QUEUE."""
    pred, conf = p.argmax(1), p.max(1)
    act = np.where(conf < tau, "ABSTAIN", np.where(pred == NEGATIVE, "QUEUE", "PASS"))
    if delta is not None:
        esc = (act == "PASS") & (pred == NEUTRAL) & (p[:, NEGATIVE] >= delta)
        act = np.where(esc, "QUEUE", act)
    return act


def policy_stats(p, y, tau, delta=None):
    act = actions(p, tau, delta)
    base = actions(p, tau)
    neg = y == NEGATIVE
    escalated = (act == "QUEUE") & (base != "QUEUE")
    return {
        "missed_complaints": int((neg & (act == "PASS")).sum()),
        "n_negative": int(neg.sum()),
        "queue_size": int((act == "QUEUE").sum()),
        "escalated": int(escalated.sum()),
        "escalated_truly_negative": int((escalated & neg).sum()),
    }


def choose_delta(p_val, y_val, tau):
    """Menor δ de la rejilla cuyo escalamiento en validación tiene precisión ≥ 0,5."""
    for d in DELTAS:
        s = policy_stats(p_val, y_val, tau, d)
        if s["escalated"] > 0 and s["escalated_truly_negative"] / s["escalated"] >= 0.5:
            return float(d)
    return None


def run_model(name, sets):
    pred = Predictor(ROOT / "models" / name)
    logits = {k: pred.logits(df["text"].tolist()) for k, df in sets.items()}
    ys = {k: np.asarray(df["label"]) for k, df in sets.items()}
    T = pred.temperature
    res = {"model": name, "temperature": T, "target_risk_val": DEFAULT_TARGET_RISK,
           "confidence": {}, "neutral_escalation": {}}

    # (a) calibrada vs. sin calibrar, τ elegido en validación para cada una
    curves = {}
    for variant, temp in (("uncalibrated", 1.0), ("calibrated", T)):
        pv = softmax(logits["tweets_val"], temp)
        tau = choose_threshold(pv.max(1), pv.argmax(1) == ys["tweets_val"], DEFAULT_TARGET_RISK)
        res["confidence"][variant] = {"temperature": temp, "tau": tau, "sets": {}}
        for k in sets:
            if k == "tweets_val":
                continue
            p = softmax(logits[k], temp)
            conf, correct = p.max(1), p.argmax(1) == ys[k]
            s = selective_stats(conf, correct, tau)
            s["aurc"] = aurc(conf, correct)
            res["confidence"][variant]["sets"][k] = s
            curves[(variant, k)] = risk_coverage_curve(conf, correct)[:2]

    # (b) escalamiento de neutrales dudosos (sobre la confianza calibrada)
    tau = res["confidence"]["calibrated"]["tau"]
    pv = softmax(logits["tweets_val"], T)
    delta = choose_delta(pv, ys["tweets_val"], tau)
    res["neutral_escalation"]["delta_chosen_on_val"] = delta
    res["neutral_escalation"]["sweep"] = {}
    for k in sets:
        p = softmax(logits[k], T)
        row = {"base": policy_stats(p, ys[k], tau)}
        if delta is not None:
            row["chosen_delta"] = policy_stats(p, ys[k], tau, delta)
        row["grid"] = {str(d): policy_stats(p, ys[k], tau, d) for d in DELTAS}
        res["neutral_escalation"]["sweep"][k] = row
    return res, curves


def plot(name, curves, sets):
    keys = [k for k in sets if k != "tweets_val"]
    fig, axes = plt.subplots(1, len(keys), figsize=(3.2 * len(keys), 2.8), sharey=True)
    titles = {"tweets_test": "Tweets (test)", "colombia_gold": "Colombia, human labels",
              "colombia_weak": "Colombia, rating labels"}
    for ax, k in zip(np.atleast_1d(axes), keys):
        for variant, style in (("uncalibrated", "--"), ("calibrated", "-")):
            cov, risk = curves[(variant, k)]
            ax.plot(cov, risk, style, lw=1.4, label=variant)
        ax.set_title(titles.get(k, k), fontsize=9)
        ax.set_xlabel("Coverage", fontsize=8)
        ax.tick_params(labelsize=7)
        ax.grid(alpha=0.3)
    np.atleast_1d(axes)[0].set_ylabel("Selective risk", fontsize=8)
    np.atleast_1d(axes)[0].legend(fontsize=7)
    fig.tight_layout()
    fig.savefig(OUT / name / "risk_coverage_calibrated_vs_raw.png", dpi=200)
    plt.close(fig)


def summary(all_res):
    lines = ["# Policy ablation\n",
             "## (a) Calibrated vs. uncalibrated confidence (τ chosen on tweet validation, target risk 0.25)\n",
             "| Model | Confidence | τ | Set | AURC | Coverage | Selective risk |",
             "|---|---|---|---|---|---|---|"]
    for r in all_res:
        for variant, v in r["confidence"].items():
            for k, s in v["sets"].items():
                lines.append(f"| {r['model']} | {variant} | {v['tau']:.3f} | {k} | {s['aurc']:.3f} | "
                             f"{s['coverage']:.2f} | {s['selective_risk']:.3f} |")
    lines += ["\n## (b) Escalating confident neutral predictions with high p_negative\n",
              "| Model | δ (val) | Set | Missed complaints: base → escalated | Queue size: base → escalated | Escalated (truly negative) |",
              "|---|---|---|---|---|---|"]
    notes = []
    for r in all_res:
        d = r["neutral_escalation"]["delta_chosen_on_val"]
        if d is None:
            notes.append(f"- {r['model']}: no δ in the grid reached an escalation precision ≥ 0.5 on "
                         "tweet validation, so the policy is not evaluated for this model.")
            continue
        for k, row in r["neutral_escalation"]["sweep"].items():
            b, c = row["base"], row["chosen_delta"]
            set_name = f"{k} (δ selection set)" if k == "tweets_val" else k
            lines.append(f"| {r['model']} | {d} | {set_name} | {b['missed_complaints']} → {c['missed_complaints']} "
                         f"(of {b['n_negative']}) | {b['queue_size']} → {c['queue_size']} | "
                         f"{c['escalated']} ({c['escalated_truly_negative']}) |")
    lines += ["",
              "δ is the smallest value in the grid whose escalated reviews on tweet validation are at "
              "least 50% truly negative. It is chosen on validation only; the other sets are reported "
              "with that δ fixed. This analysis is exploratory and does not change the service policy."]
    if notes:
        lines += [""] + notes
    (OUT / "summary.md").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print("\n".join(lines))


if __name__ == "__main__":
    sets = load_sets()
    all_res = []
    for name in MODELS:
        if not (ROOT / "models" / name / "sentitriage.json").exists():
            print(f"Se omite {name}: no está en models/")
            continue
        print(f"{name} ...", flush=True)
        r, curves = run_model(name, sets)
        (OUT / name).mkdir(parents=True, exist_ok=True)
        (OUT / name / "metrics.json").write_text(json.dumps(r, indent=2), encoding="utf-8")
        plot(name, curves, sets)
        all_res.append(r)
    summary(all_res)
