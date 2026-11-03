# Colombian restaurant comments — gold (n = 79)

| Model | Macro-F1 tweets → Colombia | Recall NEG | ECE (cal.) | AURC | Coverage at τ | Sel. risk | Missed complaints (no abst. → policy) |
|---|---|---|---|---|---|---|---|
| baseline-tfidf-lr | 53.9 → **63.0** | 0.73 | 0.194 | 0.153 | 0.37 | 0.10 | 14 → 1 |
| beto-sentitriage | 68.8 → **68.2** | 0.85 | 0.090 | 0.054 | 0.89 | 0.13 | 8 → 6 |
