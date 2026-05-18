# Hito 1 — Problem Framing Document
**Team:** Ariel Van Kilsdonk & David Hernandez  
**Capstone:** F1 Race Strategy Advisor — Module 5, Unit IV  
**Date:** May 6, 2026

---

## 1. Decision Context

**Decision:** Should a driver commit to a 1-stop or 2-stop strategy for a given Grand Prix?

**Decision-maker:** Race engineer (pit wall), consulting the strategy team.

**When in the race weekend:** The primary decision window is the **pre-race phase** (strategy briefing before the formation lap) and reinforced at **lap ~20–30** when the first pit stop window opens. The tool produces a probability score — P(top 10 finish) — for each candidate strategy, enabling the engineer to compare scenarios before committing to an in-lap call.

**Prediction unit:** One row = one driver × one race. The model receives pre-race information (grid position, constructor tier) and outputs P(is_top10). **Note:** The current baseline is scenario-insensitive and does not use scenario features. Scenario sensitivity will be implemented in Hito 2.

---

## 2. Target & Primary Metric

**Target:** `is_top10` — binary indicator, 1 if the driver finishes in positions 1–10, 0 otherwise.

This target was locked by the cohort design. It maps directly to the strategy decision: finishing in the top 10 awards constructor points, which is the currency that race engineers optimise for when choosing strategy under uncertainty.

**Primary metric:** **Brier Score** (lower = better).

Justification:
- The output is a probability, not a class label. Brier score penalises both overconfident wrong predictions and underconfident correct ones — exactly the failure modes that matter to a race engineer who must bet on a strategy.
- Log loss is reported as a secondary metric (required by the rubric) and provides complementary information on the tail of the distribution.
- ROC-AUC is reported for comparison against the docent baseline but is not the primary metric because it is threshold-invariant and does not measure calibration quality.

**Docent baseline floor:** Brier 0.132, ROC-AUC 0.892 on the 2023–2024 test set.

---

## 3. Baseline Plan with F1-Defendable Rationale

**Baseline choice:** Heuristic rule using `qualifying_position` (grid position proxy) and `constructor_tier`.

```
P(top10) = 0.85  if grid_position ≤ 5
P(top10) = 0.55  if 6 ≤ grid_position ≤ 10
P(top10) = 0.20  otherwise
```

*Constructor tier modifier (±0.05):* Top-tier constructors (Mercedes, Red Bull, Ferrari) receive +0.05; bottom-tier constructors (< 5th in prior-season WCC) receive −0.05. Probabilities are clipped to [0.05, 0.95].

**F1 rationale:**  
Starting position is the single strongest predictor of finishing position in Formula 1; since 2010, roughly 60% of top-10 finishes come from drivers who started in the top 10 (Motorsport Statistics). Constructor tier captures car pace independently of qualifying — a fast car recovers from mid-grid; a slow car rarely converts a front-row start into points without extreme luck.

This baseline is **directionally correct**: higher grid row → higher P(top10). It uses only pre-race information and does not depend on the test set. **It does not use scenario features and is not scenario-sensitive.**

**Why this beats "majority class":** The majority-class baseline (predict 0.5 for everyone in a 50/50-ish split, or 1.0 for the common class) carries no race logic. Our heuristic exploits the well-known grid-position–points correlation and will outperform naive classifiers without any data fitting.

---

## 4. What-If Comparison Plan — Two Specific Scenarios

The model is a **scenario comparison tool**. **However, the current baseline is scenario-insensitive and does not use strategy features (`n_stops`, `compound_sequence`, `stint_lengths`).** The engineer sets these in Hito 2 to ask "what if we called this strategy?" Scenario sensitivity will be implemented in Hito 2.

**Scenario A — Monaco 2024, Charles Leclerc (Ferrari)**

| Feature | 1-Stop | 2-Stop |
|---|---|---|
| `driver_id` | LEC | LEC |
| `circuit` | Monaco | Monaco |
| `qualifying_position` | 1 | 1 |
| `constructor_tier` | top | top |
| `n_stops` | 1 | 2 |
| `compound_sequence` | M→H | S→M→H |
| `stint_lengths` | [35, 43] | [20, 25, 33] |

*Hypothesis:* Monaco rewards track position. The model should assign higher P(top10) to the 1-stop strategy here.

**Scenario B — British Grand Prix 2023, Lance Stroll (Aston Martin)**

