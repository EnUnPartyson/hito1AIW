# F1 Race Strategy Advisor: Two-stop preserves P(top10) but reduces P(top5) on wet street circuits

Team:    Ariel Van Kilsdonk & David Hernandez  
Course:  IIT414W — Artificial Intelligence Workshop · 2026-1T  
Date:    May 17, 2026  
Repo:    https://github.com/davidhu12345/hito1AIW  
Commit:  06c7b96

---

## 1. Executive Summary

We built a scenario-comparison tool that helps an F1 race engineer decide between a 1-stop and 2-stop strategy before the race and at the first pit window. The model outputs calibrated probabilities for two targets: finishing in the top 10 (points survival) and finishing in the top 5 (top-end conversion). The key finding is that in wet street-circuit contexts, the strategy that maximizes P(top10) is not always the same as the strategy that maximizes P(top5). This matters because a team that only optimizes top-10 survival may give up top-5 upside.

Our main calibrated logistic models improve over the heuristic baseline and are competitive on both targets, but they do not beat the docent floor on `is_top10`. We therefore treat this report as a midpoint deliverable, not a deployable system. We recommend using the tool only for structured scenario comparison, not as a definitive strategy oracle, and only after the conditions in Section 7 are satisfied.

---

## 2. Problem Framing

**Decision context.** The race engineer must choose a 1-stop vs 2-stop strategy for a given Grand Prix before lights out, with a second confirmation window around laps 20–30 when the first pit window opens. The tool returns $P(\mathrm{top\ 10})$ and $P(\mathrm{top\ 5})$ for each candidate strategy to compare scenarios under uncertainty.

**Prediction unit.** One row equals one driver × one race. Inputs are pre-race signals plus user-controlled scenario inputs (strategy variables), and outputs are calibrated probabilities on two targets.

**Targets.**
- Primary: `is_top10` (cohort-comparable points survival)
- Expansion: `is_top5` (top-end points haul; more sensitive to strategy trade-offs)

**Scenario variables.** `n_stops` and `compound_sequence` are scenario inputs controlled by the engineer. They are post-race in the raw dataset but treated as counterfactual inputs for what-if comparison.

**Assumptions (with consequences).**
1. `qualifying_position` is a valid proxy for grid position; using qualifying time gaps is not allowed because the column is empty. Consequence: the model captures ordinal grid effects but not fine-grained pace gaps.
2. Strategy inputs are treated as user-controlled counterfactuals, not as predictors of the observed future. Consequence: strategy recommendations are conditional on the assumed pace profile, not causal proof.
3. The 2019–2024 window is structurally representative of the current regulation era. Consequence: model performance can degrade under major regulation shifts or grid-order changes.

**Metrics.** Brier score is the primary metric because the output is a probability used in decision-making, and Brier penalizes overconfident errors. ROC-AUC is reported as a secondary comparator against the docent baseline.

---

## 3. Data and Validation

**Dataset.** Official race-level dataset `f1_strategy_race_level.csv` (2019–2024).

**Temporal split (locked).** Train 2019–2021, calibration 2022, test 2023–2024. Calibration uses 2022 only and does not alter model selection.

**Leakage audit summary.**
- Pre-race predictors: `qualifying_position`, `constructor_tier`, `circuit_type`.
- Scenario inputs (post-race in raw data but user-controlled in what-if): `n_stops`, `compound_sequence`.
- Audit-only slices: `safety_car_race`, `weather_actual`, pace aggregates.
- Outcomes (`finish_position`, `points`) are never used as predictors.

**Scenario protocol.** What-if comparisons hold driver, circuit, and pre-race context fixed while varying strategy inputs to compare probabilities, not to claim causal effects.

---

## 4. Modeling Approach

**Baselines.**
- Heuristic grid-position + constructor-tier rule (Hito 1 baseline).
- Docent baseline floor used for honest comparison on `is_top10`.

**Main model family (both targets).** Calibrated logistic regression with one-hot encoded categorical features. The model is interpretable and stable under the locked split.

**Calibration.** Platt-style calibration on the 2022 block only. Test set probabilities are generated after calibration is fixed.

**Feature sets.**
- Pre-race signals: `qualifying_position`, `constructor_tier`, `circuit_type`.
- Scenario inputs: `n_stops`, `compound_sequence`.
- Audit-only columns: `weather_actual`, safety car indicators, post-race pace.

**Hyperparameter rationale.** Logistic regression was chosen for interpretability and calibration stability on a small, structured dataset. A calibrated random forest is used only as a stress-test to surface a target disagreement in the what-if grid.

---

## 5. Results and Honest Comparison

**Headline metrics (test 2023–2024).**

| Target | Main calibrated model | Metric | Value | Baseline / reference |
|---|---|---:|---:|---:|
| `is_top10` | Calibrated logistic regression | Brier | 0.1447 | Docent floor: 0.1320 |
| `is_top5` | Calibrated logistic regression | Brier | 0.0958 | Heuristic baseline: 0.1227 |

**Plain-English result per target.**
- `is_top10`: The model is competitive but does not beat the docent floor; it improves on the heuristic baseline but is not yet a deployable predictor of points survival.
- `is_top5`: The model meaningfully improves on the heuristic baseline, indicating additional signal for top-end outcomes.

