# README — F1 Race Strategy Advisor: Final Report

**Team:** Ariel Van Kilsdonk & David Hernandez  
**Course:** Module 5 — Unit IV Capstone  
**Submission:** Final Report — Reproducible Report + Repo Tag

---

## What’s in this repo

| File | Description |
|---|---|
| `hito1_baseline.ipynb` | Hito 1 baseline notebook (heuristic model, framing, leakage audit) |
| `hito2_modeling.ipynb` | Main notebook: dual-target calibration, error analysis, what-if comparison |
| `baseline_comparison.md` | Baseline comparison on both targets |
| `error_analysis.md` | Slice-based error analysis on both targets |
| `whatif_comparison.md` | Strategy disagreement case across targets |
| `leakage_audit.md` | Leakage / confounding checklist |
| `mitigations.md` | Risks and mitigations tied to observed failures |
| `PROMPTS.md` | AI usage log (Hito 1, Hito 2, and Final Report writing phase) |
| `README.md` | This file |

---

## Environment

- Python 3.11
- All results reproduced with `RANDOM_SEED = 414`
- Conda spec: environment.yml

Create the environment:

```bash
conda env create -f environment.yml
conda activate iit414w-f1-strategy
```

All dependencies are pinned in `environment.yml`. Do not install packages manually — use the conda environment above to ensure reproducibility.

---

## Data

Place `f1_strategy_race_level.csv` in the repo directory, alongside the notebook.

The notebook uses the official race-level target columns directly:

- `is_top10` from the dataset
- `is_top5` derived from `finish_position`

---

## Run (End-to-end)

Run the notebooks in order:

```bash
jupyter notebook hito1_baseline.ipynb   # Hito 1 — baseline and framing
jupyter notebook hito2_modeling.ipynb   # Hito 2 — calibration, error analysis, what-if
```

For each notebook use **Kernel → Restart & Run All**. The notebook is designed around the locked split:

- Train: 2019–2021
- Calibration: 2022
- Test: 2023–2024

Expected runtime on a standard laptop is under 10 minutes.

---

## Targets

- `is_top10`: primary cohort-comparison target
- `is_top5`: expansion target chosen because it exposes top-end strategy trade-offs that top-10 alone can hide

---

## Key Results

- Calibrated logistic regression on `is_top10`: Brier 0.1447, ROC-AUC 0.8726
- Calibrated logistic regression on `is_top5`: Brier 0.0958, ROC-AUC 0.9217
- Baseline heuristic Brier on `is_top10`: 0.1669
- Baseline heuristic Brier on `is_top5`: 0.1227

---

## Notes

- `n_stops` and `compound_sequence` are treated as scenario inputs, not predictors.
- The notebook includes a scenario-disagreement example found with a calibrated random forest stress test because the logistic model stayed monotonic on the sampled grid.
- The model is not a deployment-ready system.
- Calibration plots are saved to `calibration_curve_top10.png` and `calibration_curve_top5.png` when the notebook is run.
