"""
Project Aegis -- Risk Scorer Service

Combines graph engine analysis and ML model prediction into a
unified risk assessment for each transaction.

This is the central decision engine that determines whether a
transaction should proceed normally (SUCCESS) or be placed into
escrow (ESCROW_LIEN).
"""

import uuid
import json
from typing import Dict, Any
from services.graph_engine import get_graph_engine
from services.ml_model import get_ml_predictor


# Amount normalization constants (INR)
# Based on typical Indian transaction ranges for the prototype
AMOUNT_LOW = 1000       # Below this is very normal
AMOUNT_HIGH = 100000    # Above this is unusually high
TYPICAL_AMOUNT = 5000   # Average transaction for the demo user


def _normalize_amount(amount: float) -> float:
    """Normalize transaction amount to 0-1 range."""
    if amount <= 0:
        return 0.0
    if amount >= AMOUNT_HIGH:
        return 1.0
    return min(amount / AMOUNT_HIGH, 1.0)


def _calculate_amount_deviation(amount: float) -> float:
    """
    Calculate how far the amount deviates from the user's typical pattern.
    For the prototype, we use a fixed typical amount.
    """
    if amount <= 0:
        return 0.0
    deviation = abs(amount - TYPICAL_AMOUNT) / TYPICAL_AMOUNT
    return min(deviation, 1.0)


def generate_cpst_token() -> str:
    """
    Generate a Cryptographic Provisional Settlement Token (CPST).

    This is a prototype concept token, not a real banking
    settlement mechanism. The format is designed to look
    like a plausible financial reference.
    """
    short_id = uuid.uuid4().hex[:6].upper()
    return f"CPST-AEGIS-{short_id}"


def generate_transaction_id() -> str:
    """Generate a unique transaction identifier."""
    short_id = uuid.uuid4().hex[:8].upper()
    return f"AEG-{short_id}"


def assess_transaction_risk(
    sender: str,
    receiver: str,
    amount: float,
    screen_share: bool = False,
    is_new_receiver: bool = True,
) -> Dict[str, Any]:
    """
    Full risk assessment for a transaction.

    Combines:
    1. Graph engine analysis (proximity, centrality, community)
    2. ML model prediction (GradientBoosting on 9 features)
    3. Rule-based explainability breakdown

    Args:
        sender: Sender account identifier
        receiver: Receiver account identifier
        amount: Transaction amount in INR
        screen_share: Whether screen-sharing is detected
        is_new_receiver: Whether this is a first transaction to this receiver

    Returns:
        Complete risk assessment with score, level, and breakdown.
    """
    graph_engine = get_graph_engine()
    ml_predictor = get_ml_predictor()

    # ── Step 1: Graph Analysis ────────────────────────────────────
    graph_result = graph_engine.calculate_receiver_risk(receiver)

    # ── Step 2: Prepare ML Feature Vector ─────────────────────────
    features = {
        "hops_to_nearest_scammer": graph_result["hops_to_known_risk"],
        "pagerank_score": graph_result["pagerank"],
        "degree_centrality": graph_result["degree_centrality"],
        "receiver_in_fraud_community": 1.0 if graph_result["in_fraud_community"] else 0.0,
        "transaction_amount_normalized": _normalize_amount(amount),
        "screen_share_active": 1.0 if screen_share else 0.0,
        "is_new_receiver": 1.0 if is_new_receiver else 0.0,
        "amount_deviation": _calculate_amount_deviation(amount),
        "clustering_coefficient": graph_result["clustering_coefficient"],
    }

    # ── Step 3: ML Prediction ─────────────────────────────────────
    ml_result = ml_predictor.predict_risk(features)

    # ── Step 4: Combine Scores ────────────────────────────────────
    # Use ML score as primary, graph score as secondary validation
    ml_score = ml_result["ml_risk_score"]
    graph_score = graph_result["graph_risk_score"]

    # Weighted combination: 60% ML, 40% graph
    combined_score = (ml_score * 0.60) + (graph_score * 0.40)

    # Apply contextual boosters
    if screen_share and combined_score > 30:
        combined_score = min(combined_score + 10, 100)

    if amount >= 25000 and combined_score > 30:
        combined_score = min(combined_score + 5, 100)

    combined_score = round(min(max(combined_score, 0), 100), 1)

    # ── Step 5: Determine Risk Level ──────────────────────────────
    if combined_score >= 70:
        risk_level = "HIGH"
        status = "ESCROW_LIEN"
    elif combined_score >= 40:
        risk_level = "MEDIUM"
        # Medium risk: escrow if screen-share is active, otherwise pass
        if screen_share:
            status = "ESCROW_LIEN"
        else:
            status = "SUCCESS"
    else:
        risk_level = "LOW"
        status = "SUCCESS"

    # ── Step 6: Build Risk Factors Breakdown ──────────────────────
    risk_factors = []

    hops = graph_result["hops_to_known_risk"]
    if hops != -1 and hops <= 3:
        risk_factors.append(
            f"Receiver is {hops} hop{'s' if hops > 1 else ''} from a known high-risk account"
        )
    elif hops != -1 and hops <= 5:
        risk_factors.append(
            f"Receiver is {hops} hops from a flagged account"
        )

    if screen_share:
        risk_factors.append("Active screen-sharing detected")

    if amount >= 25000:
        risk_factors.append(f"High transaction amount: INR {amount:,.0f}")

    if graph_result["in_fraud_community"]:
        risk_factors.append("Receiver belongs to a network cluster containing flagged accounts")

    if graph_result["pagerank"] > 0.02:
        risk_factors.append("Receiver has elevated network centrality")

    if is_new_receiver:
        risk_factors.append("First transaction to this receiver")

    if not risk_factors:
        risk_factors.append("No significant risk indicators detected")

    # ── Step 7: Generate Tokens ───────────────────────────────────
    transaction_id = generate_transaction_id()
    cpst_token = generate_cpst_token() if status == "ESCROW_LIEN" else None

    return {
        "transaction_id": transaction_id,
        "risk_score": combined_score,
        "risk_level": risk_level,
        "recommended_status": status,
        "cpst_token": cpst_token,
        "risk_factors": risk_factors,
        "risk_factors_json": json.dumps(risk_factors),
        "hops_to_risk": hops,

        # Detailed breakdown (for co-signer dashboard)
        "breakdown": {
            "ml_score": ml_result["ml_risk_score"],
            "ml_prediction": ml_result["ml_prediction"],
            "ml_confidence": ml_result["ml_confidence"],
            "ml_model_type": ml_result["model_type"],
            "graph_score": graph_result["graph_risk_score"],
            "graph_risk_level": graph_result["graph_risk_level"],
            "hops_to_known_risk": hops,
            "nearest_flagged": graph_result["nearest_flagged_account"],
            "in_fraud_community": graph_result["in_fraud_community"],
            "pagerank": graph_result["pagerank"],
            "degree_centrality": graph_result["degree_centrality"],
            "clustering_coefficient": graph_result["clustering_coefficient"],
            "screen_share": screen_share,
            "amount_normalized": _normalize_amount(amount),
            "amount_deviation": _calculate_amount_deviation(amount),
        },
    }
