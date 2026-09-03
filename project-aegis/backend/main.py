"""
Project Aegis -- FastAPI Application Entry Point

Transaction Security Layer for APP Fraud Protection.
This is the main backend application that serves the REST API,
initializes the database, and loads the ML model on startup.
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

from core.database import create_tables
from api.routes_transfer import router as transfer_router
from api.routes_cosigner import router as cosigner_router
from models.schemas import HealthResponse
from services.graph_engine import get_graph_engine
from services.ml_model import get_ml_predictor

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-7s | %(name)s | %(message)s",
)
logger = logging.getLogger("aegis")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown lifecycle."""
    # Startup
    logger.info("Initializing Project Aegis Transaction Security Layer...")

    # Create database tables
    create_tables()
    logger.info("Database tables initialized.")

    # Pre-load graph engine
    engine = get_graph_engine()
    stats = engine.get_network_stats()
    logger.info(
        f"Graph engine loaded: {stats['total_nodes']} nodes, "
        f"{stats['total_edges']} edges, "
        f"{stats['known_scammers']} known scammers, "
        f"{stats['known_mules']} known mules"
    )

    # Pre-load ML model
    predictor = get_ml_predictor()
    if predictor.is_ml_available:
        logger.info("ML fraud detection model loaded (GradientBoosting).")
    else:
        logger.warning("ML model not available. Using rule-based scoring.")

    logger.info("Project Aegis is operational.")
    yield
    # Shutdown
    logger.info("Project Aegis shutting down.")


# Create FastAPI application
app = FastAPI(
    title="Project Aegis",
    description=(
        "Transaction Security Layer for Authorized Push Payment (APP) Fraud Protection. "
        "Evaluates transactions using graph-based fraud intelligence and machine learning "
        "to protect vulnerable users from social engineering attacks."
    ),
    version="1.0.0-prototype",
    lifespan=lifespan,
)

# CORS configuration
cors_origins = os.getenv("CORS_ORIGINS", "http://localhost:5173").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register API routers
app.include_router(transfer_router)
app.include_router(cosigner_router)


@app.get("/health", response_model=HealthResponse, tags=["system"])
def health_check():
    """API health check endpoint."""
    engine = get_graph_engine()
    predictor = get_ml_predictor()
    return HealthResponse(
        status="operational",
        service="Project Aegis Transaction Security Layer",
        version="1.0.0-prototype",
        database="connected",
        graph_engine=f"loaded ({engine.get_network_stats()['total_nodes']} nodes)",
        ml_model="loaded (GradientBoosting)" if predictor.is_ml_available else "rule-based fallback",
    )


if __name__ == "__main__":
    import uvicorn
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    uvicorn.run("main:app", host=host, port=port, reload=True)
