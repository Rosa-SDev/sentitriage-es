# Colombian restaurant comments — weak (n = 4744)

| Model | Macro-F1 tweets → Colombia | Recall NEG | ECE (cal.) | AURC | Coverage at τ | Sel. risk | Missed complaints (no abst. → policy) |
|---|---|---|---|---|---|---|---|
| baseline-tfidf-lr | 53.9 → **52.4** | 0.73 | 0.041 | 0.252 | 0.38 | 0.23 | 516 → 77 |
| beto-sentitriage | 68.8 → **57.7** | 0.80 | 0.076 | 0.188 | 0.83 | 0.29 | 377 → 237 |
