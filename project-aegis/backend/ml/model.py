from __future__ import annotations

from pathlib import Path
from joblib import load

from .features import make_features

MODEL_PATH = Path(__file__).resolve().parent / "artifacts" / "aegis_fraud_model.joblib"

_model = None

def get_model():
    global _model
    if _model is None:
        if not MODEL_PATH.exists():
            raise FileNotFoundError(
                f"Trained model not found at {MODEL_PATH}. "
                "Run: python -m ml.train_model"
            )
        _model = load(MODEL_PATH)
    return _model

def predict_fraud_probability(transaction: dict) -> float:
    model = get_model()
    x = [make_features(transaction)]
    return float(model.predict_proba(x)[0][1])
