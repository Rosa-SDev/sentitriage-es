"""Carga del benchmark: parte en español de UMSAB / XLM-T (Barbieri et al., 2022).

Origen: https://github.com/cardiffnlp/xlm-t (data/sentiment/spanish), derivado de
InterTASS 2017. Etiquetas: 0 = negative, 1 = neutral, 2 = positive.
Se usan las particiones oficiales (train / val / test) sin modificarlas.
"""
from __future__ import annotations

import urllib.request
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = ROOT / "data" / "raw"
BASE_URL = "https://raw.githubusercontent.com/cardiffnlp/xlm-t/main/data/sentiment/spanish"
SPLITS = ("train", "val", "test")


def download(dest: Path = RAW_DIR, force: bool = False) -> None:
    dest.mkdir(parents=True, exist_ok=True)
    for split in SPLITS:
        for kind in ("text", "labels"):
            target = dest / f"{split}_{kind}.txt"
            if target.exists() and not force:
                continue
            urllib.request.urlretrieve(f"{BASE_URL}/{split}_{kind}.txt", target)


def _read_lines(path: Path) -> list[str]:
    # Los archivos no terminan en salto de línea: split("\n") conserva el último ejemplo.
    return path.read_text(encoding="utf-8").split("\n")


def load_split(split: str, raw_dir: Path = RAW_DIR) -> pd.DataFrame:
    texts = _read_lines(raw_dir / f"{split}_text.txt")
    labels = _read_lines(raw_dir / f"{split}_labels.txt")
    if len(texts) != len(labels):
        raise ValueError(f"{split}: {len(texts)} textos y {len(labels)} etiquetas")
    return pd.DataFrame({"text": texts, "label": [int(x) for x in labels]})


def load_all(raw_dir: Path = RAW_DIR) -> dict[str, pd.DataFrame]:
    return {s: load_split(s, raw_dir) for s in SPLITS}
