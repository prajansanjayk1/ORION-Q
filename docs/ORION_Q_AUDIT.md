# ORION-Q REPOSITORY AUDIT REPORT & DATA FABRIC ARCHITECTURE

**Date**: 2026-08-12  
**Target Platform**: ORION-Q Full-Stack Institutional Market Terminal & Quantitative Intelligence Engine

---

## 1. Initial Workspace Status
- **Workspace Path**: `c:\Users\praja\Downloads\newml`
- **Initial File Count**: 0 (Clean directory initialization)
- **Status**: Blank workspace. Full implementation of backend, frontend, ML pipelines, WebSocket servers, exchange calendars, and data fabric is required.

---

## 2. Updated Data Fabric & Ingestion Architecture

### Data Fabric Architecture
```
                        ┌────────────────────┐
                        │   MARKET SOURCES   │
                        └─────────┬──────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
          INDIA LIVE           US LIVE            HISTORICAL
          PROVIDER             PROVIDER            yfinance
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                        ┌────────────────────┐
                        │ PROVIDER ADAPTER   │
                        └─────────┬──────────┘
                                  ▼
                        ┌────────────────────┐
                        │ INGESTION ENGINE   │
                        └─────────┬──────────┘
                                  ▼
                        ┌────────────────────┐
                        │ DATA VALIDATION    │
                        └─────────┬──────────┘
                                  ▼
                        ┌────────────────────┐
                        │ NORMALIZATION      │
                        └─────────┬──────────┘
                                  ▼
                        ┌────────────────────┐
                        │ EVENT STREAM       │
                        └─────────┬──────────┘
                                  │
              ┌───────────────────┼───────────────────┐
              ▼                   ▼                   ▼
          REAL-TIME CACHE     FEATURE ENGINE       DATABASE
              │                   │                   │
              │                   ▼                   │
              │              REGIME ENGINE            │
              │                   │                   │
              │                   ▼                   │
              │              ML INFERENCE             │
              │                   │                   │
              └───────────────────┼───────────────────┘
                                  ▼
                         SIGNAL + RISK + XAI
                                  │
                         ┌────────┴────────┐
                         ▼                 ▼
                     WebSocket           REST
                         │                 │
                         └────────┬────────┘
                                  ▼
                           NEXT.JS TERMINAL
```

### Provider Adapter & Capability Flags
Providers expose explicit capabilities:
- `historical`: Standard historical daily/minute OHLCV retrieval.
- `delayed_quote`: 15-minute delayed quotes.
- `realtime_quote`: Live top-of-book quotes.
- `trade_stream`: Low-latency real-time trade tick streaming.
- `bar_stream`: Real-time aggregated bar streaming.
- `market_status`: Exchange market state reporting.

`yfinance` is scoped exclusively for historical model training, development/fallback quote retrieval, and daily OHLCV dataset creation. It is never wrapped in a fake polling loop to simulate a live tick stream.

### Low-Latency Streaming & Timestamp Auditing
Rather than claiming "zero latency", ORION-Q measures exact end-to-end data latency:
1. `provider_timestamp`
2. `ingestion_timestamp`
3. `processing_timestamp`
4. `websocket_timestamp`
5. `frontend_received_timestamp`

Total end-to-end latency (`frontend_received_timestamp - provider_timestamp`) is explicitly displayed on the frontend (e.g., `DATA LATENCY: 38 ms`).

### Session Engine & Global Market Router Logic
At 15:30 IST:
1. NSE Exchange Calendar determines `NSE = CLOSED`.
2. Global Market Router switches `ACTIVE_MARKET = US` (if US session is `OPEN` or `PRE_MARKET`).
3. Frontend UI transitions main view to US Equities (`● OPEN`), while keeping Indian market status visible as `CLOSED` with `Last update: 15:30 IST` and `Next open: 09:15 IST`.
4. User retains manual override via `AUTO | INDIA | US | GLOBAL` selector.

---

## 3. Core Directives & Data State Policy
- **Data States**: Feeds explicitly declare state as `LIVE`, `DELAYED`, `STALE`, `CLOSED`, or `UNAVAILABLE`.
- **No Mock Metrics**: Zero fake prices, probabilities, accuracy metrics, or hardcoded ML results.
- **Leakage Prevention**: All transformations, features, and model hyperparameters are strictly fitted on training splits using `TimeSeriesSplit`.