**Calibration evidence.**

**Figure 1. Reliability diagram — `is_top10` (test set 2023–2024).** Generated by `hito2_modeling.ipynb`; output saved as `calibration_curve_top10.png`. The curve shows visible deviation from the diagonal in the 0.3–0.7 probability range: the model is overconfident at mid-range probabilities, consistent with the midfield Brier results in Section 6. Overall calibration is acceptable but not tight.

**Figure 2. Reliability diagram — `is_top5` (test set 2023–2024).** Generated by `hito2_modeling.ipynb`; output saved as `calibration_curve_top5.png`. The `is_top5` curve tracks the diagonal more closely than `is_top10`, consistent with its lower Brier score (0.0958), but shows overconfidence near 0.7–0.9 — the front-running slice identified in Section 6.

---

## 6. Error Analysis and What-If

**Slice analysis (Brier).**
- Strategy type: `two_stop` is the best-performing common slice; `one_stop` and `three_plus_stop` are harder.
- Circuit type: `is_top10` is hardest on semi-street circuits; `is_top5` is worst on street circuits.
- Constructor tier: `is_top10` is hardest on midfield; `is_top5` is hardest on front-running teams.
- Weather: `is_top5` degrades in wet races.

**Three failure-mode hypotheses (where / why / how-to-test).**
1. Wet street and semi-street races: probability drift due to race-control noise + pit-window timing; test by isolating wet street races in a later season block.
2. Midfield constructors for `is_top10`: boundary cases are sensitive to small pace shifts; test by adding pace proxy features and checking calibration change.
3. Front-running `is_top5`: overconfidence near podium boundary; test by reliability curves for top constructors only.

**What-if disagreement scenario.**
- Scenario: `qp=1`, `constructor_tier=top`, `circuit_type=street`. Rows conditioned on `weather_actual=wet` in the test set (2023–2024) to identify the wet-street-circuit regime; `weather_actual` is not a model feature and is not varied as a scenario input.
- Strategies compared: `one_stop` (M-H), `two_stop` (S-M-H), `three_plus_stop` (S-M-S-H), `no_stop` (S).
- Disagreement: `is_top10` prefers `two_stop` (0.7251 vs 0.7196); `is_top5` prefers `one_stop` (0.6014 vs 0.5956).
- Interpretation: in this wet street-circuit context, a two-stop strategy is associated with slightly higher P(top10), while a one-stop strategy is associated with slightly higher P(top5). These are observational comparisons, not causal claims.
- **Value-add vs existing heuristics:** the heuristic grid-position baseline assigns a single fixed P(top10) regardless of stop count and cannot expose this trade-off. Our tool is the only artifact in this workflow that surfaces a scenario where the points-survival-optimal strategy and the top-end-optimal strategy diverge.

---

## 7. Limitations and Risks

**Strategy confounding (explicit).** Strategy features are observationally confounded with car pace, driver skill, and race events; scenario outputs are conditional comparisons, not causal claims.

**Other limitations (with consequences).**
1. The dataset starts in 2019; major regulation shifts can invalidate learned relationships.
2. `qualifying_time_s` is empty, so pace gaps are not captured; the model treats grid position as ordinal only.
3. Safety car indicators are binary, not counts or timing; this hides critical timing effects on strategy.

**Mandatory honesty sentence.**
We do not recommend deploying this tool unless (1) it is re-evaluated on at least one future season beyond 2024, (2) scenario sensitivity is validated on multiple real disagreement cases, and (3) calibration for wet and midfield slices remains within a pre-specified Brier tolerance.

---

## 8. Reproducibility Note and AI Reflection

**Reproducibility.** See README for the runbook and environment setup. All outputs are reproducible from a fresh clone with the locked split, and the repo is tagged `final-v1` at the commit listed on the title page.

**AI reflection (1 paragraph).** AI helped restructure the report into the nine required sections and tighten the executive summary language. It also suggested phrasing for the what-if disagreement narrative. We overrode one incorrect suggestion that implied the `is_top10` model beat the docent floor and rewrote that passage to reflect the actual results. See PROMPTS.md for the full interaction log and the rejected suggestion.

---

## 9. References

1. IIT414W Capstone Dataset (2026). *f1_strategy_race_level.csv*. Module 5 — Unit IV, Artificial Intelligence Workshop (IIT414W), 2026-1T.
2. Viertel, T. (2024). *FastF1: A Python package for accessing Formula 1 timing and telemetry data* (v3.x). GitHub. https://github.com/theOehrly/Fast-F1
3. Jolpica (2024). *Jolpica-F1 API documentation*. GitHub. https://github.com/jolpica/jolpica-f1
4. IIT414W Module 5 rubric and lecture materials (2026). *Capstone: F1 Race Strategy Advisor — Final Report guidelines*. Artificial Intelligence Workshop, 2026-1T.
5. Scikit-learn developers (2024). *sklearn.calibration.CalibratedClassifierCV*. scikit-learn 1.4 documentation. https://scikit-learn.org/stable/modules/calibration.html
6. Brier, G. W. (1950). Verification of forecasts expressed in terms of probability. *Monthly Weather Review, 78*(1), 1–3.

---

## Optional Appendix (not counted)

- Extended slice tables
- Additional figures
- Per-team contribution statement
