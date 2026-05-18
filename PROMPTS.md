# PROMPTS.md — Hito 2 Model Expansion

**Team:** Ariel Van Kilsdonk & David Hernandez  
**Capstone:** F1 Race Strategy Advisor — Hito 2

---

## Interaction 1 — Problem Framing & Feature Classification

### Context
We were deciding which features from the official race-level file (`f1_strategy_race_level.csv`) to use as predictors vs. scenario inputs vs. audit columns. We were unsure whether `n_stops` and `compound_sequence` would constitute leakage.

### Prompt
> We have a lap-level F1 dataset with columns including `n_stops`, `compound_sequence`, `qualifying_position`, `safety_car_race`, and `finishing_position`. We want to predict `is_top10`. Which features are safe to use as predictors, which should be scenario inputs, and which are leakage risks? The product is a what-if strategy comparison tool used before and during a race.

### Output
The AI correctly identified `qualifying_position` and `constructor_tier` as safe pre-race predictors. It flagged `n_stops` and `compound_sequence` as post-race observations that would be leakage in a standard setting, but acknowledged that in a scenario comparison tool they can be treated as user-controlled inputs as long as this is explicitly declared in the framing document. It also flagged `safety_car_race` as an audit column, not a predictor.

### Validation
We cross-referenced the AI's classification with the capstone rubric's Leakage Rules section and the five known dataset limitations. The classification matched the rubric's guidance. We confirmed that `qualifying_time_s` is empty (as noted in limitation 2) and removed it from any potential feature list.

### Adaptations
The AI initially suggested using `avg_lap_time` as a predictor. We rejected this because average lap time is a post-race observation that is directly correlated with pace and finishing position — using it would be a leakage error regardless of framing.

### Final Decision
We implemented the three-category leakage audit (pre-race signal / scenario input / audit column) as a standalone notebook cell. `n_stops` and `compound_sequence` are declared scenario inputs with explicit justification in framing.md Section 7. The Hito 1 baseline remained scenario-insensitive.

---

## Interaction 2 — Baseline Design & F1 Rationale

### Context
We needed to choose a baseline that is F1-defensible without relying on test data. We considered majority-class, random, and heuristic options. The baseline was built on the official race-level file and remained scenario-insensitive.

### Prompt
> For an F1 top-10 finish prediction model, design a heuristic baseline that uses only pre-race information (grid position and constructor tier) and is justified by F1 domain logic. The baseline should produce calibrated-ish probabilities, not just class labels. Avoid using any post-race information.

### Output
The AI proposed a grid-position threshold rule with three brackets (≤5, 6–10, >10) and suggested probabilities of 0.80 / 0.55 / 0.25 respectively, with a constructor tier modifier of ±0.05. It justified the brackets using historical F1 data patterns: top-5 starters win points at a high rate; mid-grid starters are coin-flip; back-markers rarely score without attrition.

### Validation
We verified the direction is correct: the rule assigns higher P(top10) to front-runners, which matches F1 reality. We adjusted the top bracket from 0.80 to 0.85 based on our inspection of the training data (2019–2021) — front-row starters in that era finished in the top 10 at approximately 85% rate given the dominance of a small set of constructors. This adjustment was made on train data only.

### Adaptations — AI Failure Documented
The AI initially suggested adding an `avg_lap_pace_rank` feature (derived from practice session lap times) as a second heuristic input. This was **rejected** for two reasons:
1. Practice lap time data is not present in the dataset.
2. Even if it were, using practice data that includes wet-session information would conflate conditions between sessions.

This is the AI failure/rejected suggestion required by the rubric.

### Final Decision
We implemented the three-bracket heuristic with constructor tier modifier as documented in `framing.md` Section 3 and in the notebook Section 5. The top bracket probability was set to 0.85 (adjusted on train set only). The baseline was evaluated on the test set exactly once in notebook Section 6.

---

## Interaction 3 — Expansion Target Selection

### Context
Hito 2 required a second target that could expose strategy trade-offs not visible in `is_top10`.

### Prompt
> Which expansion target best fits an F1 strategy advisor that already predicts is_top10, and why?

