# 🚀 ORION-Q: Institutional Quantitative Market OS

**ORION-Q** is an end-to-end, high-frequency, institutional-grade quantitative trading platform and machine learning decision support engine. Designed for global and Indian equities (NYSE / NASDAQ / NSE), ORION-Q combines walk-forward cross-validation, probability calibration via Platt scaling, split conformal prediction intervals, and explainable AI (SHAP) into a real-time terminal UI.

---

## 🏗️ Architecture & Core Components

```
                ┌──────────────────────────────────────────────┐
                │          Next.js 14 Terminal UI             │
                │     (Zerodha Kite Dark/High-Contrast)        │
                └──────────────────────┬───────────────────────┘
                                       │ WebSocket / REST (1.0s)
                ┌──────────────────────▼───────────────────────┐
                │          FastAPI Microservice Core           │
                └───────┬──────────────────────────────┬───────┘
                        │                              │
         ┌──────────────▼──────────────┐ ┌─────────────▼──────────────┐
         │     Model Parliament        │ │  Conformal & Calibration   │
         │ (LR + RF + ET + GB + Stack) │ │ (Platt Scaling + 95% ISCP)  │
         └─────────────────────────────┘ └────────────────────────────┘
```

### 🧠 1. Institutional Machine Learning Engine (Model Parliament)
- **5-Model Parliament**: Logistic Regression, Random Forest, Extra Trees, Gradient Boosting, and Stacking Meta-Learner.
- **Leakage-Safe Preprocessing**: Chronological split with feature normalization.
- **Platt Scaling**: Calibrates raw model probabilities to produce true empirical confidence.
- **95% Split Conformal Prediction**: Computes distribution-free non-parametric prediction intervals.
- **Explainable AI (TreeSHAP)**: Identifies top positive and negative market feature drivers.

### ⚡ 2. Real-Time Data Fabric & Services
- **1.0s WebSocket Tick Streaming**: Real-time price actions, market session routing, and connection latency monitoring.
- **Parallel Institutional Scanner**: Multi-threaded signal discovery powered by `ThreadPoolExecutor` with 30s TTL in-memory caching.
- **Event-Driven Backtesting Engine**: Realistic strategy backtests incorporating 5.0 bps commission, 2.0 bps slippage, and drawdown metrics.
- **Zero-Hallucination Quantitative Copilot**: Retrieves verified factual evidence and model metrics before answering queries.

---

## 🛠️ Project Structure

```
.
├── backend/                  # FastAPI Core Backend Service
│   ├── app/
│   │   ├── api/v1/           # REST Routers (Stocks, Predictions, Scanner, Backtest, Copilot)
│   │   ├── core/             # Configuration, Logging, Currency Mappings
│   │   ├── data/             # Market Data Ingestion & Quality Gates
│   │   ├── features/         # Feature Engineering Pipeline (156+ Technical Signals)
│   │   ├── ml/               # Model Parliament, Preprocessing & Evaluation Suite
│   │   ├── services/         # Prediction, Signal, Regime, Stability & Copilot Engines
│   │   └── websocket/        # Real-time WebSocket Event Bus & Connection Manager
│   └── main.py
├── frontend/                 # Next.js 14 Production Terminal
│   ├── src/
│   │   ├── app/              # App Router, Layouts & Global CSS
│   │   ├── components/       # Zerodha-style Terminal Components & Visualizers
│   │   ├── lib/              # API Client & WebSocket Handlers
│   │   └── types/            # TypeScript Schemas & Interfaces
└── README.md
```

---

## 🚦 Quick Start Guide

### Prerequisites
- Python 3.10+
- Node.js 18+

### 1. Launch FastAPI Core Backend
```bash
# Install Python dependencies
pip install fastapi uvicorn pandas numpy scikit-learn yfinance pydantic shap

# Run Backend Server
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

### 2. Launch Next.js Production Terminal
```bash
cd frontend

# Install Node dependencies
npm install

# Run Production Build & Start Server
npm run build
npm run start
```
Access the terminal in your browser at: **`http://localhost:3000`**

---

## 👥 Authors & Academic Credits
- **Prajan Sanjay K**
- **Kishore S**
