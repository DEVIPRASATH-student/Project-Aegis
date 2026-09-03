from __future__ import annotations

import math
from typing import Mapping, Any

FEATURE_NAMES = [
    "log_amount",
    "graph_hops",
    "screen_share",
    "new_beneficiary",
    "log_beneficiary_age_days",
    "device_change",
    "velocity_1h",
    "velocity_24h",
    "odd_hour",
    "log_sender_age_days",
    "log_amount_to_avg_ratio",
    "prior_fraud_reports",
]

def make_features(tx: Mapping[str, Any]) -> list[float]:
    amount = max(float(tx.get("amount", 0)), 1.0)
    beneficiary_age = max(float(tx.get("beneficiary_age_days", 365)), 0.0)
    sender_age = max(float(tx.get("sender_age_days", 365)), 1.0)
    ratio = max(float(tx.get("amount_to_avg_ratio", 1.0)), 0.01)

    return [
        math.log1p(amount),
        float(tx.get("graph_hops", 99)),
        float(bool(tx.get("screen_share", False))),
        float(bool(tx.get("new_beneficiary", False))),
        math.log1p(beneficiary_age),
        float(bool(tx.get("device_change", False))),
        float(tx.get("velocity_1h", 0)),
        float(tx.get("velocity_24h", 0)),
        float(bool(tx.get("odd_hour", False))),
        math.log1p(sender_age),
        math.log(ratio),
        float(tx.get("prior_fraud_reports", 0)),
    ]
