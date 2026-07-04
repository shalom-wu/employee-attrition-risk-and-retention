"""Attrition prediction: logistic regression baseline + XGBoost challenger.

Class imbalance (16% positive) is handled with class weights /
scale_pos_weight; evaluation reports ROC-AUC and PR-AUC rather than
accuracy (predicting "everyone stays" already scores 84%). The operating
threshold is chosen for a retention use-case: catch >=70% of true leavers,
tolerating false positives, because a retention conversation with a false
positive costs a manager an hour while a missed leaver costs ~$37K.
"""

import numpy as np
import pandas as pd
import xgboost as xgb
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    average_precision_score,
    confusion_matrix,
    precision_recall_curve,
    roc_auc_score,
)
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler

RANDOM_STATE = 42

# Label, ID, and presentation-only derived columns — never model inputs.
NON_FEATURES = [
    "Attrition", "AttritionFlag", "EmployeeNumber",
    "TenureBand", "IncomeQuartile", "JobSatisfactionLabel",
]


def prepare_features(df: pd.DataFrame):
    """One-hot encode nominal categoricals; ordinal 1-4/1-5 codes stay numeric."""
    y = df["AttritionFlag"]
    X_raw = df.drop(columns=[c for c in NON_FEATURES if c in df.columns])
    cat_cols = X_raw.select_dtypes(include=["object", "str"]).columns.tolist()
    X = pd.get_dummies(X_raw, columns=cat_cols, drop_first=True)
    return X, y


def make_models(y_train: pd.Series) -> dict:
    spw = (y_train == 0).sum() / (y_train == 1).sum()
    return {
        "Logistic regression": Pipeline([
            ("scale", StandardScaler()),
            ("clf", LogisticRegression(class_weight="balanced", max_iter=5000, C=0.1)),
        ]),
        "XGBoost": xgb.XGBClassifier(
            n_estimators=400, max_depth=3, learning_rate=0.05,
            subsample=0.8, colsample_bytree=0.8, min_child_weight=5,
            reg_lambda=2.0, scale_pos_weight=spw,
            eval_metric="auc", random_state=RANDOM_STATE, n_jobs=-1,
        ),
    }


def evaluate(name, y_test, proba, min_recall=0.70) -> dict:
    """Test-set metrics plus precision/recall at the retention operating point."""
    prec, rec, thr = precision_recall_curve(y_test, proba)
    ok = rec[:-1] >= min_recall
    op_thr = float(thr[ok][-1]) if ok.any() else 0.5
    pred = (proba >= op_thr).astype(int)
    tn, fp, fn, tp = confusion_matrix(y_test, pred).ravel()
    return {
        "model": name,
        "roc_auc": round(roc_auc_score(y_test, proba), 3),
        "pr_auc": round(average_precision_score(y_test, proba), 3),
        "op_threshold": round(op_thr, 3),
        "recall_at_op": round(tp / (tp + fn), 3),
        "precision_at_op": round(tp / (tp + fp), 3),
        "flagged_employees": int(tp + fp),
        "true_leavers_caught": int(tp),
        "leavers_missed": int(fn),
    }


def train_and_evaluate(df: pd.DataFrame) -> dict:
    """Full pipeline: split, 5-fold CV, fit, test-set evaluation.

    Returns dict with fitted models, metrics DataFrame, predicted
    probabilities, and the train/test split for downstream plots/SHAP.
    """
    X, y = prepare_features(df)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.25, stratify=y, random_state=RANDOM_STATE
    )
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    models = make_models(y_train)

    rows, probas = [], {}
    for name, model in models.items():
        cv_auc = cross_val_score(model, X_train, y_train, cv=cv, scoring="roc_auc")
        model.fit(X_train, y_train)
        proba = model.predict_proba(X_test)[:, 1]
        row = evaluate(name, y_test, proba)
        row["cv_roc_auc_mean"] = round(cv_auc.mean(), 3)
        row["cv_roc_auc_std"] = round(cv_auc.std(), 3)
        rows.append(row)
        probas[name] = proba

    return {
        "models": models,
        "metrics": pd.DataFrame(rows),
        "probas": probas,
        "X_train": X_train, "X_test": X_test,
        "y_train": y_train, "y_test": y_test,
    }


def logreg_odds_ratios(result: dict) -> pd.DataFrame:
    """Odds ratios per 1 SD of each feature, sorted by effect size."""
    pipe = result["models"]["Logistic regression"]
    coefs = pd.DataFrame({
        "feature": result["X_train"].columns,
        "coef_per_sd": pipe.named_steps["clf"].coef_[0],
    })
    coefs["odds_ratio_per_sd"] = np.exp(coefs["coef_per_sd"]).round(3)
    return coefs.reindex(
        coefs["coef_per_sd"].abs().sort_values(ascending=False).index
    ).round(3)
