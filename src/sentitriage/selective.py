"""Clasificación selectiva (Geifman & El-Yaniv, 2017).

- Cobertura: fracción de entradas que el agente acepta (no abstiene).
- Riesgo selectivo: tasa de error sobre las entradas aceptadas.
- Curva risk–coverage: riesgo frente a cobertura al variar el umbral τ.
- AURC: área bajo esa curva (menor es mejor).
"""
from __future__ import annotations

import numpy as np


def risk_coverage_curve(confidence: np.ndarray, correct: np.ndarray):
    """Ordena por confianza descendente y acumula el error.

    Devuelve (coverage, risk, thresholds), uno por cada punto de corte posible.
    """
    order = np.argsort(-confidence, kind="stable")
    conf_sorted = confidence[order]
    err_sorted = 1.0 - correct[order].astype(float)
    n = len(confidence)
    k = np.arange(1, n + 1)
    coverage = k / n
    risk = np.cumsum(err_sorted) / k
    return coverage, risk, conf_sorted


def aurc(confidence: np.ndarray, correct: np.ndarray) -> float:
    coverage, risk, _ = risk_coverage_curve(confidence, correct)
    return float(np.mean(risk))   # promedio sobre los n puntos = área con paso 1/n


def selective_stats(confidence: np.ndarray, correct: np.ndarray, tau: float) -> dict:
    accepted = confidence >= tau
    cov = float(accepted.mean())
    risk = float(1.0 - correct[accepted].mean()) if accepted.any() else 0.0
    return {"tau": float(tau), "coverage": cov, "selective_risk": risk,
            "n_accepted": int(accepted.sum()), "n_abstained": int((~accepted).sum())}


def choose_threshold(confidence: np.ndarray, correct: np.ndarray, target_risk: float) -> float:
    """Menor τ (máxima cobertura) cuyo riesgo selectivo en validación es <= target_risk.

    Si ningún punto cumple, devuelve la confianza máxima (el agente casi siempre abstiene),
    lo cual es una señal explícita de que el objetivo es demasiado exigente para el modelo.
    """
    coverage, risk, thr = risk_coverage_curve(confidence, correct)
    ok = np.where(risk <= target_risk)[0]
    if len(ok) == 0:
        return float(thr[0])
    return float(thr[ok[-1]])
