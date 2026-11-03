"""Backends de clasificación intercambiables.

Todo modelo exportado vive en una carpeta con un `sentitriage.json`:

    {"type": "sklearn" | "transformers", "name": ..., "temperature": T, "tau": τ,
     "labels": [...], "max_length": ..., "metrics": {...}}

El servicio lee ese archivo y carga el backend correspondiente; cambiar del baseline a
BETO consiste en apuntar SENTITRIAGE_MODEL_DIR a otra carpeta.
"""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np

from ..calibration import softmax


class Predictor:
    def __init__(self, model_dir: str | Path):
        self.model_dir = Path(model_dir)
        self.meta = json.loads((self.model_dir / "sentitriage.json").read_text(encoding="utf-8"))
        self.temperature = float(self.meta.get("temperature", 1.0))
        self.tau = float(self.meta["tau"])
        kind = self.meta["type"]
        if kind == "sklearn":
            from .baseline import BaselineModel
            self._model = BaselineModel.load(self.model_dir)
        elif kind == "transformers":
            from .transformer import TransformerModel
            self._model = TransformerModel(self.model_dir, int(self.meta.get("max_length", 128)))
        else:
            raise ValueError(f"Tipo de modelo desconocido: {kind}")

    @property
    def name(self) -> str:
        return self.meta.get("name", self.model_dir.name)

    def logits(self, texts: list[str]) -> np.ndarray:
        return self._model.logits(texts)

    def predict_proba(self, texts: list[str]) -> np.ndarray:
        return softmax(self.logits(texts), self.temperature)
