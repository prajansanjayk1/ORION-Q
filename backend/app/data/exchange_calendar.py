import json
import os
import pytz
from datetime import datetime, time as dtime, timedelta
from typing import Dict, Any, Tuple, Optional

from backend.app.schemas.market import MarketSessionState, MarketSessionInfo, GlobalMarketStatus

class ExchangeCalendar:
    def __init__(self, exchange: str, timezone_str: Optional[str] = None):
        self.exchange = exchange
        
        # Load holidays.json
        current_dir = os.path.dirname(os.path.abspath(__file__))
        holidays_path = os.path.join(current_dir, "holidays.json")
        
        try:
            with open(holidays_path, "r") as f:
                data = json.load(f)
        except Exception:
            data = {"exchanges": {}}
            
        exchanges_data = data.get("exchanges", {})
        if exchange not in exchanges_data:
            self.exchange_data = None
            self.tz = pytz.timezone(timezone_str) if timezone_str else pytz.UTC
            return
            
        self.exchange_data = exchanges_data[exchange]
        
        # Inherit holidays for BSE and NASDAQ
        if "note" in self.exchange_data:
            if exchange == "BSE" and "NSE" in exchanges_data:
                self.exchange_data["holidays"] = exchanges_data["NSE"].get("holidays", {})
                self.exchange_data["shortened_sessions"] = exchanges_data["NSE"].get("shortened_sessions", {})
            elif exchange == "NASDAQ" and "NYSE" in exchanges_data:
                self.exchange_data["holidays"] = exchanges_data["NYSE"].get("holidays", {})
                self.exchange_data["shortened_sessions"] = exchanges_data["NYSE"].get("shortened_sessions", {})
                    
        self.tz = pytz.timezone(self.exchange_data.get("timezone", "UTC"))
        
    def is_weekend(self, dt: datetime) -> bool:
        # 5 = Saturday, 6 = Sunday
        return dt.weekday() >= 5
        
    def is_holiday(self, dt: datetime) -> Tuple[bool, Optional[str]]:
        if not self.exchange_data:
            return False, None
            
        year_str = str(dt.year)
        date_str = dt.strftime("%Y-%m-%d")
        
        holidays_data = self.exchange_data.get("holidays", {})
        year_holidays = holidays_data.get(year_str, [])
        
        for holiday in year_holidays:
            if holiday.get("date") == date_str:
                return True, holiday.get("name")
                
        return False, None
        
    def is_shortened_session(self, dt: datetime) -> Tuple[bool, Optional[Dict]]:
        if not self.exchange_data:
            return False, None
            
        year_str = str(dt.year)
        date_str = dt.strftime("%Y-%m-%d")
        
        shortened_data = self.exchange_data.get("shortened_sessions", {})
        year_shortened = shortened_data.get(year_str, [])
        
        for session in year_shortened:
            if session.get("date") == date_str:
                return True, session
                
        return False, None
        
    def get_next_trading_day(self, dt: datetime) -> datetime:
        next_day = dt + timedelta(days=1)
        while True:
            is_wknd = self.is_weekend(next_day)
            is_hol, _ = self.is_holiday(next_day)
            if not is_wknd and not is_hol:
                break
            next_day += timedelta(days=1)
            
        if self.exchange_data:
            regular_hours = self.exchange_data.get("regular_hours", {})
            open_time_str = regular_hours.get("open", "09:00")
            open_h, open_m = map(int, open_time_str.split(':'))
            
            is_shortened, short_session = self.is_shortened_session(next_day)
            if is_shortened and short_session and "open" in short_session:
                open_h, open_m = map(int, short_session["open"].split(':'))
                
            next_day = next_day.replace(hour=open_h, minute=open_m, second=0, microsecond=0)
            
        return next_day

    def get_session_status(self, dt: datetime) -> MarketSessionState:
        if not self.exchange_data:
            return MarketSessionState.UNKNOWN
            
        if self.is_weekend(dt):
            return MarketSessionState.CLOSED
            
        is_hol, _ = self.is_holiday(dt)
        if is_hol:
            return MarketSessionState.HOLIDAY
            
        regular_hours = self.exchange_data.get("regular_hours", {})
        pre_market_start = regular_hours.get("pre_market_start", "00:00")
        open_time = regular_hours.get("open", "09:00")
        close_time = regular_hours.get("close", "16:00")
        post_market_end = regular_hours.get("post_market_end", "23:59")
        
        is_shortened, short_session = self.is_shortened_session(dt)
        if is_shortened and short_session:
            if "open" in short_session:
                open_time = short_session["open"]
            if "close" in short_session:
                close_time = short_session["close"]
                
        time_format = "%H:%M"
        t_pre = datetime.strptime(pre_market_start, time_format).time()
        t_open = datetime.strptime(open_time, time_format).time()
        t_close = datetime.strptime(close_time, time_format).time()
        t_post = datetime.strptime(post_market_end, time_format).time()
        
        current_time = dt.time()
        
        if t_pre <= current_time < t_open:
            return MarketSessionState.PRE_MARKET
        elif t_open <= current_time < t_close:
            return MarketSessionState.OPEN
        elif t_close <= current_time < t_post:
            return MarketSessionState.POST_MARKET
        else:
            return MarketSessionState.CLOSED

    def detect_clock_skew(self, provider_timestamp: float, tolerance_seconds: float = 5.0) -> Tuple[bool, float]:
        current_timestamp = datetime.now(pytz.UTC).timestamp()
        skew = provider_timestamp - current_timestamp
        has_skew = abs(skew) > tolerance_seconds
        return has_skew, skew

    def check_session_conflict(self, provider_reported_status: str, current_dt: datetime = None) -> bool:
        if current_dt is None:
            current_dt = datetime.now(self.tz)
            
        expected_status = self.get_session_status(current_dt)
        provider_status_upper = provider_reported_status.upper()
        
        expected_is_open = (expected_status == MarketSessionState.OPEN)
        provider_is_open = (provider_status_upper == "OPEN")
        
        return expected_is_open != provider_is_open

    def get_session_info(self, current_dt: datetime = None) -> MarketSessionInfo:
        now_utc = datetime.now(pytz.utc)
        if not self.exchange_data:
            return MarketSessionInfo(
                exchange=self.exchange,
                status=MarketSessionState.UNKNOWN,
                session="UNKNOWN",
                active_market="GLOBAL",
                server_time=now_utc.isoformat(),
                exchange_time=now_utc.strftime("%Y-%m-%d %H:%M:%S %Z"),
                next_open="",
                session_status_conflict=False
            )
            
        if current_dt is None:
            current_dt = datetime.now(self.tz)
        elif current_dt.tzinfo is None:
            current_dt = self.tz.localize(current_dt)
        else:
            current_dt = current_dt.astimezone(self.tz)
            
        state = self.get_session_status(current_dt)
        holiday_name = None
        
        if state == MarketSessionState.HOLIDAY:
            _, holiday_name = self.is_holiday(current_dt)
            
        is_shortened, _ = self.is_shortened_session(current_dt)
        next_open_dt = self.get_next_trading_day(current_dt)
        next_open_str = next_open_dt.strftime("%Y-%m-%d %H:%M %Z")

        active_region = "INDIA" if self.exchange in ["NSE", "BSE"] else "US" if self.exchange in ["NYSE", "NASDAQ"] else "GLOBAL"
        session_str = "REGULAR" if state == MarketSessionState.OPEN else state.value

        return MarketSessionInfo(
            exchange=self.exchange,
            status=state,
            session=session_str,
            active_market=active_region,
            server_time=now_utc.isoformat(),
            exchange_time=current_dt.strftime("%Y-%m-%d %H:%M:%S %Z"),
            next_open=next_open_str,
            holiday_name=holiday_name,
            is_shortened_session=is_shortened,
            session_status_conflict=False,
            timezone=str(self.tz),
            currency=self.exchange_data.get("currency", "USD")
        )


