# Policy ablation

## (a) Calibrated vs. uncalibrated confidence (τ chosen on tweet validation, target risk 0.25)

| Model | Confidence | τ | Set | AURC | Coverage | Selective risk |
|---|---|---|---|---|---|---|
| beto-sentitriage | uncalibrated | 0.754 | tweets_test | 0.180 | 0.75 | 0.254 |
| beto-sentitriage | uncalibrated | 0.754 | colombia_gold | 0.079 | 0.84 | 0.158 |
| beto-sentitriage | uncalibrated | 0.754 | colombia_weak | 0.189 | 0.83 | 0.289 |
| beto-sentitriage | calibrated | 0.593 | tweets_test | 0.180 | 0.76 | 0.254 |
| beto-sentitriage | calibrated | 0.593 | colombia_gold | 0.072 | 0.86 | 0.156 |
| beto-sentitriage | calibrated | 0.593 | colombia_weak | 0.188 | 0.83 | 0.289 |
| baseline-tfidf-lr | uncalibrated | 0.470 | tweets_test | 0.320 | 0.31 | 0.278 |
| baseline-tfidf-lr | uncalibrated | 0.470 | colombia_gold | 0.183 | 0.27 | 0.125 |
| baseline-tfidf-lr | uncalibrated | 0.470 | colombia_weak | 0.256 | 0.32 | 0.214 |
| baseline-tfidf-lr | calibrated | 0.575 | tweets_test | 0.318 | 0.38 | 0.312 |
| baseline-tfidf-lr | calibrated | 0.575 | colombia_gold | 0.181 | 0.36 | 0.156 |
| baseline-tfidf-lr | calibrated | 0.575 | colombia_weak | 0.252 | 0.38 | 0.233 |

## (b) Escalating confident neutral predictions with high p_negative

| Model | δ (val) | Set | Missed complaints: base → escalated | Queue size: base → escalated | Escalated (truly negative) |
|---|---|---|---|---|---|
| beto-sentitriage | 0.25 | tweets_val (δ selection set) | 17 → 13 (of 108) | 92 → 99 | 7 (4) |
| beto-sentitriage | 0.25 | tweets_test | 48 → 40 (of 290) | 228 → 252 | 24 (8) |
| beto-sentitriage | 0.25 | colombia_gold | 7 → 6 (of 56) | 43 → 45 | 2 (1) |
| beto-sentitriage | 0.25 | colombia_weak | 237 → 174 (of 1918) | 1976 → 2085 | 109 (63) |

δ is the smallest value in the grid whose escalated reviews on tweet validation are at least 50% truly negative. It is chosen on validation only; the other sets are reported with that δ fixed. This analysis is exploratory and does not change the service policy.

- baseline-tfidf-lr: no δ in the grid reached an escalation precision ≥ 0.5 on tweet validation, so the policy is not evaluated for this model.
