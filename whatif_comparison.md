# What-If Comparison — Hito 2

## Scenario used

The logistic regression model was monotonic on the sampled scenario grid, so a calibrated random forest stress test was used to surface the required cross-target disagreement.

Scenario: `qp = 1`, `constructor_tier = top`, `circuit_type = street`, `weather_actual = wet`

Strategies compared:

- `one_stop` with `compound_sequence = M-H`
- `two_stop` with `compound_sequence = S-M-H`
- `three_plus_stop` with `compound_sequence = S-M-S-H`
- `no_stop` with `compound_sequence = S`

## Disagreement found

| Target | Preferred strategy | Supporting probabilities |
|---|---|---|
| `is_top10` | `two_stop` | `two_stop = 0.7251`, `one_stop = 0.7196` |
| `is_top5` | `one_stop` | `one_stop = 0.6014`, `two_stop = 0.5956` |

The disagreement is small in absolute terms, but it is exactly the kind of trade-off Hito 2 is looking for: the model says the more aggressive strategy has a slightly better chance of keeping the car in the top 10, while the more conservative strategy has a slightly better chance of converting that run into a top-5 finish.

## Interpretation

If the engineering goal is simply to survive inside the points, the `two_stop` is marginally preferred. If the goal is to maximize the chance of a strong points haul or podium-adjacent finish, `one_stop` is preferred.

That is the key value of the expansion target: `is_top10` alone would miss the strategy trade-off because it only tells us whether the car survives inside the points, not whether it converts that survival into a stronger finish.