### Output
The AI recommended `is_top5` because it separates top-end performance from mere points survival. It also noted that `finish_position` and `points` are valid alternatives, but binary top-5 is easier to compare with the existing cohort baseline structure.

### Validation
We checked the rubric and agreed that the critical requirement is a second target that reveals a different decision boundary. `is_top5` does that while remaining compatible with the same locked split.

### Adaptations
We rejected `finish_position` as the expansion target for this submission because it would change the metric structure and make the comparison less direct for a midpoint deliverable.

### Final Decision
We used `is_top5` as the Hito 2 expansion target.

---

## Interaction 4 — Calibration and Probability Quality

### Context
Hito 2 requires calibrated binary probabilities and probability-quality analysis.

### Prompt
> How should we calibrate the binary targets using the locked 2022 block without leaking into the test set?

### Output
The AI recommended Platt-style calibration on the 2022 block, keeping 2023–2024 untouched until final evaluation.

### Validation
We implemented calibration on the 2022 block and verified that the test-set probabilities were only generated after calibration was fixed.

### Adaptations
The first draft used the raw logistic outputs only. That was corrected so the final notebook reports calibrated probabilities.

### Final Decision
We used calibrated logistic regression for the main binary results in the notebook.

---

## Interaction 5 — Error Analysis Slicing

### Context
The rubric requires error slices by strategy type, circuit type, and a third context.

### Prompt
> What third context gives the most meaningful F1 strategy error analysis after strategy type and circuit type?

### Output
The AI recommended constructor tier and weather as the most interpretable choices because both interact with pit strategy and race outcomes.

### Validation
We sliced by constructor tier and weather in the notebook and found both were informative, especially for `is_top5` in wet races and `is_top10` in midfield contexts.

### Adaptations
We did not rely on a single context slice; we used both constructor tier and weather to keep the analysis grounded.

### Final Decision
Constructor tier and weather were added as the third and fourth contexts in the Hito 2 error analysis.

---

## Interaction 6 — Confounding and What-If Disagreement

### Context
We needed a concrete disagreement case where the two targets recommend different strategies.

### Prompt
> How can we show a strategy disagreement between is_top10 and is_top5 if the main logistic model stays monotonic?

### Output
The AI suggested using a richer tree-based model as a scenario stress test to search a wider strategy grid. That surfaced a wet street-circuit case where the recommendations diverged.

### Validation
We verified the disagreement on the fitted models: for `qp = 1`, `constructor_tier = top`, `circuit_type = street`, `weather_actual = wet`, the calibrated random forest preferred `two_stop` for `is_top10` and `one_stop` for `is_top5`.

### Adaptations
We corrected the initial narrow search because the logistic model did not expose any disagreement in the sampled grid.

### Final Decision
The final what-if comparison documents the RF stress-test disagreement, and the notebook keeps the logistic model as the primary calibrated midpoint model.

---

*PROMPTS.md format follows the 6-field standard: Context · Prompt · Output · Validation · Adaptations · Final Decision.*

---

## Interaction 7 — Final Report Drafting and Restructuring

### Context
We needed to draft the Final Report (9 required sections) and ensure the writing met the business-sense and honesty requirements without overstating results.

### Prompt
> Draft a section-by-section report outline and prose skeleton for the Final Report, including the mandatory honesty sentence, a non-technical Executive Summary, and an AI reflection paragraph. Keep all claims aligned to the Hito 2 evidence.

### Output
The AI produced a report skeleton with the nine required sections, a metrics table for both targets, a what-if disagreement description, and a suggested honesty sentence with three conditions.

### Validation
We cross-checked all numeric values and the disagreement scenario against the Hito 2 artifacts (baseline_comparison.md, error_analysis.md, whatif_comparison.md). We confirmed the model does not beat the docent floor on `is_top10` and kept that phrasing explicit.

### Adaptations — AI Failure Documented
The AI initially suggested claiming that the `is_top10` model outperformed the docent baseline. We corrected this and explicitly stated the underperformance relative to the docent floor.

### Final Decision
We used the AI-generated structure and wording for several sections but kept all quantitative claims tied to the existing artifacts and added a stricter, testable honesty sentence.
