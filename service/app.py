"""Microservicio HTTP de SentiTriage-ES (FastAPI).

Endpoints
- GET  /health            estado del servicio y modelo cargado
- GET  /model             metadatos: backend, T, τ, métricas de test
- POST /classify          {"text": "..."} -> decisión del agente
- POST /classify/batch    {"texts": [...]} -> lista de decisiones
- GET  /                  demo web (service/static/index.html)

Configuración: SENTITRIAGE_MODEL_DIR (por defecto BETO si está en models/, si no el baseline).
Kandela lo consumirá como un servicio más detrás de su API gateway; este proceso no
depende de Kandela y puede evaluarse y demostrarse solo.
"""
from __future__ import annotations

import logging
import os
import sys
import time
from pathlib import Path

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field

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


class BatchIn(BaseModel):
    texts: list[str] = Field(..., min_length=1, max_length=256)


def _safe_decision(text: str, probs) -> dict:
    d = decide(probs, predictor().tau).to_dict()
    d["text"] = text
    d["model"] = predictor().name
    return d


def _fallback(text: str, reason: str) -> dict:
    # Regla del artículo: si el modelo falla, la reseña nunca se acepta como no negativa.
    return {"text": text, "label": None, "confidence": None, "probabilities": None,
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
        out = _safe_decision(text, probs)
    except Exception as exc:  # noqa: BLE001
        log.exception("Fallo del modelo")
        out = _fallback(text, f"model_error: {exc}")
    out["latency_ms"] = round((time.perf_counter() - t0) * 1000, 1)
    return out


@app.post("/classify/batch")
def classify_batch(batch: BatchIn):
    texts = [t.strip() for t in batch.texts]
    try:
        probs = predictor().predict_proba(texts)
        return [_safe_decision(t, p) for t, p in zip(texts, probs)]
    except Exception as exc:  # noqa: BLE001
        log.exception("Fallo del modelo")
        return [_fallback(t, f"model_error: {exc}") for t in texts]


app.mount("/static", StaticFiles(directory=STATIC), name="static")


@app.get("/", include_in_schema=False)
def index():
    return FileResponse(STATIC / "index.html")