class GlobalMarketRouter:
    def __init__(self):
        self.exchanges = {
            "NSE": ExchangeCalendar("NSE"),
            "NYSE": ExchangeCalendar("NYSE"),
            "LSE": ExchangeCalendar("LSE"),
            "TSE": ExchangeCalendar("TSE"),
            "HKEX": ExchangeCalendar("HKEX"),
            "BSE": ExchangeCalendar("BSE"),
            "NASDAQ": ExchangeCalendar("NASDAQ")
        }

    def get_active_market(self, mode: str = 'AUTO') -> str:
        if mode != 'AUTO':
            return mode
            
        nse_info = self.exchanges["NSE"].get_session_info()
        nyse_info = self.exchanges["NYSE"].get_session_info()
        
        if nse_info.status == MarketSessionState.OPEN:
            return 'INDIA'
            
        if nyse_info.status == MarketSessionState.OPEN:
            return 'US'
            
        if nse_info.status != MarketSessionState.OPEN and nyse_info.status == MarketSessionState.PRE_MARKET:
            return 'US'
            
        return 'GLOBAL'

    def get_global_status(self, mode: str = 'AUTO') -> GlobalMarketStatus:
        import time
        india_session = self.exchanges["NSE"].get_session_info()
        us_session = self.exchanges["NASDAQ"].get_session_info()
        uk_session = self.exchanges["LSE"].get_session_info()
        japan_session = self.exchanges["TSE"].get_session_info()
        hongkong_session = self.exchanges["HKEX"].get_session_info()
        
        all_markets_closed = True
        after_hours_available = False
        
        for info in [india_session, us_session, uk_session, japan_session, hongkong_session]:
            if info.status == MarketSessionState.OPEN:
                all_markets_closed = False
            if info.status in (MarketSessionState.PRE_MARKET, MarketSessionState.POST_MARKET):
                after_hours_available = True
                
        active_market = self.get_active_market(mode)
        
        return GlobalMarketStatus(
            active_market=active_market,
            mode=mode,
            india_session=india_session,
            us_session=us_session,
            uk_session=uk_session,
            japan_session=japan_session,
            hongkong_session=hongkong_session,
            timestamp=time.time(),
            all_markets_closed=all_markets_closed,
            after_hours_available=after_hours_available
        )
