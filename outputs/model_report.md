# Model performance report

## Setup
- 1,470 employees, 237 leavers (16.1% positive class). Stratified 75/25
  train/test split; 5-fold CV on the training set for stability.
- 44 features after one-hot encoding; label, ID, and
  presentation-only columns excluded (see src/attrition/modeling.py).
- Class imbalance handled via class_weight='balanced' (LR) and
  scale_pos_weight (XGBoost). Accuracy is NOT a headline metric —
  predicting "everyone stays" already scores 84%.

## Results (held-out test set, n=368)
| Model | ROC-AUC | PR-AUC | CV ROC-AUC | Recall@op | Precision@op |
|---|---|---|---|---|---|
| Logistic regression | 0.81 | 0.562 | 0.842 ± 0.044 | 71% | 35% |
| XGBoost | 0.785 | 0.522 | 0.813 ± 0.033 | 71% | 35% |

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
