"""Train and evaluate the attrition models; export metrics, odds ratios,
SHAP values, and the model performance report.

Outputs: outputs/model_metrics.csv, logreg_odds_ratios.csv, shap_importance.csv,
         outputs/model_report.md, reports/figures/{roc_pr_curves,shap_*}.png
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import shap
from sklearn.metrics import (
    average_precision_score, precision_recall_curve, roc_auc_score, roc_curve,
)

from attrition import data as adata
from attrition import modeling as am
from attrition import viz

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "outputs"
FIG = ROOT / "reports" / "figures"

viz.apply_style()

df = adata.clean(adata.load_raw())
result = am.train_and_evaluate(df)
metrics = result["metrics"]
metrics.to_csv(OUT / "model_metrics.csv", index=False)
print(metrics.to_string(index=False))

y_test = result["y_test"]

# ---------------------------------------------------------------------------
# ROC + PR curves
# ---------------------------------------------------------------------------
fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.4))
colors = {"Logistic regression": viz.NAVY, "XGBoost": viz.CORAL}
for name, proba in result["probas"].items():
    fpr, tpr, _ = roc_curve(y_test, proba)
    axes[0].plot(fpr, tpr, color=colors[name], lw=2,
                 label=f"{name} (AUC {roc_auc_score(y_test, proba):.3f})")
    prec, rec, _ = precision_recall_curve(y_test, proba)
    axes[1].plot(rec, prec, color=colors[name], lw=2,
                 label=f"{name} (AP {average_precision_score(y_test, proba):.3f})")
axes[0].plot([0, 1], [0, 1], color=viz.MUTED, ls="--", lw=0.9)
axes[0].set(xlabel="False positive rate", ylabel="True positive rate")
axes[0].set_title("ROC curve (held-out test set)", loc="left", pad=12)
axes[1].axhline(y_test.mean(), color=viz.MUTED, ls="--", lw=0.9,
                label=f"Chance ({y_test.mean():.2f})")
axes[1].set(xlabel="Recall", ylabel="Precision")
axes[1].set_title("Precision-recall curve", loc="left", pad=12)
for ax in axes:
    ax.legend(loc="lower right" if ax is axes[0] else "upper right", fontsize=9)
fig.tight_layout()
fig.savefig(FIG / "roc_pr_curves.png")
plt.close(fig)

# ---------------------------------------------------------------------------
# Interpretability: odds ratios + SHAP
# ---------------------------------------------------------------------------
coefs = am.logreg_odds_ratios(result)
coefs.to_csv(OUT / "logreg_odds_ratios.csv", index=False)
print("\nTop logistic-regression drivers (odds ratio per 1 SD):")
print(coefs.head(12).to_string(index=False))

X_test = result["X_test"]
explainer = shap.TreeExplainer(result["models"]["XGBoost"])
shap_values = explainer.shap_values(X_test)
shap_imp = pd.DataFrame({
    "feature": X_test.columns,
    "mean_abs_shap": np.abs(shap_values).mean(axis=0),
}).sort_values("mean_abs_shap", ascending=False)
shap_imp.round(4).to_csv(OUT / "shap_importance.csv", index=False)
print("\nTop 15 features by mean |SHAP|:")
print(shap_imp.head(15).to_string(index=False))

plt.figure()
shap.summary_plot(shap_values, X_test, max_display=15, show=False)
plt.title("SHAP summary — direction and magnitude of attrition drivers",
          fontsize=13, fontweight="bold", loc="left", pad=16)
plt.tight_layout()
plt.savefig(FIG / "shap_summary.png", dpi=150, bbox_inches="tight")
plt.close()

plt.figure()
shap.summary_plot(shap_values, X_test, plot_type="bar", max_display=15,
                  show=False, color=viz.NAVY)
plt.title("Mean |SHAP| feature importance (XGBoost)",
          fontsize=13, fontweight="bold", loc="left", pad=16)
plt.tight_layout()
plt.savefig(FIG / "shap_bar.png", dpi=150, bbox_inches="tight")
plt.close()

# ---------------------------------------------------------------------------
# Model report
# ---------------------------------------------------------------------------
lr, xgb_row = metrics.iloc[0], metrics.iloc[1]
report = f"""# Model performance report

## Setup
- 1,470 employees, 237 leavers (16.1% positive class). Stratified 75/25
  train/test split; 5-fold CV on the training set for stability.
- {X_test.shape[1]} features after one-hot encoding; label, ID, and
  presentation-only columns excluded (see src/attrition/modeling.py).
- Class imbalance handled via class_weight='balanced' (LR) and
  scale_pos_weight (XGBoost). Accuracy is NOT a headline metric —
  predicting "everyone stays" already scores 84%.

## Results (held-out test set, n={len(y_test)})
| Model | ROC-AUC | PR-AUC | CV ROC-AUC | Recall@op | Precision@op |
|---|---|---|---|---|---|
| Logistic regression | {lr['roc_auc']} | {lr['pr_auc']} | {lr['cv_roc_auc_mean']} ± {lr['cv_roc_auc_std']} | {lr['recall_at_op']:.0%} | {lr['precision_at_op']:.0%} |
| XGBoost | {xgb_row['roc_auc']} | {xgb_row['pr_auc']} | {xgb_row['cv_roc_auc_mean']} ± {xgb_row['cv_roc_auc_std']} | {xgb_row['recall_at_op']:.0%} | {xgb_row['precision_at_op']:.0%} |

PR-AUC baseline (random model) = 0.16. The operating threshold catches
>=70% of true leavers, reflecting asymmetric costs: a retention
conversation with a false positive costs a manager an hour; a missed
leaver costs ~$37K on average.

## What the models agree on
Both rank the same drivers at the top: overtime, low job level / income /
tenure (heavily correlated), frequent business travel, being single,
distance from home, and low job/environment satisfaction. Stock option
level and total working years protect against attrition. Years since last
promotion raises risk once tenure is controlled for.

## Limitations — read before acting on this
1. **Synthetic, cross-sectional data.** IBM-generated fictional snapshot;
   no dates, so no time-based validation or survival analysis. Real
   attrition models should be trained on longitudinal HRIS data and
   validated on a later time window.
2. **Correlation, not causation.** Overtime is the strongest flag, but the
   data cannot prove that reducing overtime reduces attrition — the
   intervention estimates use deliberately discounted effect sizes and
   should be validated with a pilot.
3. **Modest sample.** 237 positive cases means per-role estimates carry
   wide confidence intervals (CV std ~0.03-0.05 AUC).
4. **No compensation benchmarking.** Internal salary only — low earners
   leave more, but we can't tell whether they are underpaid vs market.
5. **Voluntary vs involuntary attrition is not distinguished.** Some
   departures may be terminations, inflating apparent "regrettable"
   attrition and the cost estimate.
"""
(OUT / "model_report.md").write_text(report, encoding="utf-8")
print("\nWrote model outputs and report.")
