from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
from backend.app.ml.model_registry import model_registry
from backend.app.services.prediction_engine import prediction_engine

router = APIRouter()


@router.get("/registry/champions")
def get_all_champions():
    """Returns all current CHAMPION models across instruments."""
    champions = model_registry.get_all_champions()
    return {symbol: meta.model_dump() for symbol, meta in champions.items()}


@router.get("/registry/history/{symbol}")
def get_model_history(symbol: str):
    """Returns model version history and lineage for a specific symbol."""
    history = model_registry.get_history(symbol)
    if not history:
        raise HTTPException(status_code=404, detail=f"No model registry entries found for {symbol}")
    return [meta.model_dump() for meta in history]


@router.get("/registry/evaluation/{symbol}")
def get_model_evaluation(symbol: str):
    """
    Returns full evaluation suite for a symbol:
    - Multi-model ROC Curves and AUC scores
    - 3x3 Confusion Matrices per model
    - Precision, Recall, F1-Score, Log Loss
    - Walk-Forward Leaderboard Comparison
    """
    symbol_clean = symbol.upper().strip()
    champion = model_registry.get_champion(symbol_clean)

    # Ensure model prediction engine has run for this symbol to populate evaluation suite
    if not champion or not champion.evaluation_suite:
        pred = prediction_engine.predict(symbol_clean)
        champion = model_registry.get_champion(symbol_clean)

    if not champion or not champion.evaluation_suite:
        raise HTTPException(status_code=404, detail=f"Model evaluation suite for {symbol} is unavailable")

    return {
        "symbol": symbol_clean,
        "model_id": champion.model_id,
        "algorithm": champion.algorithm,
        "metrics": champion.metrics,
        "evaluation_suite": champion.evaluation_suite
    }
