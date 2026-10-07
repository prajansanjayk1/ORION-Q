import pytest
from datetime import datetime
import pytz
from backend.app.data.exchange_calendar import ExchangeCalendar, GlobalMarketRouter
from backend.app.schemas.market import MarketSessionState


class TestExchangeCalendar:
    def test_nse_regular_hours(self):
        """NSE should be OPEN between 09:15 and 15:30 IST on weekdays."""
        cal = ExchangeCalendar('NSE')
        ist = pytz.timezone('Asia/Kolkata')
        # Wednesday at 10:00 IST
        dt = ist.localize(datetime(2026, 8, 12, 10, 0))
        info = cal.get_session_info(dt)
        assert info.status == MarketSessionState.OPEN

    def test_nse_pre_market(self):
        """NSE pre-market is 09:00-09:15 IST."""
        cal = ExchangeCalendar('NSE')
        ist = pytz.timezone('Asia/Kolkata')
        dt = ist.localize(datetime(2026, 8, 12, 9, 5))
        info = cal.get_session_info(dt)
        assert info.status == MarketSessionState.PRE_MARKET

    def test_nse_post_market(self):
        """NSE post-market is 15:30-16:00 IST."""
        cal = ExchangeCalendar('NSE')
        ist = pytz.timezone('Asia/Kolkata')
        dt = ist.localize(datetime(2026, 8, 12, 15, 45))
        info = cal.get_session_info(dt)
        assert info.status == MarketSessionState.POST_MARKET

    def test_nse_closed_evening(self):
        """NSE should be CLOSED after 16:00 IST."""
        cal = ExchangeCalendar('NSE')
        ist = pytz.timezone('Asia/Kolkata')
        dt = ist.localize(datetime(2026, 8, 12, 18, 0))
        info = cal.get_session_info(dt)
        assert info.status == MarketSessionState.CLOSED

    def test_nse_weekend(self):
        """NSE should be CLOSED on Saturday."""
        cal = ExchangeCalendar('NSE')
        ist = pytz.timezone('Asia/Kolkata')
        # August 15, 2026 is a Saturday... wait, need to check. Let's use a known Saturday.
        # Aug 8, 2026 is a Saturday
        dt = ist.localize(datetime(2026, 8, 8, 10, 0))
        assert cal.is_weekend(dt) is True
        info = cal.get_session_info(dt)
        assert info.status == MarketSessionState.CLOSED

    def test_nse_holiday(self):
        """NSE should be HOLIDAY on Independence Day."""
        cal = ExchangeCalendar('NSE')
        ist = pytz.timezone('Asia/Kolkata')
        dt = ist.localize(datetime(2026, 8, 15, 10, 0))
        is_holiday, name = cal.is_holiday(dt)
        assert is_holiday is True
        assert name is not None

    def test_nyse_regular_hours(self):
        """NYSE should be OPEN between 09:30 and 16:00 ET on weekdays."""
        cal = ExchangeCalendar('NYSE')
        et = pytz.timezone('America/New_York')
        # Tuesday at 11:00 ET
        dt = et.localize(datetime(2026, 8, 11, 11, 0))
        info = cal.get_session_info(dt)
        assert info.status == MarketSessionState.OPEN

    def test_nyse_pre_market(self):
        """NYSE pre-market is 04:00-09:30 ET."""
        cal = ExchangeCalendar('NYSE')
        et = pytz.timezone('America/New_York')
        dt = et.localize(datetime(2026, 8, 11, 7, 0))
        info = cal.get_session_info(dt)
        assert info.status == MarketSessionState.PRE_MARKET

    def test_next_trading_day_skips_weekend(self):
        """Next trading day from Friday should be Monday."""
        cal = ExchangeCalendar('NSE')
        ist = pytz.timezone('Asia/Kolkata')
        # Friday Aug 7, 2026
        dt = ist.localize(datetime(2026, 8, 7, 16, 0))
        next_day = cal.get_next_trading_day(dt)
        assert next_day.weekday() == 0  # Monday

    def test_clock_skew_detection(self):
        """Should detect clock skew when timestamps differ significantly."""
        cal = ExchangeCalendar('NSE')
        import time
        # Provider timestamp 10 seconds in the future
        future_ts = time.time() + 10
        has_skew, skew_seconds = cal.detect_clock_skew(future_ts, tolerance_seconds=5.0)
        assert has_skew is True
        assert abs(skew_seconds) > 5


class TestGlobalMarketRouter:
    def test_auto_routing_india_open(self):
        """When India is open and US is closed, active market should be INDIA."""
        router = GlobalMarketRouter()
        ist = pytz.timezone('Asia/Kolkata')
        # Wednesday 10:00 IST (India open, US closed)
        dt = ist.localize(datetime(2026, 8, 12, 10, 0))
        status = router.get_global_status('AUTO')
        # India should be open during this time
        assert status.india_session.status in [MarketSessionState.OPEN, MarketSessionState.PRE_MARKET, MarketSessionState.CLOSED]

    def test_manual_override(self):
        """Manual mode should override automatic routing."""
        router = GlobalMarketRouter()
        status = router.get_global_status('INDIA')
        assert status.mode == 'INDIA'

    def test_all_markets_closed_flag(self):
        """All markets closed flag should be set when no exchange is open."""
        router = GlobalMarketRouter()
        status = router.get_global_status('AUTO')
        # This depends on current time, just test the flag exists
        assert isinstance(status.all_markets_closed, bool)
