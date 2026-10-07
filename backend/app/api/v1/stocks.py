from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Any
from backend.app.data.ingestion_engine import ingestion_engine
from backend.app.schemas.market import MarketQuote

router = APIRouter()


@router.get("/stocks/{symbol}", response_model=MarketQuote)
def get_stock_quote(symbol: str):
    quote = ingestion_engine.get_quote(symbol)
    if not quote:
        raise HTTPException(status_code=404, detail=f"Market quote for symbol '{symbol}' is unavailable")
    return quote


@router.get("/stocks/{symbol}/history")
def get_stock_history(
    symbol: str,
    period: str = Query("1y", description="Data period"),
    interval: str = Query("1d", description="Bar interval")
):
    df = ingestion_engine.get_historical_data(symbol, period=period, interval=interval)
    if df.empty:
        raise HTTPException(status_code=404, detail=f"Historical data for symbol '{symbol}' is unavailable")

    if "timestamp" in df.columns:
        df["timestamp"] = df["timestamp"].dt.strftime("%Y-%m-%d")

    return df.to_dict(orient="records")
