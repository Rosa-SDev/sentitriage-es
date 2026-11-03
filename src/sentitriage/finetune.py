"""Fine-tuning de un encoder (BETO o XLM-R) para clasificación de 3 clases.

Arquitectura (clase "Encoder-only LLMs"): el encoder produce un vector contextual del
token [CLS]; una capa lineal lo proyecta a 3 logits (negative / neutral / positive) y
se entrena todo el modelo con entropía cruzada. Se usa un bucle de PyTorch explícito
(sin `Trainer`) para que cada paso sea visible y no dependa de la versión de transformers.

Selección de época: la de mejor macro-F1 en validación. La misma partición se usa
después para T y τ; esto se declara como limitación (validación de 324 tuits).

Uso típico (Colab, GPU):
    from sentitriage.finetune import run
    run("dccuchile/bert-base-spanish-wwm-cased", "beto", out_root="/content/out")
"""
from __future__ import annotations

import json
import random
import time
from pathlib import Path

import numpy as np

from . import LABELS
from .data import load_all
from .evaluate import DEFAULT_TARGET_RISK, evaluate
from .preprocess import normalize

MODELS = {
    "beto": "dccuchile/bert-base-spanish-wwm-cased",
    "xlmr": "FacebookAI/xlm-roberta-base",
}


def set_seed(seed: int):
    import torch
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)
    if torch.cuda.is_available():
        torch.cuda.manual_seed_all(seed)


def _batches(enc, labels, batch_size, shuffle, rng):
    idx = np.arange(len(labels))
    if shuffle:
        rng.shuffle(idx)
    for i in range(0, len(idx), batch_size):
        b = idx[i:i + batch_size]
        yield {k: v[b] for k, v in enc.items()}, labels[b]


def predict_logits(model, tokenizer, texts, max_length, device, batch_size=64):
    import torch
    model.eval()
    out = []
    with torch.no_grad():
        for i in range(0, len(texts), batch_size):
            enc = tokenizer([normalize(t) for t in texts[i:i + batch_size]], truncation=True,
                            max_length=max_length, padding=True, return_tensors="pt").to(device)
            out.append(model(**enc).logits.float().cpu().numpy())
    return np.concatenate(out, axis=0)


def run(model_name: str, short_name: str, out_root: str | Path = "outputs",
        epochs: int = 4, lr: float = 2e-5, batch_size: int = 16, max_length: int = 128,
        weight_decay: float = 0.01, warmup_ratio: float = 0.1, seed: int = 42,
        target_risk: float = DEFAULT_TARGET_RISK, data=None, model=None, tokenizer=None) -> dict:
    """Entrena, evalúa con el protocolo común y exporta en formato del servicio.

    `data`, `model` y `tokenizer` permiten inyectar objetos en las pruebas.
    """
    import torch
    from transformers import (AutoModelForSequenceClassification, AutoTokenizer,
                              get_linear_schedule_with_warmup)
    from sklearn.metrics import f1_score

    set_seed(seed)
    device = "cuda" if torch.cuda.is_available() else "cpu"
    data = data or load_all()
    tr, va, te = data["train"], data["val"], data["test"]

    tokenizer = tokenizer or AutoTokenizer.from_pretrained(model_name)
    model = model or AutoModelForSequenceClassification.from_pretrained(
        model_name, num_labels=3,
        id2label=dict(enumerate(LABELS)), label2id={l: i for i, l in enumerate(LABELS)})
    model.to(device)

    enc = tokenizer([normalize(t) for t in tr["text"]], truncation=True, max_length=max_length,
                    padding="max_length", return_tensors="pt")
    y_tr = torch.tensor(tr["label"].values)

    opt = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=weight_decay)
    steps = epochs * int(np.ceil(len(tr) / batch_size))
    sched = get_linear_schedule_with_warmup(opt, int(warmup_ratio * steps), steps)
    rng = np.random.default_rng(seed)

    out_root = Path(out_root)
    model_dir = out_root / "models" / f"{short_name}-sentitriage"
    best_f1, history, t0 = -1.0, [], time.time()
    for ep in range(1, epochs + 1):
        model.train()
        losses = []
        for xb, yb in _batches(enc, y_tr, batch_size, True, rng):
            xb = {k: v.to(device) for k, v in xb.items()}
            loss = model(**xb, labels=yb.to(device)).loss
            loss.backward()
            torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)
            opt.step(); sched.step(); opt.zero_grad()
            losses.append(loss.item())
        val_logits = predict_logits(model, tokenizer, va["text"].tolist(), max_length, device)
        f1 = f1_score(va["label"], val_logits.argmax(1), average="macro")
        history.append({"epoch": ep, "train_loss": float(np.mean(losses)), "val_macro_f1": float(f1)})
        print(f"[{short_name}] epoch {ep}: loss {np.mean(losses):.4f}  val macro-F1 {f1:.4f}")
        if f1 > best_f1:
            best_f1 = f1
            model.save_pretrained(model_dir); tokenizer.save_pretrained(model_dir)
    train_seconds = time.time() - t0

    # Recarga la mejor época y evalúa con el protocolo común
    model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(device)
    lv = predict_logits(model, tokenizer, va["text"].tolist(), max_length, device)
    lt = predict_logits(model, tokenizer, te["text"].tolist(), max_length, device)
    res_dir = out_root / "results" / f"{short_name}-sentitriage"
    metrics = evaluate(f"{short_name}-sentitriage", lv, va["label"].values, lt, te["label"].values,
                       te["text"].values, res_dir, target_risk=target_risk)
    metrics["hyperparameters"] = {"base_model": model_name, "epochs": epochs, "lr": lr,
                                  "batch_size": batch_size, "max_length": max_length,
                                  "weight_decay": weight_decay, "warmup_ratio": warmup_ratio,
                                  "seed": seed, "device": device,
                                  "best_epoch": int(np.argmax([h["val_macro_f1"] for h in history]) + 1)}
    metrics["history"] = history
    metrics["train_seconds"] = round(train_seconds, 1)
    (res_dir / "metrics.json").write_text(json.dumps(metrics, indent=2, ensure_ascii=False), encoding="utf-8")

    (model_dir / "sentitriage.json").write_text(json.dumps({
        "type": "transformers", "name": f"{short_name}-sentitriage", "base_model": model_name,
        "labels": list(LABELS), "max_length": max_length,
        "temperature": metrics["temperature"], "tau": metrics["selective_test"]["tau"],
        "target_risk_val": target_risk,
        "metrics_test": {k: metrics[k] for k in ("macro_f1", "accuracy", "recall_negative",
                                                 "ece_test_after", "aurc_test")},
    }, indent=2), encoding="utf-8")
    return metrics
