"""
subscription_churn.py
=======================
Predicts which recurring produce-box subscribers are at risk of cancelling —
directly serves the brief's "subscription model for regular deliveries"
objective by making it retention-aware rather than just a billing feature.

Trained on the marketplace's own subscription data. Retention there was
DELIBERATELY made feature-dependent when generated (see
marketplace_entities.generate_subscriptions), not pure noise, so this
classifier has genuine, recoverable signal to find — exactly the situation
a real early-stage subscription product would be in before it has enough
history for the "real" ground truth.
"""

import pandas as pd
import numpy as np
from pathlib import Path
from sklearn.model_selection import cross_val_predict, StratifiedKFold
from sklearn.linear_model import LogisticRegression
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.metrics import accuracy_score, roc_auc_score

PROCESSED_DIR = Path(__file__).resolve().parent.parent / "data" / "processed"


def train_churn_model() -> dict:
    """
    With only ~144 subscriptions, a gradient-boosted model on a single held-out
    split produces unstable, meaningless metrics (verified: it scored WORSE
    than random on first attempt here — a real failure worth reporting, not
    hiding). At this sample size the honest choices are: (a) a simpler, lower-
    variance model (logistic regression), and (b) 5-fold cross-validated
    predictions instead of one small test split, so every subscription gets an
    out-of-fold prediction and the reported metric isn't a fluke of which 36
    rows happened to land in the test set.
    """
    subs = pd.read_csv(PROCESSED_DIR / "subscriptions.csv")
    y = (~subs["still_active"]).astype(int)  # 1 = churned

    X = subs[["tenure_days", "box_value", "price_sensitivity"]].copy()
    le = LabelEncoder()
    X["frequency_enc"] = le.fit_transform(subs["frequency"])
    X_scaled = StandardScaler().fit_transform(X)

    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    model = LogisticRegression(max_iter=1000, class_weight="balanced")

    oof_proba = cross_val_predict(model, X_scaled, y, cv=cv, method="predict_proba")[:, 1]
    oof_preds = (oof_proba >= 0.5).astype(int)

    metrics = {
        "n": len(subs), "cv_folds": 5,
        "accuracy": round(accuracy_score(y, oof_preds), 4),
        "roc_auc": round(roc_auc_score(y, oof_proba), 4),
    }

    # Fit on full data for interpretable coefficients (direction/magnitude of each driver)
    full_model = LogisticRegression(max_iter=1000, class_weight="balanced").fit(X_scaled, y)
    metrics["coefficients"] = dict(sorted(
        zip(X.columns, full_model.coef_[0].round(3)), key=lambda x: -abs(x[1])
    ))

    subs["churn_risk_score"] = (oof_proba * 100).round(1)
    subs["churn_risk_tier"] = pd.cut(subs["churn_risk_score"], bins=[-1, 25, 50, 75, 101],
                                      labels=["Low", "Medium", "High", "Critical"])
    subs.to_csv(PROCESSED_DIR / "subscription_churn_scores.csv", index=False)

    return {"metrics": metrics, "subs": subs}


if __name__ == "__main__":
    results = train_churn_model()
    m = results["metrics"]
    print(f"N={m['n']}, {m['cv_folds']}-fold cross-validated (out-of-fold) predictions")
    print(f"Accuracy: {m['accuracy']}   ROC-AUC: {m['roc_auc']}\n")
    print("Logistic regression coefficients (standardized; sign = direction of effect):")
    for feat, coef in m["coefficients"].items():
        print(f"  {feat}: {coef:+.3f}")

    subs = results["subs"]
    print(f"\nCurrent active subscriptions: {subs['still_active'].sum()} / {len(subs)}")
    print("\nChurn risk tier distribution:")
    print(subs["churn_risk_tier"].value_counts())
