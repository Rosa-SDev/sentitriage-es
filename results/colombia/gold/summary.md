# Colombian restaurant comments — gold (n = 90)

| Model | Macro-F1 tweets → Colombia | Recall NEG | ECE (cal.) | AURC | Coverage at τ | Sel. risk | Missed complaints (no abst. → policy) |
|---|---|---|---|---|---|---|---|
| baseline-tfidf-lr | 53.9 → **62.3** | 0.70 | 0.164 | 0.181 | 0.36 | 0.16 | 17 → 2 |
| beto-sentitriage | 68.8 → **69.0** | 0.82 | 0.111 | 0.072 | 0.86 | 0.16 | 10 → 7 |
