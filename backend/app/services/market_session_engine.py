from datetime import datetime
import pytz
from backend.app.data.exchange_calendar import ExchangeCalendar
from backend.app.schemas.market import MarketSessionInfo, MarketSessionState, GlobalMarketStatus


class MarketSessionEngine:
    def __init__(self):
        self.nse_cal = ExchangeCalendar("NSE", "Asia/Kolkata")
        self.bse_cal = ExchangeCalendar("BSE", "Asia/Kolkata")
        self.nyse_cal = ExchangeCalendar("NYSE", "America/New_York")
        self.nasdaq_cal = ExchangeCalendar("NASDAQ", "America/New_York")

    def get_session(self, exchange: str) -> MarketSessionInfo:
        ex = exchange.upper()
        if ex == "NSE":
            return self.nse_cal.get_session_info()
        elif ex == "BSE":
            return self.bse_cal.get_session_info()
        elif ex == "NYSE":
            return self.nyse_cal.get_session_info()
        elif ex == "NASDAQ":
            return self.nasdaq_cal.get_session_info()
        else:
            return self.nyse_cal.get_session_info()


class GlobalMarketRouter:
    def __init__(self, session_engine: MarketSessionEngine = None):
        self.session_engine = session_engine or MarketSessionEngine()

    def get_global_status(self, mode: str = "AUTO") -> GlobalMarketStatus:
        india_info = self.session_engine.get_session("NSE")
        us_info = self.session_engine.get_session("NASDAQ")

        mode_upper = mode.upper()
        if mode_upper == "INDIA":
            active_market = "INDIA"
        elif mode_upper == "US":
            active_market = "US"
        elif mode_upper == "GLOBAL":
            active_market = "GLOBAL"
        else:
            # AUTO mode
            if india_info.status in [MarketSessionState.OPEN, MarketSessionState.PRE_MARKET]:
                active_market = "INDIA"
            elif us_info.status in [MarketSessionState.OPEN, MarketSessionState.PRE_MARKET]:
                active_market = "US"
            else:
                # If both are closed, default to active region depending on current UTC hour
                # Or set to GLOBAL / AFTER-HOURS
                active_market = "GLOBAL"

        return GlobalMarketStatus(
            active_market=active_market,
            mode=mode_upper,
            india_session=india_info,
            us_session=us_info,
            timestamp=datetime.now(pytz.utc).timestamp()
        )


market_session_engine = MarketSessionEngine()
global_market_router = GlobalMarketRouter(market_session_engine)
