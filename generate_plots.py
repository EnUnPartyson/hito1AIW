"""
Standalone script to generate calibration curve PNGs.
Reproduces exactly the model fitting and plotting logic from hito2_modeling.ipynb.
Run with: conda run -n iit414w python generate_plots.py
"""
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from sklearn.metrics import brier_score_loss, roc_auc_score
from sklearn.calibration import calibration_curve, CalibratedClassifierCV
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import OneHotEncoder

RANDOM_SEED = 414
np.random.seed(RANDOM_SEED)

# --- Load ---
df = pd.read_csv('f1_strategy_race_level.csv')
df['is_top5'] = (df['finish_position'] <= 5).astype(int)

# --- Split ---
train = df[df['season'].isin([2019, 2020, 2021])].copy()
calib = df[df['season'] == 2022].copy()
test  = df[df['season'].isin([2023, 2024])].copy()

# --- Encode ---
features = ['qualifying_position', 'constructor_tier', 'n_stops',
            'compound_sequence', 'circuit_type', 'weather_actual']
for col in ['constructor_tier', 'compound_sequence', 'circuit_type', 'weather_actual']:
    df[col] = df[col].fillna('unknown')
    train[col] = train[col].fillna('unknown')
    calib[col] = calib[col].fillna('unknown')
    test[col]  = test[col].fillna('unknown')

cat_cols = ['constructor_tier', 'compound_sequence', 'circuit_type', 'weather_actual']
enc = OneHotEncoder(sparse_output=False, handle_unknown='ignore')
enc.fit(df[cat_cols])

def encode(X):
    X_num = X[['qualifying_position', 'n_stops']].values
    X_cat = enc.transform(X[cat_cols])
    return np.hstack([X_num, X_cat])

Xtr = encode(train); Xte = encode(test); Xca = encode(calib)
ytr10 = train['is_top10'].values; yte10 = test['is_top10'].values; yca10 = calib['is_top10'].values
ytr5  = train['is_top5'].values;  yte5  = test['is_top5'].values;  yca5  = calib['is_top5'].values

# --- Fit + calibrate ---
m10 = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED).fit(Xtr, ytr10)
m5  = LogisticRegression(max_iter=1000, random_state=RANDOM_SEED).fit(Xtr, ytr5)
cal10 = CalibratedClassifierCV(estimator=m10, cv='prefit', method='sigmoid').fit(Xca, yca10)
cal5  = CalibratedClassifierCV(estimator=m5,  cv='prefit', method='sigmoid').fit(Xca, yca5)
p10 = cal10.predict_proba(Xte)[:, 1]
p5  = cal5.predict_proba(Xte)[:, 1]

print(f"is_top10 — Brier: {brier_score_loss(yte10, p10):.4f}  ROC-AUC: {roc_auc_score(yte10, p10):.4f}")
print(f"is_top5  — Brier: {brier_score_loss(yte5, p5):.4f}  ROC-AUC: {roc_auc_score(yte5, p5):.4f}")

# --- Plot calibration curves ---
def plot_calibration(y_true, y_pred, label, filename):
    frac_pos, mean_pred = calibration_curve(y_true, y_pred, n_bins=5, strategy='quantile')
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.plot([0, 1], [0, 1], 'k--', lw=1.2, label='Perfectly calibrated')
    ax.plot(mean_pred, frac_pos, 'o-', color='steelblue', lw=1.8, ms=7, label=f'Model ({label})')
    ax.set_xlabel('Mean predicted probability', fontsize=12)
    ax.set_ylabel('Fraction of positives', fontsize=12)
    ax.set_title(f'Reliability Diagram — {label}\n(test set 2023–2024)', fontsize=12)
    ax.legend(fontsize=11)
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    fig.tight_layout()
    fig.savefig(filename, dpi=150)
    plt.close(fig)
    print(f"Saved {filename}")

plot_calibration(yte10, p10, 'is_top10', 'calibration_curve_top10.png')
plot_calibration(yte5,  p5,  'is_top5',  'calibration_curve_top5.png')
print("Done.")
