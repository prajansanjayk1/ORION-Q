from fastapi import APIRouter, HTTPException
from backend.app.services.prediction_engine import prediction_engine, PredictionResult

router = APIRouter()


@router.get("/prediction/{symbol}", response_model=PredictionResult)
def get_prediction(symbol: str):
    res = prediction_engine.predict(symbol)
    if not res:
        raise HTTPException(status_code=404, detail=f"Prediction engine could not resolve intelligence for '{symbol}'")
    return res


@router.get("/regime/{symbol}")
def get_regime(symbol: str):
    res = prediction_engine.predict(symbol)
    if not res:
        raise HTTPException(status_code=404, detail=f"Regime calculation unavailable for '{symbol}'")
    return res.regime


@router.get("/explanation/{symbol}")
def get_explanation(symbol: str):
    res = prediction_engine.predict(symbol)
    if not res:
        raise HTTPException(status_code=404, detail=f"Explanation calculation unavailable for '{symbol}'")
    return {
        "explainability": res.explainability,
        "counterfactuals": res.counterfactuals
    }
