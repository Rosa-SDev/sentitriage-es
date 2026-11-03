"""Prepara el conjunto colombiano de comentarios de restaurantes (domicilios).

Fuente: Correa, J. C. (2019). Raw data of Users' comments on Online Food Delivery
Services [Data set]. Mendeley Data, V1. https://doi.org/10.17632/k2v9sbmr8r.1 (CC BY 4.0).
Comentarios en español de clientes de una plataforma colombiana de domicilios, con una
calificación de 0 a 100 dada por el mismo cliente.

Pasos
1. Limpieza: se descartan comentarios vacíos, con menos de 3 palabras y duplicados.
2. Etiqueta débil a partir de la calificación (misma regla que el artículo para estrellas):
   20-40 -> negative (1-2 estrellas), 50-70 -> neutral (3), 80-100 -> positive (4-5).
3. Muestra estratificada para etiquetado humano: 30 por clase débil, semilla 42.
   Se generan dos hojas idénticas, una por anotador, sin la calificación (para no sesgar).

Uso:  python scripts/prepare_colombia.py ruta/a/Comments.RData
"""
import sys
from pathlib import Path

import pandas as pd
import pyreadr

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "data" / "colombia"
LABELS = ("negative", "neutral", "positive")
N_PER_CLASS = 30


def weak_label(rating: float):
    if 20 <= rating <= 40:
        return 0
    if 50 <= rating <= 70:
        return 1
    if rating >= 80:
        return 2
    return None   # 0 y 10: casos aislados sin correspondencia con estrellas


def annotation_sheet(sample: pd.DataFrame, annotator: str, path: Path):
    from openpyxl import Workbook
    from openpyxl.styles import Alignment, Font, PatternFill
    from openpyxl.worksheet.datavalidation import DataValidation

    wb = Workbook()
    ws = wb.active
    ws.title = "Etiquetado"
    ws.append(["id", "comentario", "etiqueta", "nota (opcional)"])
    for c in ws[1]:
        c.font = Font(bold=True, color="FFFFFF")
        c.fill = PatternFill("solid", fgColor="1F3A68")
    for r in sample.itertuples():
        ws.append([r.id, r.text, "", ""])
    dv = DataValidation(type="list", formula1='"negative,neutral,positive"', allow_blank=False)
    ws.add_data_validation(dv)
    dv.add(f"C2:C{len(sample) + 1}")
    ws.column_dimensions["A"].width = 8
    ws.column_dimensions["B"].width = 95
    ws.column_dimensions["C"].width = 14
    ws.column_dimensions["D"].width = 30
    for row in ws.iter_rows(min_row=2):
        row[1].alignment = Alignment(wrap_text=True, vertical="top")
    ws.freeze_panes = "A2"

    g = wb.create_sheet("Instrucciones")
    for line in [
        f"Anotador/a: {annotator}",
        "Etiqueta cada comentario SOLO por su texto, sin consultar al otro anotador.",
        "negative: queja o experiencia mala (demora, pedido equivocado, comida fría o de mala calidad), aunque mencione algo bueno si lo que predomina es la queja.",
        "neutral: no expresa una valoración clara (pregunta, dato, saludo) o lo positivo y lo negativo pesan igual.",
        "positive: experiencia buena o recomendación.",
        "Si dudas, elige la que mejor describa lo que el restaurante debería hacer con el comentario y escribe la duda en 'nota'.",
        "No cambies los id ni el orden de las filas.",
    ]:
        g.append([line])
    g.column_dimensions["A"].width = 140
    wb.save(path)


def main(rdata: str):
    df = pyreadr.read_r(rdata)["UserComments"]
    n_raw = len(df)
    df = df.dropna(subset=["text"]).copy()
    df["text"] = df["text"].str.strip()
    df = df[df["text"].str.split().str.len() >= 3].drop_duplicates("text")
    df["label"] = df["Rating"].map(weak_label)
    df = df.dropna(subset=["label"]).astype({"label": int})
    df = df.rename(columns={"doc_id": "id", "Category": "category", "Provider": "provider",
                            "Rating": "rating"})[["id", "text", "category", "provider", "rating", "label"]]
    df["id"] = df["id"].astype(int)
    OUT.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT / "delivery_weak.csv", index=False, encoding="utf-8")
    print(f"Comentarios originales: {n_raw}  ->  tras limpieza: {len(df)}")
    print(df["label"].map(dict(enumerate(LABELS))).value_counts().to_string())

    pool = df[df["text"].str.split().str.len() <= 60]
    sample = (pd.concat([pool[pool["label"] == k].sample(N_PER_CLASS, random_state=42) for k in range(3)])
                .sample(frac=1, random_state=42).reset_index(drop=True))
    sample[["id", "text", "rating", "label"]].to_csv(OUT / "gold_sample_key.csv", index=False, encoding="utf-8")
    for who in ("Rosa", "Daniel"):
        annotation_sheet(sample, who, OUT / f"anotacion_{who}.xlsx")
    print(f"Muestra para etiquetado: {len(sample)} -> data/colombia/anotacion_Rosa.xlsx, anotacion_Daniel.xlsx")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else str(ROOT / "data" / "external" / "Comments.RData"))
