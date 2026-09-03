"""
Project Aegis -- Database Seed Script

Seeds the demo database with deterministic test data
to ensure reproducible hackathon demonstrations.

Run from the backend directory:
    python scripts/seed_db.py
"""

import sys
import os

# Add backend root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.database import create_tables, SessionLocal
from models.db_models import Transaction
from services.graph_engine import get_graph_engine


def main():
    print("=" * 60)
    print("  Project Aegis -- Database Seeding")
    print("=" * 60)
    print()

    # Create tables
    create_tables()
    print("Database tables created.")

    # Clear existing data
    db = SessionLocal()
    count = db.query(Transaction).delete()
    db.commit()
    if count > 0:
        print(f"Cleared {count} existing transactions.")

    # Verify graph engine
    engine = get_graph_engine()
    stats = engine.get_network_stats()
    print(f"\nGraph engine loaded:")
    print(f"  Total nodes:         {stats['total_nodes']}")
    print(f"  Total edges:         {stats['total_edges']}")
    print(f"  Known scammers:      {stats['known_scammers']}")
    print(f"  Known mules:         {stats['known_mules']}")
    print(f"  Legitimate accounts: {stats['legitimate_accounts']}")
    print(f"  Merchants:           {stats['merchants']}")

    # Verify demo scenario
    print("\nVerifying demo scenario...")
    risk_info = engine.calculate_receiver_risk("B")
    print(f"  Receiver B risk assessment:")
    print(f"    Graph risk score:    {risk_info['graph_risk_score']}")
    print(f"    Graph risk level:    {risk_info['graph_risk_level']}")
    print(f"    Hops to scammer:     {risk_info['hops_to_known_risk']}")
    print(f"    Nearest flagged:     {risk_info['nearest_flagged_account']}")
    print(f"    Path:                {' -> '.join(risk_info['path_to_risk'])}")
    print(f"    In fraud community:  {risk_info['in_fraud_community']}")
    print(f"    PageRank:            {risk_info['pagerank']}")

    # Verify a legitimate receiver
    print(f"\n  Receiver M01 (merchant) risk assessment:")
    risk_info_legit = engine.calculate_receiver_risk("M01")
    print(f"    Graph risk score:    {risk_info_legit['graph_risk_score']}")
    print(f"    Graph risk level:    {risk_info_legit['graph_risk_level']}")
    print(f"    Hops to scammer:     {risk_info_legit['hops_to_known_risk']}")

    db.close()
    print("\nSeed complete. Database is ready for demo.")


if __name__ == "__main__":
    main()
