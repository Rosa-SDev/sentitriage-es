# SentiTriage-ES

Agente de triaje de sentimiento para reseñas en español que **se abstiene cuando no está
seguro**. Clasifica un texto como *negative*, *neutral* o *positive*, calibra su confianza
con *temperature scaling* y decide una acción:

| Acción | Condición | Efecto |
|---|---|---|
| `QUEUE` | c(x) ≥ τ y clase negativa | Va a la lista del administrador |
| `PASS` | c(x) ≥ τ y clase no negativa | Se almacena |
| `ABSTAIN` | c(x) < τ, o el modelo falla | La decide una persona |

c(x) = max softmax(z(x) / T). T y τ se ajustan en validación.

Proyecto de investigación de **Sistemas Inteligentes 2026B (Grupo 02), Universidad de
Ibagué**. Autores: Rosa Isabel Peña Yagüe y Daniel Esteban Guzmán Rodríguez.
Docente: Alexandra La Cruz Puente. El objeto de estudio es el agente y su evaluación;
[Kandela](https://github.com/Rosa-SDev/kandela) es el entorno de integración previsto.

## Estructura

```
src/sentitriage/      librería: datos, percepción, modelos, calibración, política, evaluación
experiments/          scripts reproducibles (EDA, baseline, comparación, análisis de errores)
notebooks/            fine-tuning de BETO y XLM-R en Google Colab (GPU)
service/              microservicio FastAPI + demo web
results/              métricas, predicciones y figuras generadas por los experimentos
models/               modelos exportados (no se versionan; se generan)
docs/decisions/       decisiones de arquitectura (ADR)
tests/                pruebas unitarias, del servicio y de humo del fine-tuning
```

## Inicio rápido (Python 3.10+)

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate    ·    Linux/macOS: source .venv/bin/activate
pip install -r requirements.txt

python scripts/download_data.py       # descarga el benchmark (3 archivos por partición)
python experiments/eda.py             # exploración del dataset
python experiments/run_baseline.py    # entrena y evalúa TF-IDF + LR, exporta el modelo
python -m pytest -q                   # pruebas

uvicorn service.app:app --port 8000   # demo en http://localhost:8000 · API en /docs
```

### Ejemplo de llamada

```bash
curl -X POST localhost:8000/classify -H "Content-Type: application/json" \
     -d '{"text": "Pedimos a domicilio y llegó todo frío. Pésimo servicio."}'
```

```json
{"label": "neutral", "confidence": 0.4518, "action": "ABSTAIN", "abstained": true,
 "threshold": 0.5753, "probabilities": {"negative": 0.35, "neutral": 0.45, "positive": 0.20}, ...}
```

## BETO y XLM-R

Se entrenan en Colab con `notebooks/02_finetune_transformers_colab.ipynb` (GPU T4,
≈ 20 min los dos). El notebook usa el mismo `src/sentitriage/finetune.py` y
`evaluate.py`, y descarga un zip con `results/` y `models/beto-sentitriage/`.
Para servir BETO localmente:

```bash
pip install -r requirements-transformers.txt
# Windows PowerShell
$env:SENTITRIAGE_MODEL_DIR="models/beto-sentitriage"; uvicorn service.app:app --port 8000
```

## Datos

- **Benchmark:** parte en español de UMSAB / XLM-T (Barbieri et al., LREC 2022),
  derivada de InterTASS 2017. Particiones oficiales: 1.839 / 324 / 870 tuits,
  balanceadas por clase. Fuente: `github.com/cardiffnlp/xlm-t`. Los textos provienen de
  Twitter, por eso no se redistribuyen en este repositorio; se descargan con el script.
- **Cambio de dominio:** comentarios de clientes de una plataforma colombiana de
  domicilios de restaurantes. Correa, J. C. (2019). *Raw data of Users' comments on Online
  Food Delivery Services* [Data set]. Mendeley Data, V1. https://doi.org/10.17632/k2v9sbmr8r.1
  (CC BY 4.0). Descargar `Comments.RData` en `data/external/` y ejecutar
  `python scripts/prepare_colombia.py`: deja 4.744 comentarios con etiqueta derivada de la
  calificación (20–40 negativo, 50–70 neutral, 80–100 positivo) y una muestra de 90 para
  etiquetado humano por los dos autores (kappa de Cohen).

## Estado (Fase II, 4 de noviembre de 2026)

| Componente | Estado |
|---|---|
| Datos, EDA, percepción | Hecho |
| Baseline TF-IDF + LR, calibración, abstención, risk–coverage | Hecho — `results/baseline-tfidf-lr/` |
| BETO y XLM-R | Hecho en Colab (T4) — `results/beto-sentitriage/`, `results/xlmr-sentitriage/` |
| Cambio de dominio, etiqueta por calificación (4.744) | Hecho — `results/colombia/weak/` |
| Cambio de dominio, etiqueta humana (90) | Hojas listas en `data/colombia/`; etiquetado en curso |
| Microservicio + demo web | Hecho |
| Integración con Kandela | Diseñada (ADR 0001), no implementada |
| Acción ALERT (ventana de negativos) | Fuera de alcance de esta fase |

Resultados actuales: `results/comparison.md` (tuits) y `results/colombia/weak/summary.md`
(comentarios colombianos). Para repetir la evaluación colombiana:
`python experiments/eval_colombia.py weak` (o `gold` cuando el etiquetado esté completo).

## Licencia de los datos

Los datos pertenecen a sus autores (InterTASS / SEPLN; UMSAB). Uso académico, sin
redistribución.
