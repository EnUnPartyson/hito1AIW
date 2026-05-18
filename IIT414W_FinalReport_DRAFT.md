# F1 Race Strategy Advisor: Two-stop preserves P(top10) but reduces P(top5) on wet street circuits

Team:    Ariel Van Kilsdonk & David Hernandez  
Course:  IIT414W — Artificial Intelligence Workshop · 2026-1T  
Date:    May 17, 2026  
Repo:    https://github.com/davidhu12345/hito1AIW  
Commit:  b7251ad

---

## 1. Executive Summary

We built a scenario-comparison tool that helps an F1 race engineer decide between a 1-stop and 2-stop strategy before the race and at the first pit window. The model outputs calibrated probabilities for two targets: finishing in the top 10 (points survival) and finishing in the top 5 (top-end conversion). The key finding is that in wet street-circuit contexts, the strategy that maximizes P(top10) is not always the same as the strategy that maximizes P(top5). This matters because a team that only optimizes top-10 survival may give up top-5 upside.

Our main calibrated logistic models improve over the heuristic baseline and are competitive on both targets, but they do not beat the docent floor on `is_top10`. We therefore treat this report as a midpoint deliverable, not a deployable system. We recommend using the tool only for structured scenario comparison, not as a definitive strategy oracle, and only after the conditions in Section 7 are satisfied.

---

## 2. Problem Framing

**Decision context.** The target user is a race engineer at the pit wall, working in coordination with the strategy team. The decision being supported is: choose between a 1-stop and 2-stop tyre strategy for a given Grand Prix before lights out. This decision has two windows — the primary window is the pre-race strategy briefing, typically 60–90 minutes before the formation lap, when the team commits to a baseline plan. A second confirmation window opens around laps 20–30, when the first pit stop window becomes live and the engineer can revise the strategy based on track position and tyre condition. The tool is designed to support both windows by returning $P(\mathrm{top\ 10})$ and $P(\mathrm{top\ 5})$ for each candidate strategy, enabling the engineer to compare scenarios quantitatively before committing to an in-lap call.

**Prediction unit.** One row equals one driver × one race. Inputs are pre-race signals (grid position, constructor tier, circuit type) plus user-controlled scenario inputs (stop count and compound sequence). Outputs are calibrated probabilities on two binary targets. The model is not a real-time telemetry tool — it operates on pre-race information and user-specified strategy hypotheticals.

**Targets.**
- Primary: `is_top10` — binary, 1 if the driver finishes in positions 1–10. This is the cohort-comparable target locked by the course design and maps directly to the strategy decision because finishing in the top 10 awards constructor points, which is the currency race engineers optimise for under uncertainty.
- Expansion: `is_top5` — binary, 1 if the driver finishes in positions 1–5. This target is more sensitive to strategy trade-offs than `is_top10` because it separates strong points hauls from mere survival and exposes decision boundaries that top-10 alone hides.

**Scenario variables.** `n_stops` and `compound_sequence` are scenario inputs controlled by the engineer. They are post-race observations in the raw dataset but are treated as user-controlled counterfactual inputs for what-if comparison — analogous to how a flight simulator receives pilot inputs that define the scenario rather than sniff the outcome.

**Assumptions (with consequences).**
1. `qualifying_position` is a valid proxy for grid position. Using `qualifying_time_s` (the pace gap to pole) is not allowed because that column is empty throughout the dataset. Consequence: the model captures ordinal grid effects but cannot represent fine-grained pace gaps between qualifiers starting at adjacent grid positions.
2. Strategy inputs (`n_stops`, `compound_sequence`) are treated as user-controlled counterfactuals, not as predictors of the observed future. Consequence: scenario outputs are conditional on the assumed strategy, not causal proof that the strategy caused the result. A recommendation to use two stops does not mean two stops will achieve the predicted probability — it means that in the historical distribution of races with similar pre-race context, two-stop drivers achieved top-10 finishes at that rate.
3. The 2019–2024 window is structurally representative of the current regulation era. Consequence: model performance can degrade under major regulation shifts or significant changes to the competitive grid order. The 2022 regulation change is partially addressed by using 2022 as the calibration block rather than as training data, but the model was not validated against a post-2024 season.

**Metrics.** Brier score is the primary evaluation metric because the model output is a probability used directly in decision-making. Brier score penalises overconfident wrong predictions and underconfident correct ones — exactly the failure modes that matter to a race engineer who is betting a strategy on a probability estimate. Lower is better; a perfect forecaster scores 0 and the worst naive forecaster scores 1. ROC-AUC is reported as a secondary comparator to enable fair comparison against the docent baseline, but it is not used for model selection because it is threshold-invariant and does not measure calibration quality.

