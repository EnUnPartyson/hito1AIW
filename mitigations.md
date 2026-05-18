# Mitigations — Hito 2

## Main risks

1. The model can still overfit to constructor strength, especially on `is_top10`, where midfield performance is the hardest slice.
2. Strategy confounding remains the biggest conceptual risk: the model may learn that a pit strategy is associated with a finish rather than actually being the cause of it.
3. `is_top5` is more sensitive to overconfidence at the front of the field, so small probability errors matter more.
4. Wet-race behavior is still under-modeled relative to dry races, especially for scenario comparisons.

## Mitigations tied to observed failures

- Keep the locked temporal split so the model does not leak future race structure into training.
- Calibrate on 2022 only, then evaluate once on 2023–2024.
- Use slice-level reporting to expose the worst cases: midfield for `is_top10`, wet races for `is_top5`, and semi-street or street circuits where pit timing matters more.
- Keep strategy inputs explicitly labeled as counterfactual controls so the team does not present the model as causal.
- For deployment, replace the current baseline with a model that includes more race-state context and, if possible, interaction terms or a richer tree-based learner.

## Before deployment

The model should not be deployed as a live recommendation engine until it is re-evaluated on a later season and its scenario sensitivity is tested against more than one disagreement case. The current submission is a midpoint model, not a final product.
