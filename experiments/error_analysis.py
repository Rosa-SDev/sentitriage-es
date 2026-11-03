"""Análisis de errores a partir de results/<modelo>/test_predictions.csv.

Extrae ejemplos representativos: errores con alta confianza (los más peligrosos),
abstenciones que evitaron un error, y aciertos seguros. Escribe error_analysis.md.

Uso:  python experiments/error_analysis.py baseline-tfidf-lr
"""
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]


def table(df: pd.DataFrame) -> str:
    rows = ["| Text | Gold | Pred | Conf. | Action |", "|---|---|---|---|---|"]
    for r in df.itertuples():
        t = r.text.replace("|", "/")
        rows.append(f"| {t} | {r.gold} | {r.pred} | {r.confidence:.2f} | {r.action} |")
    return "\n".join(rows)


def main(name: str, k: int = 8):
    d = Path(ROOT / "results" / name)
    df = pd.read_csv(d / "test_predictions.csv")
    out = [f"# Error analysis — {name}\n",
           f"Test set: {len(df)} tweets. Accepted: {(df.action != 'ABSTAIN').sum()}, "
           f"abstained: {(df.action == 'ABSTAIN').sum()}.\n"]

    acc = df[df.action != "ABSTAIN"]
    out.append("## Confident errors (accepted and wrong)\n")
    out.append(table(acc[~acc.correct].sort_values("confidence", ascending=False).head(k)))
    out.append("\n\n## Complaints passed silently (gold negative, action PASS)\n")
    out.append(table(df[(df.gold == "negative") & (df.action == "PASS")]
                     .sort_values("confidence", ascending=False).head(k)))
    out.append("\n\n## Errors caught by abstention (wrong, but the agent abstained)\n")
    ab = df[(df.action == "ABSTAIN") & (~df.correct)]
    out.append(table(ab.sort_values("confidence").head(k)))
    out.append("\n\n## Confident correct decisions\n")
    out.append(table(acc[acc.correct].sort_values("confidence", ascending=False).head(k)))

    out.append("\n\n## Confusion between classes (all test, without abstention)\n")
    out.append(pd.crosstab(df.gold, df.pred).to_markdown())
    (d / "error_analysis.md").write_text("\n".join(out) + "\n", encoding="utf-8")
    print(f"-> {d / 'error_analysis.md'}")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "baseline-tfidf-lr")
