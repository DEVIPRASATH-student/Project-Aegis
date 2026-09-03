"""
Project Aegis -- Model Training Script

Generates synthetic fraud transaction data, trains a GradientBoosting
classifier, evaluates it, and saves the model to disk.

Run this script before starting the backend to pre-train the model:
    python -m scripts.train_model

Or from the backend directory:
    python scripts/train_model.py
"""

import sys
import os

# Add backend root to path so imports work
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.ml_model import train_model, generate_synthetic_training_data


def main():
    print("=" * 60)
    print("  Project Aegis -- Fraud Detection Model Training")
    print("=" * 60)
    print()

    print("Generating synthetic training data (5000 transactions)...")
    df = generate_synthetic_training_data(n_samples=5000)
    print(f"  Total samples: {len(df)}")
    print(f"  Legitimate: {len(df[df['is_fraud'] == 0])} ({len(df[df['is_fraud'] == 0])/len(df)*100:.1f}%)")
    print(f"  Fraudulent: {len(df[df['is_fraud'] == 1])} ({len(df[df['is_fraud'] == 1])/len(df)*100:.1f}%)")
    print()

    print("Training GradientBoosting classifier...")
    results = train_model(n_samples=5000)

    if "error" in results:
        print(f"ERROR: {results['error']}")
        sys.exit(1)

    print()
    print("-" * 40)
    print("  Model Performance")
    print("-" * 40)
    print(f"  Accuracy:          {results['accuracy']:.4f}")
    print(f"  Precision (fraud): {results['precision_fraud']:.4f}")
    print(f"  Recall (fraud):    {results['recall_fraud']:.4f}")
    print(f"  F1-Score (fraud):  {results['f1_fraud']:.4f}")
    print(f"  Training samples:  {results['training_samples']}")
    print(f"  Test samples:      {results['test_samples']}")
    print()

    print("-" * 40)
    print("  Feature Importances (Ranked)")
    print("-" * 40)
    for i, (feature, importance) in enumerate(results["feature_importances"].items(), 1):
        bar = "#" * int(importance * 50)
        print(f"  {i}. {feature:<35} {importance:.4f}  {bar}")
    print()

    print(f"Model saved to: {results['model_path']}")
    print()
    print("Training complete.")


if __name__ == "__main__":
    main()
