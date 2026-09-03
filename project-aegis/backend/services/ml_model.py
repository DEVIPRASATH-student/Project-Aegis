"""
Project Aegis -- ML Fraud Detection Model

Trained GradientBoosting classifier for transaction risk scoring.
Uses 9 features extracted from graph analysis and transaction context:

  1. hops_to_nearest_scammer   (graph: shortest path distance)
  2. pagerank_score            (graph: centrality measure)
  3. degree_centrality         (graph: connection density)
  4. receiver_in_fraud_community (graph: community detection)
  5. transaction_amount        (context: normalized amount)
  6. screen_share_active       (context: screen-sharing detected)
  7. is_new_receiver           (context: first transaction to this receiver)
  8. amount_deviation          (context: deviation from typical amount)
  9. clustering_coefficient    (graph: fraud ring tightness)

The model is pre-trained on synthetic data and serialized with joblib
for instant loading during the demo.

Fallback: if the trained model is unavailable, a deterministic
rule-based scorer is used instead.
"""

import os
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

# Attempt to load sklearn and joblib -- graceful fallback if unavailable
try:
    from sklearn.ensemble import GradientBoostingClassifier
    from sklearn.model_selection import train_test_split
    from sklearn.metrics import classification_report, accuracy_score
    import joblib
    SKLEARN_AVAILABLE = True
except ImportError:
    SKLEARN_AVAILABLE = False
    logger.warning("scikit-learn not available; using rule-based scoring only.")


# Path to the pre-trained model file
MODEL_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "models", "trained")
MODEL_PATH = os.path.join(MODEL_DIR, "fraud_model.joblib")

# Feature names (must match training order)
FEATURE_NAMES = [
    "hops_to_nearest_scammer",
    "pagerank_score",
    "degree_centrality",
    "receiver_in_fraud_community",
    "transaction_amount_normalized",
    "screen_share_active",
    "is_new_receiver",
    "amount_deviation",
    "clustering_coefficient",
]


def generate_synthetic_training_data(n_samples: int = 5000, seed: int = 42) -> pd.DataFrame:
    """
    Generate a labeled synthetic dataset of transactions for training.

    Distribution:
      - ~75% legitimate transactions (label=0)
      - ~25% fraudulent transactions (label=1)

    Feature ranges are designed to reflect realistic patterns
    observed in APP fraud scenarios.
    """
    rng = np.random.RandomState(seed)
    records = []

    n_fraud = int(n_samples * 0.25)
    n_legit = n_samples - n_fraud

    # ── Legitimate Transactions ───────────────────────────────────
    # Distributions overlap with fraud to force model to use all features.
    for _ in range(n_legit):
        # Most legit users are far from scammers, but some have shorter paths
        hops = rng.choice([2, 3, 4, 5, 6, 7, 8, -1], p=[0.03, 0.07, 0.12, 0.18, 0.20, 0.15, 0.10, 0.15])
        # Legit users CAN send large amounts (salary transfers, purchases)
        amt = float(np.clip(rng.beta(2, 5) * 1.0, 0.01, 1.0))
        deviation = float(np.clip(rng.beta(2, 5) * 1.0, 0.0, 1.0))
        records.append({
            "hops_to_nearest_scammer": hops,
            "pagerank_score": rng.uniform(0.001, 0.035),
            "degree_centrality": rng.uniform(0.01, 0.10),
            "receiver_in_fraud_community": 1 if rng.random() < 0.08 else 0,
            "transaction_amount_normalized": amt,
            "screen_share_active": 1 if rng.random() < 0.04 else 0,
            "is_new_receiver": 1 if rng.random() < 0.20 else 0,
            "amount_deviation": deviation,
            "clustering_coefficient": rng.uniform(0.0, 0.45),
            "is_fraud": 0,
        })

    # ── Fraudulent Transactions ───────────────────────────────────
    # Fraud has stronger signals across MULTIPLE features, not just amount.
    for _ in range(n_fraud):
        # Fraudulent receivers tend to be closer to scammers but not always
        hops = rng.choice([1, 2, 3, 4, 5, 6], p=[0.12, 0.25, 0.30, 0.18, 0.10, 0.05])
        # Fraud amounts overlap with legit -- some scams are small test amounts
        amt = float(np.clip(rng.beta(5, 2) * 1.0, 0.05, 1.0))
        deviation = float(np.clip(rng.beta(4, 2) * 1.0, 0.1, 1.0))
        records.append({
            "hops_to_nearest_scammer": hops,
            "pagerank_score": rng.uniform(0.008, 0.08),
            "degree_centrality": rng.uniform(0.04, 0.16),
            "receiver_in_fraud_community": 1 if rng.random() < 0.65 else 0,
            "transaction_amount_normalized": amt,
            "screen_share_active": 1 if rng.random() < 0.55 else 0,
            "is_new_receiver": 1 if rng.random() < 0.72 else 0,
            "amount_deviation": deviation,
            "clustering_coefficient": rng.uniform(0.15, 0.75),
            "is_fraud": 1,
        })

    df = pd.DataFrame(records)
    # Replace -1 hops (unreachable) with a high value for the model
    df["hops_to_nearest_scammer"] = df["hops_to_nearest_scammer"].replace(-1, 10)
    return df


