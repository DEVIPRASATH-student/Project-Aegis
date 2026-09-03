"""
Project Aegis -- Transfer API Routes

Handles the victim-side transaction flow:
  POST /api/v1/transfer       -- Submit a new transaction
  GET  /api/v1/transfer/{id}  -- Poll transaction status (for victim UI updates)
"""

import datetime
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.db_models import Transaction, TransactionStatus
from models.schemas import TransferRequest, TransferResponse, TransactionStatusResponse
from services.risk_scorer import assess_transaction_risk

router = APIRouter(prefix="/api/v1", tags=["transfer"])


@router.post("/transfer", response_model=TransferResponse)
def create_transfer(request: TransferRequest, db: Session = Depends(get_db)):
    """
    Submit a new transaction for risk assessment.

    The backend evaluates the transaction using the graph engine
    and ML model, then either:
      - Marks it SUCCESS (low risk) and returns success
      - Marks it ESCROW_LIEN (high risk) and returns a deceptive
        success message to the victim while protecting the funds

    The victim-facing response always appears successful.
    """
    # Validate amount
    if request.amount <= 0:
        raise HTTPException(status_code=400, detail="Amount must be greater than zero.")
    if request.amount > 10000000:
        raise HTTPException(status_code=400, detail="Amount exceeds maximum allowed value.")

    # Run risk assessment
    risk_result = assess_transaction_risk(
        sender=request.sender,
        receiver=request.receiver,
        amount=request.amount,
        screen_share=request.screen_share,
        is_new_receiver=True,  # For prototype, treat all as new
    )

    # Create database record
    transaction = Transaction(
        transaction_id=risk_result["transaction_id"],
        sender=request.sender,
        receiver=request.receiver,
        amount=request.amount,
        risk_score=risk_result["risk_score"],
        risk_level=risk_result["risk_level"],
        status=risk_result["recommended_status"],
        cpst_token=risk_result["cpst_token"],
        screen_share=request.screen_share,
        hops_to_risk=risk_result["hops_to_risk"],
        risk_factors=risk_result["risk_factors_json"],
        created_at=datetime.datetime.utcnow(),
    )

    db.add(transaction)
    db.commit()
    db.refresh(transaction)

    # Build response -- victim always sees "success"
    now = datetime.datetime.utcnow().isoformat() + "Z"

    if risk_result["recommended_status"] == TransactionStatus.ESCROW_LIEN.value:
        # High risk: show deceptive success to victim
        return TransferResponse(
            transaction_id=risk_result["transaction_id"],
            display_status="SUCCESS",
            message="Payment Successful",
            amount=request.amount,
            receiver=request.receiver,
            timestamp=now,
            actual_status=TransactionStatus.ESCROW_LIEN.value,
            risk_score=risk_result["risk_score"],
            cpst_token=risk_result["cpst_token"],
        )
    else:
        # Low risk: genuine success
        return TransferResponse(
            transaction_id=risk_result["transaction_id"],
            display_status="SUCCESS",
            message="Payment Successful",
            amount=request.amount,
            receiver=request.receiver,
            timestamp=now,
            actual_status=TransactionStatus.SUCCESS.value,
            risk_score=risk_result["risk_score"],
            cpst_token=None,
        )


@router.get("/transfer/{transaction_id}", response_model=TransactionStatusResponse)
def get_transaction_status(transaction_id: str, db: Session = Depends(get_db)):
    """
    Poll transaction status.

    Used by the victim UI to detect when a co-signer has
    reversed a transaction (ESCROW_LIEN -> REVERSED).
    """
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    return TransactionStatusResponse(
        transaction_id=transaction.transaction_id,
        sender=transaction.sender,
        receiver=transaction.receiver,
        amount=transaction.amount,
        status=transaction.status,
        risk_score=transaction.risk_score,
        risk_level=transaction.risk_level,
        cpst_token=transaction.cpst_token,
        screen_share=transaction.screen_share,
        hops_to_risk=transaction.hops_to_risk,
        risk_factors=transaction.risk_factors,
        created_at=transaction.created_at.isoformat() if transaction.created_at else None,
        resolved_at=transaction.resolved_at.isoformat() if transaction.resolved_at else None,
        resolved_by=transaction.resolved_by,
    )
