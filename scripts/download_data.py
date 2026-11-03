"""Descarga la parte en español de UMSAB/XLM-T a data/raw/ y verifica los tamaños."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from sentitriage.data import RAW_DIR, download, load_all  # noqa: E402

if __name__ == "__main__":
    download(force="--force" in sys.argv)
    for split, df in load_all().items():
        print(f"{split:5s}: {len(df):5d} ejemplos  ->  {RAW_DIR}")
