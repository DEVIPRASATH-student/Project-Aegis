"""
Project Aegis -- Pydantic Schemas

Request and response schemas for the API layer.
These define the contract between frontend and backend.
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


# ── Transfer Schemas ──────────────────────────────────────────────

class TransferRequest(BaseModel):
    """Incoming transfer request from the victim application."""
    sender: str = Field(..., min_length=1, max_length=128, description="Sender account identifier")
    receiver: str = Field(..., min_length=1, max_length=128, description="Receiver account identifier")
    amount: float = Field(..., gt=0, description="Transaction amount in INR")
    screen_share: bool = Field(default=False, description="Whether screen-sharing is detected/simulated")
    note: Optional[str] = Field(default=None, max_length=256, description="Optional transaction note")


class TransferResponse(BaseModel):
    """
    Response returned to the victim application.

    Note: For HIGH-RISK transactions, the victim-facing fields
    (display_status, message) deliberately show success to implement
    asymmetric deception. The actual backend status may differ.
    """
    transaction_id: str
    display_status: str  # What the victim UI should show (always SUCCESS-like)
    message: str
    amount: float
    receiver: str
    timestamp: str

    # Backend truth (not shown to victim, used by co-signer)
    actual_status: str
    risk_score: Optional[float] = None
    cpst_token: Optional[str] = None


# ── Escrow / Co-Signer Schemas ────────────────────────────────────

class EscrowResolveRequest(BaseModel):
    """Co-signer's decision on an escrowed transaction."""
    transaction_id: str = Field(..., description="The transaction to resolve")
    decision: str = Field(..., pattern="^(REVERSED|SUCCESS)$", description="REVERSED or SUCCESS")
    resolved_by: Optional[str] = Field(default="co-signer", description="Who resolved the transaction")


class EscrowResolveResponse(BaseModel):
    """Confirmation of escrow resolution."""
    transaction_id: str
    previous_status: str
    new_status: str
    message: str


class TransactionStatusResponse(BaseModel):
    """Transaction status for polling by victim or co-signer."""
    transaction_id: str
    sender: str
    receiver: str
    amount: float
    status: str
    risk_score: Optional[float] = None
    risk_level: Optional[str] = None
    cpst_token: Optional[str] = None
    screen_share: bool = False
    hops_to_risk: Optional[int] = None
    risk_factors: Optional[str] = None
    created_at: Optional[str] = None
    resolved_at: Optional[str] = None
    resolved_by: Optional[str] = None


class EscrowListResponse(BaseModel):
    """List of escrowed transactions for the co-signer dashboard."""
    transactions: List[TransactionStatusResponse]
    total_protected_amount: float
    active_alerts: int


# ── Health / Utility Schemas ──────────────────────────────────────

class HealthResponse(BaseModel):
    """API health check response."""
    status: str = "operational"
    service: str = "Project Aegis Transaction Security Layer"
    version: str = "1.0.0-prototype"
    database: str = "connected"
    graph_engine: str = "loaded"
    ml_model: str = "loaded"
