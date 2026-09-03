# Aegis ML Upgrade

This adds a CPU-friendly hybrid ML layer to the existing Aegis architecture.

## Why this model?

`HistGradientBoostingClassifier` is a strong fit for tabular fraud features:
- fast training/inference on CPU
- captures nonlinear interactions
- no neural-network infrastructure
- compact serialized artifact
- works well for mixed behavioral/risk features

## Important

The included dataset is **synthetic demo data**. It is useful for demonstrating the ML pipeline, not for claiming real-world fraud-detection accuracy.

For production, retrain and validate on institution-approved, privacy-safe transaction data with confirmed fraud labels and time-based validation.

## Train

From `backend/`:

```bash
pip install -r requirements.txt
python -m ml.train_model
```

The trained artifact is written to:

```text
backend/ml/artifacts/aegis_fraud_model.joblib
```

## Features

- transaction amount
- graph distance to known risk node
- screen-share demo signal
- new beneficiary
- beneficiary age
- device change
- transaction velocity
- unusual hour
- sender account age
- amount-vs-average ratio
- prior fraud reports

## Integration

`services/risk_scorer.py` can call:

```python
from ml.model import predict_fraud_probability
```

and combine the probability with the explainable NetworkX graph signal.

Do not use a model probability alone to freeze real customer funds. Production decisions require authorized banking controls, calibrated thresholds, monitoring, human/step-up review where appropriate, and regulatory/compliance validation.
