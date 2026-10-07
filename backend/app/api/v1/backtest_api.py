from fastapi import APIRouter, HTTPException, Query
from typing import Dict, Any, Optional
from backend.app.data.ingestion_engine import ingestion_engine
from backend.app.services.backtest_engine import backtest_engine

router = APIRouter()


@router.get("/backtest/run")
def run_backtest(
    symbol: str = Query("AAPL", description="Ticker symbol"),
    strategy: str = Query("ADAPTIVE HYBRID", description="Strategy type"),
    period: str = Query("1y", description="Historical period"),
    commission_bps: float = Query(5.0, description="Commission in basis points"),
    slippage_bps: float = Query(2.0, description="Slippage in basis points")
):
    """
    Executes transaction-cost aware event-driven strategy backtest.
    """
    df = ingestion_engine.get_historical_data(symbol, period=period, interval="1d")
    if df.empty:
        raise HTTPException(status_code=404, detail=f"No historical price data found for {symbol}")

    summary, equity_df = backtest_engine.run_backtest(
        df, strategy=strategy, commission_bps=commission_bps, slippage_bps=slippage_bps
    )

    records = []
    if not equity_df.empty:
        equity_df["timestamp"] = equity_df["timestamp"].dt.strftime("%Y-%m-%d")
        records = equity_df.to_dict(orient="records")

    return {
        "symbol": symbol.upper(),
        "summary": summary.model_dump(),
        "equity_curve": records
    }
