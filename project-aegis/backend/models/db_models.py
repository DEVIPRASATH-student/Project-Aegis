"""
Project Aegis -- Database Models

SQLAlchemy ORM model for the transactions ledger.
Stores all transaction state including escrow/lien status.
"""

import datetime
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Enum
from core.database import Base
import enum


class TransactionStatus(str, enum.Enum):
    """Possible states for a transaction in the Aegis ledger."""
    PENDING = "PENDING"
    SUCCESS = "SUCCESS"
    ESCROW_LIEN = "ESCROW_LIEN"
    REVERSED = "REVERSED"


class Transaction(Base):
    """
    Transaction record in the Aegis prototype ledger.

    This represents a simulated payment transaction with its
    associated risk assessment and escrow state.
    """
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    transaction_id = Column(String(64), unique=True, index=True, nullable=False)
    sender = Column(String(128), nullable=False)
    receiver = Column(String(128), nullable=False)
    amount = Column(Float, nullable=False)
    risk_score = Column(Float, nullable=True)
    risk_level = Column(String(16), nullable=True)
    status = Column(
        String(16),
        default=TransactionStatus.PENDING.value,
        nullable=False,
    )
    cpst_token = Column(String(128), nullable=True)
    screen_share = Column(Boolean, default=False)
    hops_to_risk = Column(Integer, nullable=True)
    risk_factors = Column(String(1024), nullable=True)  # JSON string of risk breakdown
    created_at = Column(DateTime, default=datetime.datetime.utcnow)
    resolved_at = Column(DateTime, nullable=True)
    resolved_by = Column(String(128), nullable=True)
