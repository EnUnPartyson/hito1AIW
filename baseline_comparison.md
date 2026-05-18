# Baseline Comparison — Hito 2

## Summary

| Target | Main calibrated model | Test metric | Value | Baseline / reference |
|---|---|---:|---:|---:|
| `is_top10` | Calibrated logistic regression | Brier | 0.1447 | Docent floor: 0.1320 |
| `is_top5` | Calibrated logistic regression | Brier | 0.0958 | Heuristic baseline: 0.1227 |

## Interpretation

The calibrated logistic model is competitive on both targets, but it still sits above the docent floor on `is_top10`. That is the right way to read Hito 2: the model is no longer a toy heuristic, but it is not yet the final deployed product.

For the expansion target, the model improves over the justified heuristic baseline by 0.0269 Brier points ($0.1227 - 0.0958$). That matters because `is_top5` is the stricter target and is more sensitive to strategy trade-offs than `is_top10`.

## Notes

- `is_top10` remains the cohort-comparable target.
- `is_top5` is the expansion target chosen because it surfaces decision value beyond top-10 survival.
- The calibration block from 2022 is used only for probability calibration, not for model tuning.