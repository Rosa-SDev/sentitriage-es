"""Experimento 4: cambio de dominio a comentarios colombianos de restaurantes.

Cada modelo se aplica con la T y el τ que se ajustaron con tuits; no se reentrena ni se
recalibra nada. Así se mide lo que pasaría al desplegar el agente tal como está.

Conjuntos
- weak: 4.744 comentarios con etiqueta derivada de la calificación del cliente
  (data/colombia/delivery_weak.csv; ver scripts/prepare_colombia.py).
- gold: muestra de 90 comentarios etiquetados por los dos autores. Se usa solo si
  existen data/colombia/anotacion_Rosa.xlsx y anotacion_Daniel.xlsx completos; se
  reporta el kappa de Cohen y la etiqueta final es la acordada (los desacuerdos se
  resuelven en data/colombia/gold_adjudicated.csv si existe, o se excluyen).

Uso:  python experiments/eval_colombia.py [weak|gold|all]
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

import pandas as pd  # noqa: E402
from sklearn.metrics import cohen_kappa_score  # noqa: E402

from sentitriage import LABELS  # noqa: E402
from sentitriage.evaluate import evaluate_fixed  # noqa: E402
from sentitriage.models import Predictor  # noqa: E402

DATA = ROOT / "data" / "colombia"
RES = ROOT / "results" / "colombia"
MODELS = ["baseline-tfidf-lr", "beto-sentitriage", "xlmr-sentitriage"]
L2I = {l: i for i, l in enumerate(LABELS)}


def available_models():
    for name in MODELS:
        if (ROOT / "models" / name / "sentitriage.json").exists():
            yield name, Predictor(ROOT / "models" / name)


def tweets_reference(name):
    f = ROOT / "results" / name / "metrics.json"
    return json.loads(f.read_text(encoding="utf-8")) if f.exists() else None


def run(set_name: str, df: pd.DataFrame):
    out = {}
    for name, pred in available_models():
        print(f"[{set_name}] {name}: {len(df)} textos ...", flush=True)
        m = evaluate_fixed(name, pred.logits(df["text"].tolist()), df["label"].values,
                           df["text"].values, pred.temperature, pred.tau,
                           RES / set_name / name, reference=tweets_reference(name))
        out[name] = m
    return out


def load_gold():
    sheets = {}
    for who in ("Rosa", "Daniel"):
        f = DATA / f"anotacion_{who}.xlsx"
        if not f.exists():
            return None
        s = pd.read_excel(f, sheet_name="Etiquetado")
        s["etiqueta"] = s["etiqueta"].astype(str).str.strip().str.lower()
        if not s["etiqueta"].isin(LABELS).all():
            print(f"anotacion_{who}.xlsx incompleto: {(~s['etiqueta'].isin(LABELS)).sum()} filas sin etiqueta")
            return None
        sheets[who] = s.set_index("id")["etiqueta"]
    key = pd.read_csv(DATA / "gold_sample_key.csv").set_index("id")
    a, b = sheets["Rosa"].loc[key.index], sheets["Daniel"].loc[key.index]
    kappa = cohen_kappa_score(a, b)
    agree = (a == b)
    gold = key.assign(rosa=a, daniel=b, agree=agree)
    adj = DATA / "gold_adjudicated.csv"
    if adj.exists():
        res = pd.read_csv(adj).set_index("id")["label_final"]
        gold["final"] = gold["rosa"].where(agree, res.reindex(gold.index))
    else:
        gold["final"] = gold["rosa"].where(agree)
    gold["weak"] = gold["label"].map(dict(enumerate(LABELS)))
    stats = {"n": int(len(gold)), "cohen_kappa": float(kappa), "raw_agreement": float(agree.mean()),
             "n_disagreements": int((~agree).sum()),
             "weak_vs_human_agreement": float((gold["weak"] == gold["final"]).mean()),
             "adjudicated": adj.exists()}
    RES.mkdir(parents=True, exist_ok=True)
    gold.reset_index().to_csv(RES / "gold_annotations.csv", index=False, encoding="utf-8")
    (RES / "annotation_agreement.json").write_text(json.dumps(stats, indent=2), encoding="utf-8")
    print(json.dumps(stats, indent=2))
    g = gold.dropna(subset=["final"]).reset_index()
    return pd.DataFrame({"text": g["text"], "label": g["final"].map(L2I)})


def summary(results: dict, set_name: str):
    rows = ["| Model | Macro-F1 tweets → Colombia | Recall NEG | ECE (cal.) | AURC | Coverage at τ | Sel. risk | Missed complaints (no abst. → policy) |",
            "|---|---|---|---|---|---|---|---|"]
    for name, m in results.items():
        r = m.get("reference_tweets") or {}
        s = m["selective"]
        rows.append(f"| {name} | {100*r.get('macro_f1', float('nan')):.1f} → **{100*m['macro_f1']:.1f}** | "
                    f"{m['recall_negative']:.2f} | {m['ece_after']:.3f} | {m['aurc']:.3f} | {s['coverage']:.2f} | "
                    f"{s['selective_risk']:.2f} | {m['missed_negatives_without_abstention']} → {m['missed_negatives_with_policy']} |")
    text = f"# Colombian restaurant comments — {set_name} (n = {next(iter(results.values()))['n']})\n\n" + "\n".join(rows) + "\n"
    (RES / set_name / "summary.md").write_text(text, encoding="utf-8")
    print(text)


if __name__ == "__main__":
    which = sys.argv[1] if len(sys.argv) > 1 else "all"
    if which in ("weak", "all"):
        weak = pd.read_csv(DATA / "delivery_weak.csv")
        summary(run("weak", weak), "weak")
    if which in ("gold", "all"):
        gold = load_gold()
        if gold is None:
            print("Etiquetado humano pendiente: se omite el conjunto gold.")
        else:
            summary(run("gold", gold), "gold")
