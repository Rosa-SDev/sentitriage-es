# Model comparison — UMSAB Spanish test (n = 870)

| Model | Macro-F1 (95% CI) | Recall NEG | T | ECE before → after | AURC | τ | Coverage | Sel. risk | Missed complaints (no abst. → policy) |
|---|---|---|---|---|---|---|---|---|---|
| baseline-tfidf-lr | 53.9 (50.6–57.3) | 0.624 | 0.49 | 0.093 → 0.042 | 0.318 | 0.575 | 0.38 | 0.31 | 109 → 29 |
| beto-sentitriage | 68.8 (65.8–71.9) | 0.707 | 1.92 | 0.165 → 0.042 | 0.180 | 0.593 | 0.76 | 0.25 | 85 → 48 |
| xlmr-sentitriage | 66.0 (62.9–69.1) | 0.734 | 1.27 | 0.115 → 0.065 | 0.225 | 0.608 | 0.78 | 0.30 | 77 → 46 |

Published references (macro-F1, Spanish-only training): FastText [6] 50.1, XLM-R [6] 65.9, XLM-T [6] 68.5
