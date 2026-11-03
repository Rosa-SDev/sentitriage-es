"""Política de decisión del agente (artículo, Sec. IV-A).

- ABSTAIN: la confianza calibrada c(x) < τ  -> la reseña pasa a una persona.
- QUEUE:   confianza suficiente y clase negativa -> cola del administrador.
- PASS:    confianza suficiente y clase no negativa -> se almacena.

Regla de seguridad: si el modelo falla, la reseña nunca se marca como no negativa;
el servicio devuelve ABSTAIN.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict

import numpy as np

from . import LABELS, NEGATIVE

PASS, QUEUE, ABSTAIN = "PASS", "QUEUE", "ABSTAIN"


@dataclass
class Decision:
    label: str
    confidence: float
    probabilities: dict
    action: str
    abstained: bool
    threshold: float

    def to_dict(self) -> dict:
        return asdict(self)


def decide(probs: np.ndarray, tau: float) -> Decision:
    probs = np.asarray(probs, dtype=float)
    k = int(probs.argmax())
    conf = float(probs[k])
    if conf < tau:
        action = ABSTAIN
    elif k == NEGATIVE:
        action = QUEUE
    else:
        action = PASS
    return Decision(
        label=LABELS[k],
        confidence=round(conf, 4),
        probabilities={LABELS[i]: round(float(p), 4) for i, p in enumerate(probs)},
        action=action,
        abstained=action == ABSTAIN,
        threshold=round(float(tau), 4),
    )
