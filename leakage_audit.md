# Leakage Audit — Hito 2

## Checklist results

- `is_top10` is taken directly from the official race-level file and is not reconstructed from lap-level artifacts.
- `is_top5` is derived only from official `finish_position` in the same race-level file.
- `n_stops` and `compound_sequence` are treated as scenario inputs only. They are allowed in the what-if comparison because the product is a counterfactual strategy tool, not a pre-race oracle.
- `qualifying_time_s` remains excluded because it is empty / unreliable in the dataset.
- `finish_position`, `points`, and other post-race outcome columns are never used as predictors.

## Confounding check

The strategy features are highly confounded with car pace, driver quality, weather, and circuit characteristics. That means the model should not be interpreted causally: a good strategy score does not prove the strategy caused the result.

This limitation holds for both targets. It is especially important for `is_top5`, because podium-adjacent outcomes are more sensitive to race-control events and small pacing differences.

## Mitigation attempts

- Use locked temporal split: train 2019–2021, calibration 2022, test 2023–2024.
- Include constructor tier, circuit type, and weather as explanatory context.
- Treat strategy inputs as counterfactual scenario controls only in the what-if comparison.
- Report calibration and slice-based error analysis so the confounding problem is visible rather than hidden.
