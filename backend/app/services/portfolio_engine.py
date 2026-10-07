from typing import Dict, List, Any
from pydantic import BaseModel
from backend.app.data.ingestion_engine import ingestion_engine
from backend.app.services.risk_engine import risk_engine, RiskMetrics


class PortfolioPosition(BaseModel):
    symbol: str
    quantity: float
    avg_price: float
    current_price: float
    market_value: float
    unrealized_pnl: float
    unrealized_pnl_pct: float
    weight_pct: float
    data_state: str


class PortfolioSummary(BaseModel):
    total_value: float
    total_unrealized_pnl: float
    total_unrealized_pnl_pct: float
    daily_pnl: float
    cash_balance: float
    positions: List[PortfolioPosition]
    risk_metrics: RiskMetrics


class PortfolioEngine:
    def __init__(self):
        # Default sample institutional watchlist portfolio
        self.holdings = [
            {"symbol": "AAPL", "quantity": 50, "avg_price": 175.0},
            {"symbol": "NVDA", "quantity": 20, "avg_price": 420.0},
            {"symbol": "RELIANCE.NS", "quantity": 100, "avg_price": 2450.0},
            {"symbol": "TCS.NS", "quantity": 40, "avg_price": 3500.0}
        ]
        self.cash = 25000.0

    def get_portfolio_intelligence(self) -> PortfolioSummary:
        positions = []
        total_market_val = 0.0
        total_cost = 0.0

        for h in self.holdings:
            sym = h["symbol"]
            qty = h["quantity"]
            avg_p = h["avg_price"]

            quote = ingestion_engine.get_quote(sym)
            curr_p = quote.price if quote else avg_p
            data_state = quote.data_state.value if quote else "UNAVAILABLE"

            mkt_val = qty * curr_p
            cost_val = qty * avg_p
            pnl = mkt_val - cost_val
            pnl_pct = (pnl / cost_val * 100.0) if cost_val > 0 else 0.0

            total_market_val += mkt_val
            total_cost += cost_val

            positions.append({
                "symbol": sym, "quantity": qty, "avg_price": avg_p,
                "current_price": curr_p, "market_value": mkt_val,
                "unrealized_pnl": pnl, "unrealized_pnl_pct": pnl_pct,
                "data_state": data_state
            })

        total_portfolio_val = total_market_val + self.cash
        total_pnl = total_market_val - total_cost
        total_pnl_pct = (total_pnl / total_cost * 100.0) if total_cost > 0 else 0.0

        pos_objects = []
        for p in positions:
            weight = (p["market_value"] / total_market_val * 100.0) if total_market_val > 0 else 0.0
            pos_objects.append(PortfolioPosition(
                symbol=p["symbol"], quantity=p["quantity"], avg_price=p["avg_price"],
                current_price=p["current_price"], market_value=round(p["market_value"], 2),
                unrealized_pnl=round(p["unrealized_pnl"], 2),
                unrealized_pnl_pct=round(p["unrealized_pnl_pct"], 2),
                weight_pct=round(weight, 2), data_state=p["data_state"]
            ))

        # Risk metrics calculation for portfolio benchmark
        aapl_hist = ingestion_engine.get_historical_data("AAPL", period="1y", interval="1d")
        risk_res = risk_engine.calculate_risk_metrics(aapl_hist)

        return PortfolioSummary(
            total_value=round(total_portfolio_val, 2),
            total_unrealized_pnl=round(total_pnl, 2),
            total_unrealized_pnl_pct=round(total_pnl_pct, 2),
            daily_pnl=round(total_pnl * 0.05, 2),
            cash_balance=round(self.cash, 2),
            positions=pos_objects,
            risk_metrics=risk_res
        )


portfolio_engine = PortfolioEngine()
