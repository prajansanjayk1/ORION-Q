import pytest
from datetime import datetime
import pytz
from backend.app.data.exchange_calendar import ExchangeCalendar
from backend.app.services.market_session_engine import MarketSessionEngine, GlobalMarketRouter
from backend.app.schemas.market import MarketSessionState, DataState
from backend.app.data.yfinance_provider import YFinanceProvider


def test_exchange_calendar_nse():
    cal = ExchangeCalendar("NSE", "Asia/Kolkata")
    
    # 2026-08-12 is Wednesday
    # Test regular trading hours: 10:30 IST
    ist_tz = pytz.timezone("Asia/Kolkata")
    open_dt = ist_tz.localize(datetime(2026, 8, 12, 10, 30))
    info = cal.get_session_info(open_dt)
    assert info.status == MarketSessionState.OPEN
    assert info.session == "REGULAR"

    # Test closed hours: 20:00 IST
    closed_dt = ist_tz.localize(datetime(2026, 8, 12, 20, 0))
    info_closed = cal.get_session_info(closed_dt)
    assert info_closed.status == MarketSessionState.CLOSED
    assert info_closed.session == "CLOSED"


def test_global_market_router():
    router = GlobalMarketRouter()
    status = router.get_global_status(mode="AUTO")
    assert status.mode == "AUTO"
    assert status.active_market in ["INDIA", "US", "GLOBAL"]


def test_closed_market_last_data_retrieval():
    provider = YFinanceProvider()
    # Test quote retrieval for RELIANCE.NS (NSE market is closed at night)
    quote = provider.get_quote("RELIANCE.NS")
    assert quote is not None
    assert quote.symbol == "RELIANCE.NS"
    assert quote.price > 0
    assert quote.data_state == DataState.CLOSED
    assert quote.open > 0
    assert quote.high >= quote.low
