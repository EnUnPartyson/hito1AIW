# Demo Day — Q&A Preparation Guide
**F1 Race Strategy Advisor · Ariel Van Kilsdonk & David Hernández**

---

> **How to use this guide**
> Read each question out loud. Answer it out loud without looking at the answer.
> Then check your answer against the template below.
> A memorized answer is NOT the goal — understanding that lets you adapt is.

---

## CATEGORY 1 — Methodology

### Q1: "Why did you use the 2022 season specifically as your calibration block and not just add it to training?"

**What's being tested:** Do you understand your own split design, not just that you did it?

**Answer template:**
"Two reasons. First, 2022 introduced a major aerodynamic regulation change — ground-effect cars replaced the previous aero philosophy — which shifted the competitive grid order significantly. Red Bull's dominance began there. Training on that data and using it for calibration would mix two structurally different eras. Second, using 2022 only for Platt scaling means our calibration reflects the post-regulation-change probability distribution, without contaminating the 2019–2021 training signal with a different competitive landscape."

---

### Q2: "Why logistic regression and not a gradient boosted model like LightGBM?"

**What's being tested:** Whether you chose your model for domain reasons, not just convention.

**Answer template:**
"Three reasons specific to this problem. One: interpretability — a strategy engineer can look at the logistic coefficients and understand how grid position and compound sequence shift the log-odds. That auditability matters for a decision-support tool. Two: calibration stability — logistic regression outputs are closer to well-calibrated probabilities on small structured datasets than tree ensembles, which are known to need more aggressive calibration correction. Three: the dataset has 1,132 training rows with a small feature set. That favors a low-variance model. We did use a random forest as a stress test to search for the disagreement scenario, but it's not our primary reported model."

---

### Q3: "What does 'Platt scaling' actually do?"

**What's being tested:** Whether you understand calibration beyond the name.

**Answer template:**
"Platt scaling fits a sigmoid — a logistic function — on top of the model's raw probability outputs, using a held-out dataset. In our case, the model outputs raw probabilities on the 2022 block, and we fit a sigmoid that maps those raw outputs to better-calibrated probabilities. The effect is to compress overconfident predictions — if the model was outputting 0.9 but only 80% of those cases actually finished top 10, the sigmoid pulls that output down toward 0.8. After calibration, the probabilities better reflect true frequencies in the data."

---

## CATEGORY 2 — Honesty

### Q4: "What's the worst case for your tool — where would you least trust it?"

**What's being tested:** Whether you can name a specific failure slice with evidence, not a generic disclaimer.

**Answer template:**
"Two clear worst cases, both backed by our slice analysis. For is_top10, the midfield constructor tier is hardest — Brier 0.1700, our worst single slice. That's exactly where the model sits near the decision boundary, and small unobserved pace changes can swing the result above or below the top-10 cutoff. For is_top5, front-running teams are hardest — Brier 0.1972. The model has to separate 'already finishing well' from 'finishing on the podium,' and that boundary is where calibration errors hurt most because the probabilities are near 0.7 to 0.9. Both of these get worse in wet conditions — wet is_top5 is 0.1183 versus 0.0923 in dry — which is also where strategy confounding is strongest."

---

### Q5: "Your is_top10 model doesn't beat the docent floor. Why should we use it at all?"

**What's being tested:** Whether you can defend the work honestly without overselling.

**Answer template:**
"Fair challenge. For is_top10 alone, we wouldn't claim superiority over the docent reference. But the docent baseline is scenario-insensitive — it assigns the same probability regardless of stop count. Our model is the only one in this workflow that can compare a 1-stop against a 2-stop and output different probabilities for each. The value is not 'our Brier is lower' — the value is the scenario comparison capability and the dual-target disagreement surface. For is_top5, we do meaningfully beat the heuristic by 0.027 Brier. And the combination — the disagreement between the two targets — is what a strategy engineer actually needs, because survival and top-5 conversion are different objectives."

---

## CATEGORY 3 — Decision Value

### Q6: "Why should a strategy engineer use this instead of just calling an expert or using the grid-position rule?"

**What's being tested:** Whether you can articulate a specific, differentiated value-add.

**Answer template:**
"The grid-position heuristic tells you one number regardless of strategy. It cannot distinguish between 'one-stop gives P(top10) = 0.72' and 'two-stop gives P(top10) = 0.73.' It has no stop-count dimension at all. Our tool surfaces exactly that difference, and — more importantly — it surfaces cases where the best strategy for P(top10) and the best strategy for P(top5) diverge. In our wet street-circuit scenario, two-stop maximizes survival and one-stop maximizes top-5 conversion. A strategy engineer who only asks 'will we score points?' will miss that trade-off entirely. Our tool makes it visible. Whether they act on it is still the engineer's decision."

