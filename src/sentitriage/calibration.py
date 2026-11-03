"""Calibración por temperature scaling (Guo et al., 2017) y error de calibración (ECE).

Se ajusta un único escalar T sobre la partición de validación minimizando la
log-verosimilitud negativa. T > 1 suaviza las probabilidades (corrige sobreconfianza);
T < 1 las agudiza. T no cambia la clase predicha, solo la confianza.
"""
from __future__ import annotations

import numpy as np
from scipy.optimize import minimize_scalar


def softmax(logits: np.ndarray, temperature: float = 1.0) -> np.ndarray:
    z = np.asarray(logits, dtype=float) / temperature
    z = z - z.max(axis=1, keepdims=True)
    e = np.exp(z)
    return e / e.sum(axis=1, keepdims=True)


def nll(logits: np.ndarray, y: np.ndarray, temperature: float = 1.0) -> float:
    p = softmax(logits, temperature)
    return float(-np.mean(np.log(p[np.arange(len(y)), y] + 1e-12)))


def fit_temperature(logits: np.ndarray, y: np.ndarray) -> float:
    """Devuelve T que minimiza la NLL en validación (búsqueda en log T)."""
    res = minimize_scalar(lambda lt: nll(logits, y, float(np.exp(lt))),
                          bounds=(np.log(0.05), np.log(20.0)), method="bounded")
    return float(np.exp(res.x))


def expected_calibration_error(probs: np.ndarray, y: np.ndarray, n_bins: int = 15) -> float:
    """ECE con bins de igual ancho sobre la confianza máxima (Guo et al., 2017, Eq. 3)."""
    conf = probs.max(axis=1)
    correct = (probs.argmax(axis=1) == y).astype(float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    ece = 0.0
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (conf > lo) & (conf <= hi)
        if mask.any():
            ece += mask.mean() * abs(correct[mask].mean() - conf[mask].mean())
    return float(ece)


def reliability_bins(probs: np.ndarray, y: np.ndarray, n_bins: int = 10):
    conf = probs.max(axis=1)
    correct = (probs.argmax(axis=1) == y).astype(float)
    edges = np.linspace(0.0, 1.0, n_bins + 1)
    rows = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        mask = (conf > lo) & (conf <= hi)
        if mask.any():
            rows.append((float((lo + hi) / 2), float(conf[mask].mean()),
                         float(correct[mask].mean()), int(mask.sum())))
    return rows
