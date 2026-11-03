"""Prueba de humo del bucle de fine-tuning con un BERT diminuto aleatorio (sin descargas).

Verifica que finetune.run entrena, evalúa con el protocolo común y exporta una carpeta
que el servicio puede cargar con Predictor. No mide calidad.
"""
import json
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

torch = pytest.importorskip("torch")
transformers = pytest.importorskip("transformers")


def test_finetune_pipeline(tmp_path):
    from transformers import BertConfig, BertForSequenceClassification, BertTokenizerFast

    from sentitriage.data import load_all
    from sentitriage.finetune import run
    from sentitriage.models import Predictor

    full = load_all()
    data = {k: v.groupby("label").head(20).reset_index(drop=True) for k, v in full.items()}

    words = sorted({w for t in data["train"]["text"] for w in t.lower().split()})[:500]
    vocab = tmp_path / "vocab.txt"
    vocab.write_text("\n".join(["[PAD]", "[UNK]", "[CLS]", "[SEP]", "[MASK]"] + words), encoding="utf-8")
    tok = BertTokenizerFast(vocab_file=str(vocab), do_lower_case=True)
    cfg = BertConfig(vocab_size=tok.vocab_size, hidden_size=32, num_hidden_layers=1,
                     num_attention_heads=2, intermediate_size=64, num_labels=3)
    model = BertForSequenceClassification(cfg)

    m = run("tiny-random-bert", "tiny", out_root=tmp_path, epochs=1, batch_size=8,
            max_length=32, data=data, model=model, tokenizer=tok)
    assert 0 <= m["macro_f1"] <= 1 and m["temperature"] > 0

    model_dir = tmp_path / "models" / "tiny-sentitriage"
    meta = json.loads((model_dir / "sentitriage.json").read_text())
    assert meta["type"] == "transformers"
    p = Predictor(model_dir)
    probs = p.predict_proba(["La comida estuvo deliciosa"])
    assert probs.shape == (1, 3) and abs(probs.sum() - 1) < 1e-5
