# Demo Day — 7-Minute Pitch Script
**F1 Race Strategy Advisor · Ariel Van Kilsdonk & David Hernández**

---

> **How to use this script**
> - Read it aloud with a timer. Target pace: ~120 words/minute = ~840 words for 7 min.
> - The `[SLIDE X]` markers are your cue to advance.
> - Speaker assignments are suggestions — adjust based on comfort, but both must speak roughly equally.
> - Practice until you no longer need to read it. The jury penalizes reading from slides.

---

## PRE-PITCH (before the clock starts)

*Both presenters standing. One at the clicker, one slightly to the side.*

---

## [SLIDE 1] Context + Decision — Ariel speaks (target: 60 seconds)

"Good afternoon. Imagine you're the race engineer for a top constructor.
It's 90 minutes before lights out at a wet street circuit.
Your driver qualified P1. You need to decide: one stop or two?

That is the exact decision this tool was built to support.

We built a scenario-comparison tool that outputs two calibrated probabilities
for each candidate strategy: the probability of finishing in the top 10 —
which is points survival — and the probability of finishing in the top 5 —
which is top-end conversion.

The decision this tool supports is: *which stop count gives the best
probability of finishing top 10 versus top 5 — and do those two answers agree?*

[pause — let that land]

As we'll show you in 60 seconds: they don't always agree."

---

## [SLIDE 2] Approach — David speaks (target: 90 seconds)

"Let me walk you through the approach quickly.

Our dataset is 2,447 driver-race entries across six seasons, 2019 to 2024,
from the official course file.

The temporal split is locked: we train on 2019 to 2021, calibrate on 2022 only —
we chose 2022 because the aerodynamic regulation change makes it a natural
structural break from the training era — and we evaluate on 2023 and 2024,
touched once, at the end.

We model two binary targets. is_top10 is the primary target — finishing in the
top 10 awards constructor points, which is the currency engineers optimize for.
is_top5 is our expansion target — it separates a strong points haul from
just surviving inside the points.

The model is calibrated logistic regression. We use qualifying position,
constructor tier, and circuit type as pre-race predictors. Stop count and
compound sequence are scenario inputs — what-if controls set by the engineer,
not features we sniff from the future.

Calibration matters here because the output is a probability used in a
live decision. We apply Platt scaling on the 2022 block, and the test set
is never touched until the final evaluation."

---

## [SLIDE 3] Results — Ariel speaks (target: 90 seconds)

"Here are the results on the 2023–2024 test set.

[point to table]

For is_top10: our calibrated model achieves a Brier score of 0.1447.
The heuristic baseline — a grid-position bracket rule — scores 0.1669.
We beat the heuristic. But we do *not* beat the docent floor of 0.1320.
We're reporting that honestly. This model is not ready for deployment on is_top10.

For is_top5: Brier 0.0958 against a heuristic of 0.1227.
That's a reduction of 0.027 — meaningful for a target this strict.
ROC-AUC of 0.9217 shows strong discrimination.

[point to calibration plot]

The calibration curve for is_top10 shows visible overconfidence in the
0.3-to-0.7 range — that's the midfield slice, and it's our hardest failure case.
is_top5 tracks the diagonal more closely, which is consistent with the lower Brier.

The headline: competitive on both targets, honest about where we fall short."

---

## [SLIDE 4] The Trade-off — David speaks (target: 60 seconds)

"Now — the centerpiece.

[point to scenario header]

Scenario: qualifying P1, top constructor, street circuit, wet race.
We run four strategy options through a calibrated random forest stress test.

[point to the two highlighted rows]

is_top10 prefers two-stop — 0.7251 versus 0.7196 for one-stop.
is_top5 prefers one-stop — 0.6014 versus 0.5956 for two-stop.

The targets disagree.

[pause]

What does this mean operationally?
If your only goal is to keep the car inside the points, the more aggressive
two-stop gives you a marginal edge.
If your goal is to convert this run into a top-5 finish — which is the
difference between 10 points and 25 — the conservative one-stop is better.

A grid-position heuristic cannot tell you this. It assigns the same probability
regardless of stop count.
Our tool is the only artifact in this workflow that surfaces this trade-off."

---

## [SLIDE 5] Verdict + Honesty — Ariel speaks (target: 30 seconds + outro)

"Our verdict:

Use this tool for structured scenario comparison — specifically when you need
to distinguish between the points-survival-optimal strategy and the
top-5-optimal strategy.

Do not use it as a single-number oracle.

[read the three conditions — slowly and clearly]

We do not recommend deploying this tool unless:
One — it is re-evaluated on at least one future season beyond 2024,
achieving Brier at or below 0.1320 on is_top10.
Two — scenario sensitivity is validated on at least three real race
disagreement cases where our recommendation differed from the observed decision.
Three — calibration for wet and midfield slices stays within 0.02 Brier
of the overall test score on the new season.

Thank you."

---

## TIMING GUIDE

| Slide | Cumulative target | Speaker |
|-------|------------------|---------|
| 1 | 1:00 | Ariel |
| 2 | 2:30 | David |
| 3 | 4:00 | Ariel |
| 4 | 5:00 | David |
| 5 | 5:30 → 7:00 | Ariel |

> **Rule**: if you hit 6:00 and you're still on slide 3, skip to slide 4 immediately.
> If you finish slide 5 early, hold the closing line — do not fill silence with extras.

---

## REHEARSAL NOTES

- **Stand.** Do not sit. Both presenters visible.
- **Timer face-up** on the desk or desk edge.
- **Advance the slide** only on the `[SLIDE X]` cue — not before.
- **Do not read the slide text verbatim.** The slides support you, they do not replace you.
- **The pause after "they don't always agree"** (slide 1) and the pause after showing the disagreement (slide 4) are deliberate. Hold them for 2 seconds.
- **The honesty sentence** on slide 5 should be delivered calmly and confidently. It is a strength, not a weakness. Say it like you mean it.