---

## 3. Data and Validation

**Dataset summary.** The official course dataset `f1_strategy_race_level.csv` contains 2,447 driver-race entries across six Formula 1 seasons (2019–2024), with 47 raw columns covering pre-race context, race strategy, weather, safety car, and finishing outcomes. Each row is one driver's participation in one race weekend. The dataset covers between 17 and 24 race weekends per season depending on the calendar, with 20 drivers per grid.

| Split | Seasons | Entries | Purpose |
|---|---|---:|---|
| Train | 2019–2021 | 1,132 | Model fitting |
| Calibration | 2022 | 426 | Platt-scaling only |
| Test | 2023–2024 | 889 | Final evaluation (used once) |

**Temporal split rationale.** The split is locked at season boundaries to prevent future race information from leaking into training. The 2022 season was selected as the calibration block rather than as additional training data for two reasons: (1) the 2022 regulation change introduced a substantially different aerodynamic package that shifted the competitive grid order, making 2022 a natural structural break; and (2) using 2022 only for calibration means the probability calibration reflects the post-regulation-change distribution without contaminating the pre-change training signal.

**Leakage audit summary.** All columns were classified into one of three categories before any model was fit. Pre-race predictors are features whose values are known before the race starts: `qualifying_position`, `constructor_tier`, and `circuit_type`. These are the only columns used as model inputs. Scenario inputs are features that are post-race observations in the raw dataset but are declared as user-controlled counterfactual controls: `n_stops` and `compound_sequence`. Their use as model inputs is justified because the product is a what-if comparison tool, not a pre-race oracle — the engineer explicitly sets these values to ask "what is P(top10) if we execute this strategy?" Audit-only slices are post-race observations used only for error analysis, never as model inputs: `safety_car_race`, `weather_actual`, pace aggregates, and stint timing. Outcomes (`finish_position`, `points`, `is_top3`, `is_top5`, `is_top10`, `dnf`) are never used as predictors.

The column `qualifying_time_s` is confirmed empty in the dataset and was excluded from all feature lists. The columns `driver_prior3_avg_finish` and `constructor_prior3_avg_finish` are pre-race signals that could be added in future iterations, but were excluded from this submission to keep the feature set minimal and interpretable.

**Scenario protocol.** What-if comparisons hold driver, circuit, and all pre-race context fixed while varying only the scenario inputs (`n_stops`, `compound_sequence`) across the candidate strategies. The outputs are compared as conditional probabilities under different strategy hypotheticals, not as predictions of what will happen. All scenario outputs are framed as observational comparisons, not as causal claims.

---

## 4. Modeling Approach

**Baselines.** Two baselines are used for honest comparison. The heuristic baseline is a grid-position and constructor-tier rule built on Hito 1 training data (2019–2021 only) without any access to test data. It assigns probabilities as follows: drivers starting in grid positions 1–5 receive P(top10) = 0.85; positions 6–10 receive P(top10) = 0.55; positions 11 and above receive P(top10) = 0.20. A constructor-tier modifier of ±0.05 is applied for top-tier and bottom-tier constructors respectively, clipped to [0.05, 0.95]. This baseline is directionally correct — it exploits the well-documented grid-position–points correlation — but it is entirely scenario-insensitive: it assigns the same probability regardless of stop count. The docent baseline floor for `is_top10` is Brier 0.1320, ROC-AUC 0.892 on the 2023–2024 test set, and is used as the primary honest comparison point for the primary target.

**Main model family — both targets.** Calibrated logistic regression with one-hot encoded categorical features is the primary model for both `is_top10` and `is_top5`. Logistic regression was chosen for three reasons specific to this problem: (1) interpretability — the coefficients directly show how grid position and each strategy type shift the log-odds, which makes the model auditable by an F1 engineer; (2) calibration stability — logistic regression outputs are closer to well-calibrated probabilities than tree-based models on small structured datasets, reducing the correction needed at calibration time; and (3) the dataset has 1,132 training rows with a small feature set, making a low-variance linear model more appropriate than a high-capacity learner.

**Feature encoding.** The features fed to the logistic model are: `qualifying_position` treated as a continuous ordinal feature (values 1–20); `constructor_tier` one-hot encoded into three levels (front, midfield, backmarker); `circuit_type` one-hot encoded into three levels (permanent, semi-street, street); `n_stops` one-hot encoded into four levels (no_stop, one_stop, two_stop, three_plus_stop); and `compound_sequence` one-hot encoded across the observed unique sequences in the training set. The same encoding is applied identically to both `is_top10` and `is_top5` models.

