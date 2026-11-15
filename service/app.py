"""Microservicio HTTP de SentiTriage-ES (FastAPI).

Endpoints
- GET  /health            estado del servicio y modelo cargado
- GET  /model             metadatos: backend, T, τ, métricas de test
- POST /classify          {"text": "...", "id"?: "...", "metadata"?: {...}} -> decisión
- POST /classify/batch    {"items": [{"text", "id"?, "metadata"?}, ...]} o {"texts": [...]}

Contrato de integración: el servicio no sabe nada del negocio que lo llama. Recibe el
texto y, opcionalmente, un `id` y un objeto `metadata` del sistema cliente (pedido,
sucursal, canal...), que se devuelven sin modificar para que el cliente relacione cada
decisión con su registro. La respuesta siempre trae los campos `label`, `confidence`,
`probabilities`, `threshold` y `action` (PASS / QUEUE / ABSTAIN); si el modelo falla,
`action` es ABSTAIN, los demás vienen en null y se agrega `error`. Qué hace el negocio
con cada acción (almacenar, cola de quejas, revisión humana) queda en el sistema cliente.
- GET  /                  demo web (service/static/index.html)

Configuración: SENTITRIAGE_MODEL_DIR (por defecto BETO si está en models/, si no el baseline).
Cualquier sistema (por ejemplo, Kandela detrás de su API gateway, o el cliente de
examples/integration_client.py) lo consume por HTTP; este proceso no depende de ninguno.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, model_validator

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from sentitriage import __version__  # noqa: E402
from sentitriage.agent import ABSTAIN, decide  # noqa: E402
from sentitriage.models import Predictor  # noqa: E402

log = logging.getLogger("sentitriage")
_DEFAULT = ROOT / "models" / ("beto-sentitriage" if (ROOT / "models" / "beto-sentitriage" / "sentitriage.json").exists()
                               else "baseline-tfidf-lr")
MODEL_DIR = Path(os.environ.get("SENTITRIAGE_MODEL_DIR", _DEFAULT))
STATIC = Path(__file__).parent / "static"

app = FastAPI(title="SentiTriage-ES", version=__version__,
              description="Clasificación de sentimiento en español con abstención calibrada.")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["GET", "POST"], allow_headers=["*"])

_predictor: Predictor | None = None


def predictor() -> Predictor:
    global _predictor
    if _predictor is None:
        _predictor = Predictor(MODEL_DIR)
        log.info("Modelo cargado: %s (T=%.3f, tau=%.3f)", _predictor.name,
                 _predictor.temperature, _predictor.tau)
    return _predictor


class ReviewIn(BaseModel):
    text: str = Field(..., min_length=1, max_length=2000, examples=["La comida llegó fría y nadie nos atendió."])
    id: str | None = Field(None, max_length=128, description="Identificador del sistema cliente; se devuelve igual.")
    metadata: dict[str, Any] | None = Field(None, description="Datos del cliente (pedido, sucursal...); se devuelven igual.")


class BatchIn(BaseModel):
    items: list[ReviewIn] | None = Field(None, min_length=1, max_length=256)
    texts: list[str] | None = Field(None, min_length=1, max_length=256, description="Forma simple, sin id ni metadata.")

    @model_validator(mode="after")
    def _one_form(self):
        if (self.items is None) == (self.texts is None):
            raise ValueError("Envíe exactamente uno de los campos 'items' o 'texts'.")
        return self

    def reviews(self) -> list[ReviewIn]:
        return self.items if self.items is not None else [ReviewIn(text=t) for t in self.texts]


def _echo(out: dict, review: ReviewIn, text: str) -> dict:
    out["text"] = text
    out["id"] = review.id
    out["metadata"] = review.metadata
    return out


def _safe_decision(probs) -> dict:
    d = decide(probs, predictor().tau).to_dict()
    d["model"] = predictor().name
    return d


def _fallback(reason: str) -> dict:
    # Regla del artículo: si el modelo falla, la reseña nunca se acepta como no negativa.
    return {"label": None, "confidence": None, "probabilities": None,
            "action": ABSTAIN, "abstained": True, "threshold": None,
            "model": None, "error": reason}


@app.get("/health")
def health():
    try:
        p = predictor()
        return {"status": "ok", "model": p.name, "version": __version__}
    except Exception as exc:  # noqa: BLE001
        return {"status": "degraded", "error": str(exc), "version": __version__}


@app.get("/model")
def model_info():
    p = predictor()
    return {"name": p.name, "type": p.meta["type"], "temperature": p.temperature, "tau": p.tau,
            "labels": p.meta["labels"], "target_risk_val": p.meta.get("target_risk_val"),
            "metrics_test": p.meta.get("metrics_test", {})}


@app.post("/classify")
def classify(review: ReviewIn):
    text = review.text.strip()
    if not text:
        raise HTTPException(422, "El texto está vacío.")
    t0 = time.perf_counter()
    try:
        probs = predictor().predict_proba([text])[0]
        out = _safe_decision(probs)
    except Exception as exc:  # noqa: BLE001
        log.exception("Fallo del modelo")
        out = _fallback(f"model_error: {exc}")
    _echo(out, review, text)
    out["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return out


@app.post("/classify/batch")
def classify_batch(batch: BatchIn):
    reviews = batch.reviews()
    texts = [r.text.strip() for r in reviews]
    empty = [i for i, t in enumerate(texts) if not t]
    if empty:
        raise HTTPException(422, f"Textos vacíos en las posiciones {empty}.")
    try:
        probs = predictor().predict_proba(texts)
        outs = [_safe_decision(p) for p in probs]
    except Exception as exc:  # noqa: BLE001
        log.exception("Fallo del modelo")
        outs = [_fallback(f"model_error: {exc}") for _ in texts]
    return [_echo(o, r, t) for o, r, t in zip(outs, reviews, texts)]


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")
