from __future__ import annotations

from pathlib import Path
import pandas as pd
from joblib import dump
from sklearn.ensemble import HistGradientBoostingClassifier
from sklearn.metrics import (
    average_precision_score,
    classification_report,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split

from .features import FEATURE_NAMES

ROOT = Path(__file__).resolve().parent
DATA = ROOT / "artifacts" / "training_data.csv"
MODEL = ROOT / "artifacts" / "aegis_fraud_model.joblib"

def main():
    df = pd.read_csv(DATA)
    X = df[[
        "amount", "graph_hops", "screen_share", "new_beneficiary",
        "beneficiary_age_days", "device_change", "velocity_1h",
        "velocity_24h", "odd_hour", "sender_age_days",
        "amount_to_avg_ratio", "prior_fraud_reports"
    ]].copy()

    # Match inference-time transformations.
    X["amount"] = X["amount"].clip(lower=1).map(__import__("math").log1p)
    X["beneficiary_age_days"] = X["beneficiary_age_days"].clip(lower=0).map(__import__("math").log1p)
    X["sender_age_days"] = X["sender_age_days"].clip(lower=1).map(__import__("math").log1p)
    X["amount_to_avg_ratio"] = X["amount_to_avg_ratio"].clip(lower=.01).map(__import__("math").log)
    X = X.rename(columns={
        "amount": "log_amount",
        "beneficiary_age_days": "log_beneficiary_age_days",
        "sender_age_days": "log_sender_age_days",
        "amount_to_avg_ratio": "log_amount_to_avg_ratio",
    })
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=.20, random_state=42, stratify=y
    )

    # Fast CPU-friendly model. class_weight helps with fraud imbalance.
    model = HistGradientBoostingClassifier(
        learning_rate=0.08,
        max_iter=220,
        max_leaf_nodes=31,
        min_samples_leaf=35,
        l2_regularization=1.0,
        class_weight="balanced",
        random_state=42,
    )
    model.fit(X_train, y_train)

    p = model.predict_proba(X_test)[:, 1]
    print(f"Rows: {len(df):,}")
    print(f"Fraud rate: {y.mean():.3%}")
    print(f"ROC-AUC: {roc_auc_score(y_test, p):.4f}")
    print(f"PR-AUC:  {average_precision_score(y_test, p):.4f}")
    print(classification_report(y_test, p >= .50, digits=4))

    dump(model, MODEL, compress=3)
    print(f"Saved model: {MODEL}")

if __name__ == "__main__":
    main()