**Hyperparameter rationale.** Logistic regression is fit with default regularisation (L2, C = 1.0) and `max_iter = 1000` to ensure convergence on one-hot expanded feature sets. No hyperparameter search was performed because the primary goal was a stable, interpretable probability model rather than maximum discrimination. Regularisation with C = 1.0 applies mild shrinkage that is appropriate for a sparse one-hot feature matrix of this size. The `random_state` is set to `RANDOM_SEED = 414` for all stochastic operations.

**Calibration approach.** Platt-style calibration is applied using `CalibratedClassifierCV` with `cv='prefit'` on the 2022 block only. The logistic model is first fit on 2019–2021 training data, then passed to the calibration wrapper which fits a sigmoid function on the 2022 block probabilities. The test set (2023–2024) is never touched until final evaluation. This procedure is applied identically to both targets. Calibrated probabilities, not raw logistic outputs, are used for all reported metrics and all what-if comparisons.

**RF stress test (what-if disagreement only).** A calibrated random forest (`n_estimators = 100`, `max_depth = 5`, `random_state = 414`) was used as a scenario stress test to search a wider strategy grid than the logistic model, which stayed monotonic on the sampled scenario grid and did not expose a cross-target disagreement. The RF is not a primary model and its metrics are not reported in the headline table — it is used only to demonstrate that a target disagreement exists in the joint strategy space, reported in Section 6.

---

## 5. Results and Honest Comparison

**Headline metrics (test 2023–2024).**

| Target | Model | Brier | ROC-AUC | Baseline Brier | Docent floor Brier |
|---|---|---:|---:|---:|---:|
| `is_top10` | Calibrated logistic regression | 0.1447 | 0.8726 | 0.1669 | 0.1320 |
| `is_top5` | Calibrated logistic regression | 0.0958 | 0.9217 | 0.1227 | — |

**Plain-English result per target.**
- `is_top10`: The model improves over the heuristic baseline (Brier 0.1447 vs 0.1669) but does not beat the docent floor (0.1320). It is competitive but not yet a deployable predictor of points survival. The ROC-AUC of 0.8726 indicates strong discrimination, but the Brier gap to the docent floor shows the model's probability estimates are less accurate than the course reference.
- `is_top5`: The model meaningfully outperforms the heuristic baseline (Brier 0.0958 vs 0.1227, a reduction of 0.0269). ROC-AUC of 0.9217 indicates strong discrimination on the top-5 boundary. No docent floor was published for this expansion target.

**Calibration evidence.**

**Figure 1. Reliability diagram — `is_top10` (test set 2023–2024).** Generated by `hito2_modeling.ipynb`; output saved as `calibration_curve_top10.png`. The curve shows visible deviation from the diagonal in the 0.3–0.7 probability range: the model is overconfident at mid-range probabilities, consistent with the midfield Brier results in Section 6. Overall calibration is acceptable but not tight.

**Figure 2. Reliability diagram — `is_top5` (test set 2023–2024).** Generated by `hito2_modeling.ipynb`; output saved as `calibration_curve_top5.png`. The `is_top5` curve tracks the diagonal more closely than `is_top10`, consistent with its lower Brier score (0.0958), but shows overconfidence near 0.7–0.9 — the front-running slice identified in Section 6.

---

## 6. Error Analysis and What-If

**Slice analysis — strategy type.**

| Strategy | `is_top10` Brier | `is_top5` Brier |
|---|---:|---:|
| `no_stop` | 0.0442 | 0.0281 |
| `one_stop` | 0.1559 | 0.1045 |
| `two_stop` | 0.1350 | 0.0899 |
| `three_plus_stop` | 0.1521 | 0.0967 |

The `no_stop` slice has very low Brier scores on both targets but is a rare and unrepresentative case (typically drivers in dominant positions or races neutralised by red flags). Among the common strategy classes, `two_stop` is the best-performing slice on both targets. `one_stop` and `three_plus_stop` are consistently harder — `one_stop` because it is used in diverse contexts ranging from dominant car management to backmarker gambles, and `three_plus_stop` because these races typically involve unexpected weather or safety car events that introduce high variance the model cannot predict pre-race.

**Slice analysis — circuit type.**

| Circuit type | `is_top10` Brier | `is_top5` Brier |
|---|---:|---:|
| `permanent` | 0.1391 | 0.0933 |
| `semi-street` | 0.1774 | 0.0848 |
| `street` | 0.1417 | 0.1104 |

