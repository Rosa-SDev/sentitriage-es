"""Exploración del dataset: tamaños, distribución de clases y longitud de los textos.

Uso:  python experiments/eda.py
Salida: results/eda/eda.json, class_distribution.png, length_distribution.png
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

from sentitriage import LABELS  # noqa: E402
from sentitriage.data import load_all  # noqa: E402
from sentitriage.preprocess import normalize  # noqa: E402

OUT = ROOT / "results" / "eda"


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    data = load_all()
    summary = {}
    for split, df in data.items():
        words = df["text"].str.split().str.len()
        summary[split] = {
            "n": int(len(df)),
            "class_counts": {LABELS[k]: int(v) for k, v in df["label"].value_counts().sort_index().items()},
            "words_mean": float(words.mean()), "words_median": float(words.median()),
            "words_max": int(words.max()),
            "with_user_mention": int(df["text"].str.contains("@user").sum()),
            "with_url": int(df["text"].str.contains("http").sum()),
            "duplicates_within_split": int(df["text"].duplicated().sum()),
        }
    tr, te = set(data["train"]["text"]), set(data["test"]["text"])
    summary["overlap_train_test"] = len(tr & te)
    summary["normalization_examples"] = [
        {"original": t, "normalized": normalize(t)}
        for t in data["train"]["text"].head(200) if normalize(t) != t
    ][:5]
    (OUT / "eda.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False), encoding="utf-8")

    fig, ax = plt.subplots(figsize=(5, 3.2), dpi=200)
    x = np.arange(3)
    for i, split in enumerate(["train", "val", "test"]):
        counts = [summary[split]["class_counts"][l] for l in LABELS]
        ax.bar(x + (i - 1) * 0.27, counts, width=0.27, label=f"{split} (n={summary[split]['n']})")
    ax.set_xticks(x, LABELS); ax.set_ylabel("Tweets"); ax.legend(fontsize=7)
    ax.set_title("Class distribution — UMSAB Spanish (InterTASS)", fontsize=9)
    fig.tight_layout(); fig.savefig(OUT / "class_distribution.png"); plt.close(fig)

    fig, ax = plt.subplots(figsize=(5, 3.2), dpi=200)
    for k, lab in enumerate(LABELS):
        w = data["train"].loc[data["train"]["label"] == k, "text"].str.split().str.len()
        ax.hist(w, bins=30, alpha=0.5, label=lab)
    ax.set_xlabel("Words per tweet (train)"); ax.set_ylabel("Count"); ax.legend(fontsize=7)
    fig.tight_layout(); fig.savefig(OUT / "length_distribution.png"); plt.close(fig)

    print(json.dumps({k: v for k, v in summary.items() if k != "normalization_examples"}, indent=2))


if __name__ == "__main__":
    main()
