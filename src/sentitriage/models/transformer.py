"""Backend transformer (BETO o XLM-R) para inferencia.

Carga una carpeta exportada por notebooks/02_finetune_transformers_colab.ipynb
(formato `save_pretrained` de Hugging Face + sentitriage.json). torch y transformers
se importan solo aquí, para que el baseline y las pruebas no dependan de ellos.
"""
from __future__ import annotations

from pathlib import Path

import numpy as np

from ..preprocess import normalize


class TransformerModel:
    def __init__(self, model_dir: Path, max_length: int = 128, batch_size: int = 32):
        import torch
        from transformers import AutoModelForSequenceClassification, AutoTokenizer

        self.torch = torch
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.tokenizer = AutoTokenizer.from_pretrained(model_dir)
        self.model = AutoModelForSequenceClassification.from_pretrained(model_dir).to(self.device).eval()
        self.max_length = max_length
        self.batch_size = batch_size

    def logits(self, texts) -> np.ndarray:
        out = []
        texts = [normalize(t) for t in texts]
        with self.torch.no_grad():
            for i in range(0, len(texts), self.batch_size):
                enc = self.tokenizer(texts[i:i + self.batch_size], truncation=True,
                                     max_length=self.max_length, padding=True,
                                     return_tensors="pt").to(self.device)
                out.append(self.model(**enc).logits.float().cpu().numpy())
        return np.concatenate(out, axis=0)
