from fastapi import APIRouter, Query
from backend.app.services.market_session_engine import global_market_router
from backend.app.schemas.market import GlobalMarketStatus

router = APIRouter()


@router.get("/market-session", response_model=GlobalMarketStatus)
def get_market_session(mode: str = Query("AUTO", description="AUTO | INDIA | US | GLOBAL")):
    return global_market_router.get_global_status(mode=mode)


@router.get("/markets")
def get_supported_markets():
    return {
        "supported_modes": ["AUTO", "INDIA", "US", "GLOBAL"],
        "india_indices": ["^NSEI", "^BSESN", "^NSEBANK", "^INDIAVIX"],
        "us_indices": ["^GSPC", "^IXIC", "^DJI", "^VIX"]
    }
