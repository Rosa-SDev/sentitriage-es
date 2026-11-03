# Model comparison — UMSAB Spanish test (n = 870)

| Model | Macro-F1 (95% CI) | Recall NEG | T | ECE before → after | AURC | τ | Coverage | Sel. risk | Missed complaints (no abst. → policy) |
|---|---|---|---|---|---|---|---|---|---|
| baseline-tfidf-lr | 53.9 (50.6–57.3) | 0.624 | 0.49 | 0.093 → 0.042 | 0.318 | 0.575 | 0.38 | 0.31 | 109 → 29 |

Published references (macro-F1, Spanish-only training): FastText [6] 50.1, XLM-R [6] 65.9, XLM-T [6] 68.5
