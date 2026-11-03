"""Experimento 1: línea base TF-IDF + regresión logística.

1. Selecciona C por macro-F1 en validación (rejilla pequeña).
2. Reentrena con train (val queda reservada para T y τ).
3. Evalúa con el protocolo común (src/sentitriage/evaluate.py).
4. Exporta el modelo a models/baseline-tfidf-lr/ en el formato que carga el servicio.

Uso:  python experiments/run_baseline.py [--target-risk 0.20]
"""
import argparse
import json
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sklearn.metrics import f1_score  # noqa: E402

from sentitriage import LABELS  # noqa: E402
from sentitriage.data import load_all  # noqa: E402
from sentitriage.evaluate import DEFAULT_TARGET_RISK, evaluate  # noqa: E402
from sentitriage.models.baseline import BaselineModel, build_pipeline  # noqa: E402

GRID_C = [0.25, 0.5, 1.0, 2.0, 4.0, 8.0]
NAME = "baseline-tfidf-lr"


def main(target_risk: float):
    data = load_all()
    tr, va, te = data["train"], data["val"], data["test"]

    search = {}
    for C in GRID_C:
        m = BaselineModel(build_pipeline(C)).fit(tr["text"], tr["label"])
        search[C] = f1_score(va["label"], m.logits(va["text"]).argmax(1), average="macro")
        print(f"C={C:<5} macro-F1 val = {search[C]:.4f}")
    best_C = max(search, key=search.get)

    t0 = time.time()
    model = BaselineModel(build_pipeline(best_C)).fit(tr["text"], tr["label"])
    train_seconds = time.time() - t0

    outdir = ROOT / "results" / NAME
    metrics = evaluate(NAME, model.logits(va["text"]), va["label"].values,
                       model.logits(te["text"]), te["label"].values, te["text"].values,
                       outdir, target_risk=target_risk)
    metrics["hyperparameters"] = {"C": best_C, "grid_val_macro_f1": search,
                                  "features": "word 1-2 + char_wb 2-5 TF-IDF"}
    metrics["train_seconds"] = round(train_seconds, 2)
    (outdir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    model_dir = ROOT / "models" / NAME
    model.save(model_dir)
    (model_dir / "sentitriage.json").write_text(json.dumps({
        "type": "sklearn", "name": NAME, "labels": list(LABELS),
        "temperature": metrics["temperature"], "tau": metrics["selective_test"]["tau"],
        "target_risk_val": target_risk,
        "metrics_test": {k: metrics[k] for k in ("macro_f1", "accuracy", "recall_negative",
                                                 "ece_test_after", "aurc_test")},
    }, indent=2), encoding="utf-8")

    keys = ["accuracy", "macro_f1", "macro_f1_ci95", "recall_negative", "temperature",
            "ece_test_before", "ece_test_after", "aurc_test", "selective_test",
            "true_negatives_by_action"]
    print(json.dumps({k: metrics[k] for k in keys}, indent=2))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--target-risk", type=float, default=DEFAULT_TARGET_RISK)
    main(ap.parse_args().target_risk)
