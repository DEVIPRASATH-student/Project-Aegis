from __future__ import annotations

from .graph_engine import graph_engine
from ..ml.model import predict_fraud_probability

def score_transaction(payload: dict) -> dict:
    """
    Hybrid Aegis score:
      - ML estimates transaction fraud probability.
      - Network graph provides an explainable structural signal.
      - Demo telemetry is already a model feature.

    The final score is intentionally conservative: ML is the main signal,
    while graph proximity provides an explicit containment boost.
    """
    graph_result = graph_engine.evaluate_receiver(payload["receiver"])
    ml_payload = {
        **payload,
        "graph_hops": graph_result.get("hops", 99),
    }

    probability = predict_fraud_probability(ml_payload)
    graph_score = 100 if graph_result.get("hops", 99) <= 3 else 0

    # 75% learned probability + 25% explainable graph signal.
    final_score = round(75 * probability + 0.25 * graph_score)

    if final_score >= 75:
        level = "HIGH"
    elif final_score >= 45:
        level = "MEDIUM"
    else:
        level = "LOW"

    return {
        "risk_score": final_score,
        "risk_level": level,
        "ml_probability": round(probability, 4),
        "graph_score": graph_score,
        "graph": graph_result,
    }