`is_top10` is hardest on semi-street circuits, which is consistent with the idea that mixed-track character and race interruptions make the top-10 boundary noisier. `is_top5` is worst on street circuits, suggesting the podium and top-5 boundary is more fragile in street-circuit contexts — likely because track position is harder to recover once lost on narrow street layouts, making strategy comparisons less reliable.

**Slice analysis — constructor tier.**

| Constructor tier | `is_top10` Brier | `is_top5` Brier |
|---|---:|---:|
| `backmarker` | 0.1295 | 0.0078 |
| `front` | 0.1121 | 0.1972 |
| `midfield` | 0.1700 | 0.1210 |

`is_top10` is hardest on midfield teams — this is the most operationally significant failure mode because midfield is exactly where small strategy changes can swing the result across the points boundary. The `is_top5` Brier is worst for front-running constructors because the model is making sharper top-end decisions there, and the podium boundary is far more sensitive to overconfidence errors.

**Slice analysis — weather.**

| Weather | `is_top10` Brier | `is_top5` Brier |
|---|---:|---:|
| `dry` | 0.1451 | 0.0923 |
| `wet` | 0.1425 | 0.1183 |

The `is_top5` model degrades substantially in wet conditions (0.1183 vs 0.0923 in dry races), which is exactly where strategy confounding is strongest and where stop-count decisions tend to matter most operationally.

**Three failure-mode hypotheses.**
1. *Wet street and semi-street circuits* — where: wet street and semi-street race slices; why: the model combines race-control noise with pit-window timing, and both factors interact in wet conditions on narrow circuits in ways that are not captured by pre-race inputs; how to test: isolate wet street circuit races from the 2025+ season block and compute Brier, comparing against the dry street circuit Brier from the test set.
2. *Midfield constructors for `is_top10`* — where: the midfield constructor tier slice (Brier 0.1700, the worst single slice); why: the model sits near the decision boundary for midfield teams, and small unobserved pace shifts can move the probability mass above or below the top-10 cutoff; how to test: add a pace proxy feature (e.g. `constructor_prior3_avg_finish`) and check whether the midfield Brier decreases meaningfully.
3. *Front-running teams for `is_top5`* — where: the front constructor tier slice (Brier 0.1972 on `is_top5`, the worst single slice across all analyses); why: the model is asked to separate already-strong finishes from podium-contending finishes, and calibration errors are most visible when the model must place high-confidence estimates near the 0.7–0.9 range; how to test: compute reliability curves for top constructors only and compare the deviation from the diagonal against the full-sample reliability curve.

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
1. The dataset starts in 2019; major regulation shifts can invalidate learned relationships. The 2022 aerodynamic regulation change is partially mitigated by using that season as a calibration block, but a future regulation change of similar scale would require retraining from scratch.
2. `qualifying_time_s` is empty throughout the dataset, so pace gaps between adjacent qualifiers are not captured. The model treats grid position as ordinal, which means a driver qualifying P3 by 0.001 s and one qualifying P3 by 0.5 s are treated identically.
3. Safety car indicators in the dataset are binary (occurred / did not occur), not counts or timing. This hides critical timing effects: a lap-1 safety car has completely different strategic implications from a lap-40 safety car, but both are encoded as the same flag.

**Mandatory honesty sentence.**
We do not recommend deploying this tool unless (1) it is re-evaluated on at least one future season beyond 2024 and achieves Brier ≤ 0.1320 on `is_top10`, (2) scenario sensitivity is validated on at least three real race disagreement cases where our model's preferred strategy differed from the observed team decision, and (3) calibration for wet and midfield slices remains within ±0.02 Brier of the overall test set score on the new evaluation season.

---

## 8. Reproducibility Note and AI Reflection

**Reproducibility.** See README for the runbook and environment setup. All outputs are reproducible from a fresh clone with the locked split (`RANDOM_SEED = 414` set in every `random_state` argument), and the repo is tagged `final-v1` at the commit listed on the title page. Calibration curves are generated and saved as `calibration_curve_top10.png` and `calibration_curve_top5.png` when `hito2_modeling.ipynb` is run with Kernel → Restart & Run All.

**AI reflection (1 paragraph).** AI helped restructure the report into the nine required sections and tighten the executive summary language. It also suggested phrasing for the what-if disagreement narrative. We overrode one incorrect suggestion that implied the `is_top10` model beat the docent floor and rewrote that passage to reflect the actual results. See PROMPTS.md for the full interaction log and the rejected suggestion documented in Interaction 7.

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