def train_model(n_samples: int = 5000) -> Dict[str, Any]:
    """
    Train a GradientBoosting classifier on synthetic fraud data.

    Returns training metrics and saves the model to disk.
    """
    if not SKLEARN_AVAILABLE:
        return {"error": "scikit-learn not installed"}

    df = generate_synthetic_training_data(n_samples=n_samples)

    X = df[FEATURE_NAMES]
    y = df["is_fraud"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    model = GradientBoostingClassifier(
        n_estimators=150,
        max_depth=4,
        learning_rate=0.1,
        min_samples_split=10,
        min_samples_leaf=5,
        subsample=0.8,
        random_state=42,
    )

    model.fit(X_train, y_train)

    # Evaluate
    y_pred = model.predict(X_test)
    accuracy = accuracy_score(y_test, y_pred)
    report = classification_report(y_test, y_pred, output_dict=True)

    # Feature importances
    importances = dict(zip(FEATURE_NAMES, model.feature_importances_))

    # Save model
    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    return {
        "accuracy": round(accuracy, 4),
        "precision_fraud": round(report["1"]["precision"], 4),
        "recall_fraud": round(report["1"]["recall"], 4),
        "f1_fraud": round(report["1"]["f1-score"], 4),
        "feature_importances": {k: round(v, 4) for k, v in sorted(importances.items(), key=lambda x: -x[1])},
        "training_samples": len(X_train),
        "test_samples": len(X_test),
        "model_path": MODEL_PATH,
    }


def load_model():
    """Load the pre-trained model from disk."""
    if not SKLEARN_AVAILABLE:
        return None
    if not os.path.exists(MODEL_PATH):
        logger.info("No pre-trained model found. Training now...")
        train_model()
    if os.path.exists(MODEL_PATH):
        return joblib.load(MODEL_PATH)
    return None


class MLFraudPredictor:
    """
    ML-based fraud risk predictor.

    Uses a trained GradientBoosting model to output a fraud
    probability score (0-100). Falls back to rule-based scoring
    if the ML model is unavailable.
    """

    def __init__(self):
        self.model = load_model()
        self.is_ml_available = self.model is not None

    def predict_risk(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Predict fraud risk from a feature dictionary.

        Args:
            features: Dictionary with keys matching FEATURE_NAMES.

        Returns:
            Dictionary with ml_risk_score (0-100), prediction, and confidence.
        """
        # Prepare feature vector in correct order
        feature_vector = []
        for name in FEATURE_NAMES:
            val = features.get(name, 0.0)
            # Handle -1 hops (unreachable) for the model
            if name == "hops_to_nearest_scammer" and val == -1:
                val = 10
            feature_vector.append(float(val))

        if self.is_ml_available and self.model is not None:
            try:
                X = np.array([feature_vector])
                proba = self.model.predict_proba(X)[0]
                fraud_probability = proba[1] if len(proba) > 1 else proba[0]
                prediction = int(self.model.predict(X)[0])

                return {
                    "ml_risk_score": round(fraud_probability * 100, 2),
                    "ml_prediction": "FRAUD" if prediction == 1 else "LEGITIMATE",
                    "ml_confidence": round(max(proba) * 100, 2),
                    "model_type": "GradientBoosting",
                    "using_ml": True,
                }
            except Exception as e:
                logger.error(f"ML prediction failed: {e}")

        # Fallback: rule-based scoring
        return self._rule_based_score(features)

    def _rule_based_score(self, features: Dict[str, float]) -> Dict[str, Any]:
        """
        Deterministic rule-based scoring as fallback.
        Weighted combination of features.
        """
        score = 0.0

        # Hop distance (major factor, 35%)
        hops = features.get("hops_to_nearest_scammer", -1)
        if hops == -1 or hops > 6:
            score += 5
        elif hops <= 1:
            score += 35
        elif hops <= 2:
            score += 30
        elif hops <= 3:
            score += 25
        elif hops <= 4:
            score += 15
        else:
            score += 8

        # Screen share (significant factor, 25%)
        if features.get("screen_share_active", 0):
            score += 25

        # Amount (moderate factor, 15%)
        amount_norm = features.get("transaction_amount_normalized", 0)
        score += amount_norm * 15

        # Fraud community (15%)
        if features.get("receiver_in_fraud_community", 0):
            score += 15

        # New receiver (10%)
        if features.get("is_new_receiver", 0):
            score += 10

        score = min(max(score, 0), 100)

        return {
            "ml_risk_score": round(score, 2),
            "ml_prediction": "FRAUD" if score >= 50 else "LEGITIMATE",
            "ml_confidence": round(abs(score - 50) * 2, 2),
            "model_type": "rule_based_fallback",
            "using_ml": False,
        }


# Module-level singleton
_predictor_instance: Optional[MLFraudPredictor] = None


def get_ml_predictor() -> MLFraudPredictor:
    """Get or create the singleton ML predictor instance."""
    global _predictor_instance
    if _predictor_instance is None:
        _predictor_instance = MLFraudPredictor()
    return _predictor_instance
