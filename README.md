# Project Aegis 🛡️

> **Asymmetric Deception & Escrow Lien Architecture for Real-Time Fraud Interception**

Project Aegis is a fraud prevention and victim-protection framework designed to intercept high-risk, socially engineered transfers (e.g., screen-share scams, urgent impersonation, mule accounts) **without alerting the fraudster**.

---

## 💡 The Core Problem: The Coercion Dilemma

In modern digital payment scams (such as remote-access support fraud, fake police scams, or digital arrest scams), fraudsters actively coerce victims over phone calls or remote-desktop screen-sharing sessions (AnyDesk, TeamViewer, Zoom). 

When a banking app simply **blocks** a payment:
- The fraudster becomes aggressive or instructs the victim to retry through another channel or bank.
- The victim remains trapped in the coercive environment.

### 🛡️ The Aegis Solution: Asymmetric Deception & Escrow Lien

1. **Simultaneous Risk Scoring**: When a transaction is submitted, the hybrid ML model (Isolation Forest + Behavioral Heuristics) and the **NetworkX Graph Engine** evaluate:
   - Account behavioral anomalies & transaction velocity
   - Telemetry signals (active screen sharing, clipboard manipulation, call status)
   - Graph network distance to known mule rings & bad-actor clusters
2. **Escrow Interception**: If high risk is detected ($Score \ge 70$):
   - The funds are not routed to the scammer. They are placed into an immutable **Escrow Lien** accompanied by a cryptographically verifiable **CPST** (Conditional Payment State Token).
   - **Victim's Screen (Controlled Deception)**: The victim sees a realistic **"Payment Successful"** confirmation. To the scammer watching the screen, the transaction appears complete.
3. **Co-Signer Protection Flow**:
   - The trusted co-signer / family contact is immediately alerted via their dedicated dashboard (`/dashboard`).
   - The co-signer can review risk factors (e.g., "Active screen share detected", "Target account 3 hops from known scam syndicate").
   - With a single click, the co-signer can **Reverse Transaction** to return the funds safely, or **Authorize** if legitimate.
4. **Auto-Synchronization**:
   - Once safely detached or reversed, the victim's application cleanly transitions to reflect the cancelled/reversed transfer.

---

## 🏛️ System Architecture

```
                 +-----------------------+
                 |  Victim Client (Web)  |
                 |  - Transfer Form      |
                 |  - Telemetry Sensor   |
                 +-----------+-----------+
                             |
                   POST /api/transfer/send
                             |
                             v
                 +-----------------------+
                 |   FastAPI Backend     |
                 |  - Risk Scoring       |
                 |  - Graph Analysis     |
                 |  - Escrow Lien Engine |
                 +-----+-----------+-----+
                       |           |
            High Risk? |           | Co-Signer Actions
                       v           v
     +-------------------+       +-----------------------+
     |   Escrow Lien     | <---> |  Co-Signer Dashboard  |
     |   (CPST Token)    |       |  - Alerts & Risk HUD  |
     +-------------------+       |  - Reversal / Release |
                                 +-----------------------+
```

---

## 🚀 Tech Stack

- **Backend**: Python 3.10+, FastAPI, SQLAlchemy, SQLite, Pydantic
- **Detection Engines**:
  - **Graph Engine**: NetworkX graph analysis (hop distance to fraud nodes, mule community clustering, PageRank centrality)
  - **ML Engine**: Scikit-Learn Isolation Forest & RandomForest anomaly detection
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide Icons, Axios

---

## 📁 Repository Structure

```
project-aegis/
├── backend/
│   ├── api/
│   │   ├── routes_transfer.py      # Transfer initiation, status polling, telemetry
│   │   └── routes_cosigner.py      # Co-signer alerts, escrow approvals, reversals
│   ├── core/
│   │   └── database.py             # Database engine & session setup
│   ├── models/
│   │   ├── db_models.py            # SQLAlchemy models (User, Transaction, EscrowLien, Alert)
│   │   ├── schemas.py              # Pydantic schemas & DTOs
│   │   └── trained/                # Serialized ML model weights
│   ├── scripts/
│   │   ├── seed_db.py              # Demo database seeder
│   │   └── train_model.py          # ML anomaly model training script
│   ├── services/
│   │   ├── graph_engine.py         # NetworkX fraud ring graph analyzer & alias resolution
│   │   ├── ml_model.py             # Scikit-learn transaction model
│   │   └── risk_scorer.py          # Unified hybrid risk scoring engine
│   ├── main.py                     # FastAPI entrypoint
│   ├── requirements.txt            # Python dependencies
│   └── .env.example                # Sample environment configuration
├── frontend/
│   ├── src/
│   │   ├── api/client.js           # API client
│   │   ├── components/             # Reusable UI components (TransferForm, ProvisionalReceipt, EscrowCard)
│   │   ├── hooks/useTelemetry.js   # Browser telemetry & screen-share detector hook
│   │   ├── pages/                  # VictimDashboard (/transfer) & CoSignerAlerts (/dashboard)
│   │   ├── App.jsx                 # Route configurations
│   │   └── main.jsx                # Application root
│   ├── package.json
│   ├── vite.config.js
│   └── tailwind.config.js
└── .gitignore
```

---

## 🛠️ Quickstart & Local Setup

### 1. Backend Setup

```bash
cd project-aegis/backend

# Create and activate virtual environment (optional)
python -m venv venv
source venv/bin/activate    # On Windows: .\venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# (Optional) Seed the database with demo accounts and test network
python scripts/seed_db.py

# Run FastAPI server
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Backend API will be live at `http://localhost:8000` (Swagger docs at `http://localhost:8000/docs`).

### 2. Frontend Setup

```bash
cd project-aegis/frontend

# Install dependencies
npm install

# Start Vite development server
npm run dev
```

Frontend application will be accessible at:
- **Victim Transfer Interface**: `http://localhost:5173/transfer`
- **Co-Signer Emergency Dashboard**: `http://localhost:5173/dashboard`

---

## 🧪 Testing the Scenario Flow

1. Open `http://localhost:5173/transfer`.
2. Notice the target account `XXXX4821` (connected to simulated mule ring in `graph_engine.py`).
3. Toggle **"Simulate Screen Sharing Detected"** ON, set amount to `50000`, and submit.
4. The page will render **"Payment Successful"** to deceive the fraudster.
5. In another tab, open `http://localhost:5173/dashboard`:
   - An alert appears with score **80.3/100 (HIGH RISK)** and ₹50,000 in Protected Funds.
   - Click **"Reverse Transaction"**.
6. Switch back to the `/transfer` tab: the transfer status auto-updates to **"Transfer Cancelled"** with trusted contact reversal feedback.
