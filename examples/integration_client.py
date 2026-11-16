"""Ejemplo de integración: un sistema externo envía sus reseñas a SentiTriage-ES.

Simula lo que haría cualquier negocio (un restaurante, una tienda en línea, un sistema
de PQR): toma sus reseñas de un CSV, las envía al servicio por HTTP y reparte el
resultado según la acción del agente. Solo usa la biblioteca estándar de Python, para
mostrar que el cliente no necesita nada del proyecto.

Entrada: CSV con columnas `id` y `text`; cualquier otra columna viaja como `metadata`
y vuelve sin cambios.

Uso:
    uvicorn service.app:app --port 8000          # en otra terminal
    python examples/integration_client.py examples/sample_reviews.csv
    python examples/integration_client.py reviews.csv --url http://host:8000 --out decisions.csv
"""
import argparse
import csv
import json
import sys
import urllib.request
from collections import defaultdict

BATCH = 256  # máximo por petición en POST /classify/batch


def classify(url: str, items: list[dict]) -> list[dict]:
    out = []
    for i in range(0, len(items), BATCH):
        body = json.dumps({"items": items[i:i + BATCH]}).encode("utf-8")
        req = urllib.request.Request(f"{url}/classify/batch", data=body,
                                     headers={"Content-Type": "application/json"})
        with urllib.request.urlopen(req, timeout=120) as resp:
            out.extend(json.loads(resp.read().decode("utf-8")))
    return out


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("csv", help="CSV con columnas id y text")
    ap.add_argument("--url", default="http://localhost:8000")
    ap.add_argument("--out", default="decisions.csv")
    args = ap.parse_args()

    with open(args.csv, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    items = [{"id": r.pop("id"), "text": r.pop("text"), "metadata": r or None} for r in rows]

    decisions = classify(args.url, items)

    with open(args.out, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["id", "action", "label", "confidence", "threshold", "metadata", "text"])
        for d in decisions:
            w.writerow([d["id"], d["action"], d["label"], d["confidence"], d["threshold"],
                        json.dumps(d["metadata"], ensure_ascii=False), d["text"]])

    by_action = defaultdict(list)
    for d in decisions:
        by_action[d["action"]].append(d)
    print(f"{len(decisions)} reseñas · modelo {decisions[0]['model'] if decisions else '-'}")
    for action, meaning in (("QUEUE", "cola de quejas"), ("ABSTAIN", "revisión humana"),
                            ("PASS", "almacenadas")):
        group = by_action.get(action, [])
        print(f"\n{action} ({meaning}): {len(group)}")
        for d in group:
            conf = "-" if d["confidence"] is None else f"{d['confidence']:.2f}"
            print(f"  {d['id']:<10} {conf}  {d['text'][:70]}")
    print(f"\nDecisiones guardadas en {args.out}")


if __name__ == "__main__":
    sys.exit(main())
