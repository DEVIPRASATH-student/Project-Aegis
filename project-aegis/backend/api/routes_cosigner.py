"""
Project Aegis -- Co-Signer API Routes

Handles the trusted co-signer's dashboard operations:
  GET  /api/v1/escrow/{user_id}   -- List all escrowed transactions
  POST /api/v1/escrow/resolve     -- Approve or reverse a transaction
  POST /api/v1/demo/reset         -- Reset demo state (dev only)
"""

import datetime
import json
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from core.database import get_db
from models.db_models import Transaction, TransactionStatus
from models.schemas import (
    EscrowResolveRequest,
    EscrowResolveResponse,
    TransactionStatusResponse,
    EscrowListResponse,
)

router = APIRouter(prefix="/api/v1", tags=["cosigner"])


@router.get("/escrow/{user_id}", response_model=EscrowListResponse)
def get_escrowed_transactions(user_id: str, db: Session = Depends(get_db)):
    """
    Retrieve all transactions currently in ESCROW_LIEN status
    where the given user is the sender.

    The co-signer dashboard polls this endpoint every 2-3 seconds
    to detect new alerts.
    """
    transactions = db.query(Transaction).filter(
        Transaction.status == TransactionStatus.ESCROW_LIEN.value,
    ).order_by(Transaction.created_at.desc()).all()

    tx_list = []
    total_protected = 0.0

    for tx in transactions:
        total_protected += tx.amount
        tx_list.append(
            TransactionStatusResponse(
                transaction_id=tx.transaction_id,
                sender=tx.sender,
                receiver=tx.receiver,
                amount=tx.amount,
                status=tx.status,
                risk_score=tx.risk_score,
                risk_level=tx.risk_level,
                cpst_token=tx.cpst_token,
                screen_share=tx.screen_share,
                hops_to_risk=tx.hops_to_risk,
                risk_factors=tx.risk_factors,
                created_at=tx.created_at.isoformat() if tx.created_at else None,
                resolved_at=tx.resolved_at.isoformat() if tx.resolved_at else None,
                resolved_by=tx.resolved_by,
            )
        )

    return EscrowListResponse(
        transactions=tx_list,
        total_protected_amount=total_protected,
        active_alerts=len(tx_list),
    )


@router.post("/escrow/resolve", response_model=EscrowResolveResponse)
def resolve_escrow(request: EscrowResolveRequest, db: Session = Depends(get_db)):
    """
    Resolve an escrowed transaction.

    The co-signer decides to either:
      - REVERSED: Cancel the transaction (funds remain protected)
      - SUCCESS: Approve the transaction (funds released)

    Only transactions currently in ESCROW_LIEN can be resolved.
    """
    transaction = db.query(Transaction).filter(
        Transaction.transaction_id == request.transaction_id
    ).first()

    if not transaction:
        raise HTTPException(status_code=404, detail="Transaction not found.")

    if transaction.status != TransactionStatus.ESCROW_LIEN.value:
        raise HTTPException(
            status_code=400,
            detail=f"Transaction is in '{transaction.status}' state and cannot be resolved. "
                   f"Only ESCROW_LIEN transactions can be resolved."
        )

    if request.decision not in (TransactionStatus.REVERSED.value, TransactionStatus.SUCCESS.value):
        raise HTTPException(
            status_code=400,
            detail="Decision must be either 'REVERSED' or 'SUCCESS'."
        )

    previous_status = transaction.status
    transaction.status = request.decision
    transaction.resolved_at = datetime.datetime.utcnow()
    transaction.resolved_by = request.resolved_by or "co-signer"

    db.commit()
    db.refresh(transaction)

    if request.decision == TransactionStatus.REVERSED.value:
        message = "Transaction has been reversed. Funds remain protected."
    else:
        message = "Transaction has been approved. Funds released."

    return EscrowResolveResponse(
        transaction_id=transaction.transaction_id,
        previous_status=previous_status,
        new_status=transaction.status,
        message=message,
    )


@router.get("/transactions/{user_id}")
def get_all_transactions(user_id: str, db: Session = Depends(get_db)):
    """
    Get all transactions for a user (all statuses).
    Used by the co-signer dashboard for the full history view.
    """
    transactions = db.query(Transaction).filter(
        Transaction.sender == user_id
    ).order_by(Transaction.created_at.desc()).all()

    return {
        "transactions": [
            {
                "transaction_id": tx.transaction_id,
                "sender": tx.sender,
                "receiver": tx.receiver,
                "amount": tx.amount,
                "status": tx.status,
                "risk_score": tx.risk_score,
                "risk_level": tx.risk_level,
                "created_at": tx.created_at.isoformat() if tx.created_at else None,
                "resolved_at": tx.resolved_at.isoformat() if tx.resolved_at else None,
            }
            for tx in transactions
        ],
        "total": len(transactions),
    }


@router.post("/demo/reset")
def reset_demo(db: Session = Depends(get_db)):
    """
    Reset all demo transaction data.
    This is a development-only endpoint for hackathon demonstrations.
    Clears all transactions from the ledger.
    """
    count = db.query(Transaction).delete()
    db.commit()
    return {
        "message": "Demo state reset successfully.",
        "transactions_cleared": count,
    }