| Feature | 1-Stop | 2-Stop |
|---|---|---|
| `driver_id` | STR | STR |
| `circuit` | British Grand Prix | British Grand Prix |
| `qualifying_position` | 8 | 8 |
| `constructor_tier` | mid | mid |
| `n_stops` | 1 | 2 |
| `compound_sequence` | M→H | S→M→H |
| `stint_lengths` | [30, 22] | [14, 20, 18] |

*Hypothesis:* Silverstone's high tyre degradation rewards the 2-stop; the model should reflect this via compound usage patterns in the training data.

---

## 5. Known Dataset Limitations (at least 2 acknowledged)

**Limitation 1 — Coverage starts in 2019 (consequence: structural gaps)**  
The recovered lap-level artifact covers 2019–2024. Pre-2019 seasons — including the hybrid-era dominance years of 2014–2018 — are absent. Models trained on this window may overfit to the competitive structures of this specific era (Mercedes/Red Bull/Ferrari hierarchy) and underperform if regulations change the field order drastically, as they did in 2022.

**Limitation 2 — `qualifying_position` is a proxy for `grid_position`; `qualifying_time_s` is empty**  
The column `qualifying_position` is retained for consistency but it is a stand-in derived from the available artifacts. `qualifying_time_s` is blank and must not be used as a numeric signal. Building a model that relies on qualifying *time gaps* (e.g., gap to pole) would be a graded error. We treat `qualifying_position` as an ordinal feature only.

**Limitation 3 — `safety_car_periods` is a binary indicator, not a count**  
The feature flags whether any safety-car period occurred in the race, not how many or at which lap. This collapses critical differences: a lap-1 safety car has different strategic implications than a lap-40 safety car. We treat this variable as an audit slice (post-race observation), not a pre-race input.

**Limitation 4 — Strategy confounding**  
Strategy choice (n_stops, compound sequence) is not independent of car pace, driver skill, weather, and race incidents. A 1-stop that succeeded may have done so because the car had exceptional tyre management, not because the strategy was inherently superior. The model cannot fully disentangle these. Our framing.md and PROMPTS.md acknowledge this limitation and any recommendations include the caveat "conditional on a car with pace profile similar to [constructor_tier]."

---

## 6. Three Experiments Planned for Hito 2

**Experiment 1 — Logistic Regression with strategy scenario features**  
*Hypothesis:* Adding `n_stops` and `compound_sequence` (one-hot encoded) as scenario inputs will reduce Brier score below the heuristic baseline (< 0.208) without causing leakage, because they are explicitly declared as user-controlled inputs.  
*Metric:* Brier score on test set (2023–2024).

**Experiment 2 — Gradient Boosted Trees (LightGBM) with full feature set**  
*Hypothesis:* A tree-based model can capture non-linear interactions between `qualifying_position`, `constructor_tier`, `n_stops`, and `circuit` that the logistic model cannot. We expect Brier < 0.15, approaching or beating the docent baseline (0.132).  
*Metric:* Brier score + ROC-AUC on test set; calibration curve visual.

**Experiment 3 — Calibrated model (Platt scaling on 2022 calibration set)**  
*Hypothesis:* The raw probability outputs of LightGBM are overconfident for mid-field drivers. Applying Platt scaling on the 2022 calibration block will improve Brier score by ≥ 0.01 versus the uncalibrated model.  
*Metric:* Brier score before vs. after calibration; reliability diagram.

---

## 7. Leakage Rules — Strategy Features as Scenario Inputs

The features `n_stops`, `compound_sequence`, and `stint_lengths` are **post-race observations** in the raw dataset. In any standard predictive modelling task, using them as predictors would constitute target leakage — they are known only after the race concludes.

**This capstone permits them for a specific and declared reason:** the product is a *scenario comparison tool*, not a pre-race oracle. The race engineer explicitly sets these variables to ask "what is P(top10) *if* we execute this strategy?" The model receives them as user-controlled inputs, exactly as a flight simulator receives pilot inputs — they define the counterfactual, they are not sniffed from the future.

This distinction is declared here and must be replicated in the notebook's leakage audit cell. Any feature that is a true post-race outcome (e.g., `safety_car_periods`, `current_rainfall`) is **not** used as a scenario input; if it appears in the data, it is treated as an audit slice or stress-test dimension only.

---

## 8. Team Workflow

| Period | Ariel Van Kilsdonk | David Hernandez |
|---|---|---|
| Mon evening | Draft framing.md §1–4 | Explore CSV, identify feature types |
| Tue morning | Implement temporal split + baseline notebook | Draft PROMPTS.md interactions |
| Tue afternoon | Run leakage audit cell, compute metrics | Write README.md, test clean-clone run |
| Wed (class) | Final review + calibration curve | Submit to Canvas, push to GitHub |
