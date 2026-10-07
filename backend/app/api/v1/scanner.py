from fastapi import APIRouter
from typing import List, Dict, Any
from concurrent.futures import ThreadPoolExecutor
from backend.app.services.prediction_engine import prediction_engine
from backend.app.core.config import settings

router = APIRouter()


@router.get("/scanner")
def scan_markets():
    symbols = ["AAPL", "MSFT", "NVDA", "RELIANCE", "TCS", "INFY"]

    def _get_pred(sym: str):
        try:
            pred = prediction_engine.predict(sym)
            if pred:
                conf_dict = pred.signal.conformal_range.model_dump() if hasattr(pred.signal.conformal_range, "model_dump") else pred.signal.conformal_range
                return {
                    "symbol": pred.symbol,
                    "price": pred.quote_price,
                    "currency": pred.currency,
                    "data_state": pred.data_state,
                    "signal": pred.signal.signal,
                    "calibrated_probability": pred.signal.calibrated_probability,
                    "expected_return_pct": pred.signal.expected_return_pct,
                    "conformal_range": conf_dict,
                    "regime": pred.regime.regime_name,
                    "stability": pred.stability.stability_level,
                    "model_accuracy": pred.model_leaderboard.get("Stacked Ensemble", 75.0)
                }
        except Exception:
            pass
        return None

    with ThreadPoolExecutor(max_workers=6) as executor:
        futures = [executor.submit(_get_pred, sym) for sym in symbols]
        results = [f.result() for f in futures if f.result() is not None]

    # Sort into categories
    opportunities = [r for r in results if r["signal"] in ["STRONG BUY", "BUY"]]
    risks = [r for r in results if r["signal"] in ["STRONG SELL", "SELL"]]
    no_trade = [r for r in results if r["signal"] == "NO TRADE"]
    momentum = sorted(results, key=lambda x: x.get("expected_return_pct", 0.0), reverse=True)

    return {
        "OPPORTUNITIES": opportunities if opportunities else results[:2],
        "RISKS": risks,
        "NO_TRADE": no_trade,
        "MOMENTUM": momentum,
        "ALL_SIGNALS": results
    }

