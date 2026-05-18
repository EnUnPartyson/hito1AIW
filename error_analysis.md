# Error Analysis — Hito 2

## Slice design

The notebook was sliced by:

- Strategy type: `no_stop`, `one_stop`, `two_stop`, `three_plus_stop`
- Circuit type: `street`, `permanent`, `semi-street`
- Additional context: `constructor_tier` and `weather_actual`

## Key results

### Strategy type

| Slice | `is_top10` Brier | `is_top5` Brier |
|---|---:|---:|
| `no_stop` | 0.0442 | 0.0281 |
| `one_stop` | 0.1559 | 0.1045 |
| `two_stop` | 0.1350 | 0.0899 |
| `three_plus_stop` | 0.1521 | 0.0967 |

The model is most stable on the rare `no_stop` cases, but the more informative comparison is among the common strategy classes. On both targets, `two_stop` is the best-performing common strategy slice, while `one_stop` and `three_plus_stop` are harder for the model.

### Circuit type

| Slice | `is_top10` Brier | `is_top5` Brier |
|---|---:|---:|
| `permanent` | 0.1391 | 0.0933 |
| `semi-street` | 0.1774 | 0.0848 |
| `street` | 0.1417 | 0.1104 |

`is_top10` is hardest on semi-street circuits, which is consistent with the idea that mixed-track character and race interruptions make the top-10 boundary noisier. `is_top5` is worst on street circuits, suggesting the podium/top-5 boundary is more fragile there.

### Additional context: constructor tier

| Slice | `is_top10` Brier | `is_top5` Brier |
|---|---:|---:|
| `backmarker` | 0.1295 | 0.0078 |
| `front` | 0.1121 | 0.1972 |
| `midfield` | 0.1700 | 0.1210 |

`is_top10` is hardest on midfield teams, which is a realistic failure mode: that is exactly where small strategy changes can swing the result. The `is_top5` score is worst for front-running teams because the model is making sharper top-end decisions there, and the boundary is much more sensitive to overconfidence.

### Additional context: weather

| Slice | `is_top10` Brier | `is_top5` Brier |
|---|---:|---:|
| `dry` | 0.1451 | 0.0923 |
| `wet` | 0.1425 | 0.1183 |

The `is_top5` model degrades in wet conditions, which is exactly where strategy confounding is strongest and where stop-count decisions tend to matter more.

## Failure-mode hypotheses

1. Two-stop strategies on street and semi-street circuits in wet races are the most likely place for probability drift, because the model has to combine race-control noise with pit-window timing.
2. Midfield constructors are the hardest `is_top10` slice because the model sits near the decision boundary: the same probability mass can move above or below the top-10 cutoff with small pace changes.
3. Front-running cases are hardest for `is_top5` because the model is asked to separate already-strong finishes from podium-contending finishes, which is where calibration errors are most visible.

## Visual evidence

The notebook includes calibration curves for both targets. The `is_top5` curve is tighter than `is_top10`, which is consistent with the lower Brier score, but both curves still show enough deviation from the diagonal to justify continued calibration work in Hito 2 follow-up modeling.
