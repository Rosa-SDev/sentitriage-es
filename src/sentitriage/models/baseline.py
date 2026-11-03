"""Línea base clásica: TF-IDF + regresión logística (temas del curso).

Se combinan n-gramas de palabras (1-2) y de caracteres (2-5, dentro de palabra).
Los de caracteres hacen al modelo menos sensible a errores de ortografía y a
variaciones como "buenísimo"/"buenisimo", frecuentes en tuits y reseñas.
Los logits son la función de decisión de la regresión logística multinomial, de modo
que softmax(logits) = predict_proba y el temperature scaling se aplica igual que en
los transformers.
"""
from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import FeatureUnion, Pipeline

from ..preprocess import normalize


def build_pipeline(C: float = 1.0, seed: int = 42) -> Pipeline:
    features = FeatureUnion([
        ("word", TfidfVectorizer(ngram_range=(1, 2), min_df=2, sublinear_tf=True, lowercase=True)),
        ("char", TfidfVectorizer(analyzer="char_wb", ngram_range=(2, 5), min_df=2,
                                 sublinear_tf=True, lowercase=True)),
    ])
    clf = LogisticRegression(C=C, max_iter=2000, random_state=seed)
    return Pipeline([("tfidf", features), ("clf", clf)])


class BaselineModel:
    FILE = "baseline.joblib"

    def __init__(self, pipeline: Pipeline):
        self.pipeline = pipeline

    def fit(self, texts, y):
        self.pipeline.fit([normalize(t) for t in texts], y)
        return self

    def logits(self, texts) -> np.ndarray:
        return self.pipeline.decision_function([normalize(t) for t in texts])

    def save(self, model_dir: Path) -> None:
        model_dir.mkdir(parents=True, exist_ok=True)
        joblib.dump(self.pipeline, model_dir / self.FILE)

    @classmethod
    def load(cls, model_dir: Path) -> "BaselineModel":
        return cls(joblib.load(Path(model_dir) / cls.FILE))