---

## CATEGORY 4 — Calibration / Probability

### Q7: "What does P(top10) = 0.73 actually mean for this driver in this race?"

**What's being tested:** Whether you understand probability as more than a ranking score.

**Answer template:**
"It means: in the historical distribution of races with the same pre-race context — same grid position, same constructor tier, same circuit type — and the same declared strategy, drivers finished in the top 10 approximately 73% of the time. It does not mean this driver will finish top 10. It is a frequency estimate, conditional on the assumed pace profile being similar to the training distribution. It is not causal — we're not saying the strategy caused the result, we're saying that in similar historical situations, this strategy was associated with a 73% top-10 rate. The engineer uses it to compare two options and pick the one with better expected outcomes."

---

### Q8: "Your calibration curve shows the model is overconfident in the 0.3–0.7 range. What does that mean in practice?"

**What's being tested:** Whether you can translate a calibration plot into operational consequences.

**Answer template:**
"It means that when the model outputs, say, 0.6 for P(top10), the true empirical rate in the test set is closer to 0.5 — the model is more confident than it should be. For a strategy engineer, the consequence is that the model may nudge you toward a strategy it's 'confident' about when the real probability is lower. That's why we don't recommend using this as a single-number oracle. The calibration is better on is_top5 — its curve tracks the diagonal more closely — but both have enough deviation that we put the uncertainty bounds on the honesty conditions."

---

## CATEGORY 5 — Domain / F1 Specific

### Q9: "If I deploy this for the Monaco Grand Prix, what happens?"

**What's being tested:** Whether you can reason about your model in a specific F1 context.

**Answer template:**
"Monaco is a semi-street circuit, not a street circuit in our dataset — so the model is drawing on semi-street circuit training examples, not Monaco-specific data. The semi-street slice is actually our hardest is_top10 slice, Brier 0.1774. The circuit-specific training data is limited because Monaco only runs once per season. More importantly, Monaco is famous for track position being almost irreplaceable once lost — overtaking is nearly impossible. Our model doesn't capture that overtaking difficulty because we don't have a track-position-defense feature. The strategy confounding is particularly strong there: a driver who stays out does so because they CAN hold position. The model would probably assign similar probabilities to both strategies because it's learned from circuits where track position dynamics are less extreme. That's a known gap, and it's one of the reasons condition 2 on our honesty sentence requires validation on specific race disagreement cases before deployment."

---

### Q10: "Your scenario uses weather_actual as a conditioning variable. Isn't that post-race data — isn't that leakage?"

**What's being tested:** Whether you understand your own leakage audit.

**Answer template:**
"Good catch. weather_actual is classified as an audit-only slice in our leakage audit — it's not a model feature. What we did in the what-if comparison is use it as a filter to identify the wet-street-circuit regime in the test set rows, then run the RF stress test on that subset. The model itself never sees weather_actual as an input — it was trained and calibrated without it. The conditioning is purely analytical: we're asking 'among races that happened to be wet street circuits, does the disagreement appear?' We're not feeding the model real-time weather. In a deployment scenario, the engineer would need to specify the weather forecast and the model would need weather as an explicit feature, which is a future improvement."

---

## QUICK NUMBERS — memorize these

| Fact | Value |
|------|-------|
| Training rows | 1,132 |
| Test rows | 889 |
| is_top10 Brier | 0.1447 |
| is_top10 docent floor | 0.1320 |
| is_top5 Brier | 0.0958 |
| is_top5 heuristic | 0.1227 |
| ROC-AUC is_top10 | 0.8726 |
| ROC-AUC is_top5 | 0.9217 |
| Worst is_top10 slice | midfield 0.1700 |
| Worst is_top5 slice | front 0.1972 |
| Disagreement: two_stop P(top10) | 0.7251 |
| Disagreement: one_stop P(top5) | 0.6014 |
| Seasons | 2019–2024 |
| Total rows | 2,447 |

---

## THE GOLDEN RULE FOR Q&A

If you don't know → say: **"That's a question I'd need more time to answer properly. My best guess is X, but I haven't tested it."**

This scores higher than a wrong confident answer. It scores the same as or better than silence.

If you spot an error in your own slide → name it: **"Looking at this now, I think the number I just said was wrong — the actual value is X."**

This is rewarded. Defending a wrong claim is not.
