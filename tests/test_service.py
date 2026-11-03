import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

pytestmark = pytest.mark.skipif(
    not (ROOT / "models" / "baseline-tfidf-lr" / "sentitriage.json").exists(),
    reason="Ejecutar antes experiments/run_baseline.py")


@pytest.fixture(scope="module")
def client():
    from fastapi.testclient import TestClient
    import os
    os.environ["SENTITRIAGE_MODEL_DIR"] = str(ROOT / "models" / "baseline-tfidf-lr")
    from service.app import app
    return TestClient(app)


def test_health(client):
    assert client.get("/health").json()["status"] == "ok"


def test_classify_contract(client):
    d = client.post("/classify", json={"text": "La comida llegó fría y nadie nos atendió."}).json()
    assert d["label"] in {"negative", "neutral", "positive"}
    assert d["action"] in {"PASS", "QUEUE", "ABSTAIN"}
    assert abs(sum(d["probabilities"].values()) - 1) < 1e-3
    assert d["abstained"] == (d["confidence"] < d["threshold"])


def test_batch(client):
    out = client.post("/classify/batch", json={"texts": ["Excelente", "Horrible"]}).json()
    assert len(out) == 2


def test_rejects_empty(client):
    assert client.post("/classify", json={"text": ""}).status_code == 422


def test_model_failure_never_passes(client, monkeypatch):
    import service.app as app_mod

    def boom(_):
        raise RuntimeError("simulated failure")
    monkeypatch.setattr(app_mod.predictor(), "predict_proba", boom)
    d = client.post("/classify", json={"text": "Todo bien"}).json()
    assert d["action"] == "ABSTAIN" and d["label"] is None


def test_index(client):
    assert "SentiTriage" in client.get("/").text


def test_demo_page_is_self_contained(client):
    html = client.get("/").text
    # accesibilidad básica y sin recursos externos
    assert 'for="text"' in html and 'aria-live="polite"' in html
    assert "https://" not in html.split("<script>")[0]
    assert client.get("/static/fonts/IBMPlexSans-Regular.woff2").status_code == 200
