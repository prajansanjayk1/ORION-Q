import time
from typing import Dict, Optional, List, Set, Any
import pandas as pd
from backend.app.data.provider_adapter import BaseMarketDataProvider
from backend.app.data.yfinance_provider import YFinanceProvider
from backend.app.data.quality import DataQualityChecker
from backend.app.schemas.market import MarketQuote, ProviderCapability, DataState
from backend.app.core.logging import logger

class IngestionEngine:
    def __init__(self):
        self.providers: List[BaseMarketDataProvider] = [
            YFinanceProvider()
        ]
        self._quote_cache: Dict[str, MarketQuote] = {}
        self._hist_cache: Dict[str, Tuple[float, pd.DataFrame]] = {}
        self._event_dedup_set: Set[str] = set()
        self.provider_switches: List[Dict] = []
        self._last_processed_ts: Dict[str, float] = {}

        self.FRESH_THRESHOLD_SEC = 10
        self.STALE_THRESHOLD_SEC = 120
        self.EXPIRED_THRESHOLD_SEC = 900

    def add_provider(self, provider: BaseMarketDataProvider):
        self.providers.append(provider)

    def _check_duplicate(self, symbol: str, timestamp: float) -> bool:
        event_id = f"{symbol}:{timestamp}"
        if event_id in self._event_dedup_set:
            return True
        self._event_dedup_set.add(event_id)
        if len(self._event_dedup_set) > 10000:
            self._event_dedup_set.clear()
        return False

    def _check_out_of_order(self, symbol: str, timestamp: float) -> bool:
        last_ts = self._last_processed_ts.get(symbol, 0.0)
        if timestamp < last_ts:
            return True
        self._last_processed_ts[symbol] = timestamp
        return False

    def _record_provider_switch(self, symbol: str, from_provider: str, to_provider: str, reason: str):
        switch_info = {
            "symbol": symbol,
            "from_provider": from_provider,
            "to_provider": to_provider,
            "reason": reason,
            "switch_timestamp": time.time()
        }
        self.provider_switches.append(switch_info)
        logger.warning(f"Provider switch for {symbol}: {from_provider} -> {to_provider}. Reason: {reason}")

    def get_provider_health_summary(self) -> Dict[str, Any]:
        return {p.provider_name: p.get_provider_health() for p in self.providers}

    def get_quote(self, symbol: str) -> Optional[MarketQuote]:
        symbol_clean = symbol.upper().strip()
        ingestion_ts = time.time()

        if symbol_clean in self._quote_cache:
            cached_q = self._quote_cache[symbol_clean]
            if cached_q.timestamp and (ingestion_ts - cached_q.timestamp < 15.0):
                return cached_q
        
        last_failed_provider = None
        last_failure_reason = None

        for provider in self.providers:
            if not provider.health.is_available():
                continue
                
            if provider.has_capability(ProviderCapability.DELAYED_QUOTE) or provider.has_capability(ProviderCapability.REALTIME_QUOTE):
                try:
                    start_time = time.time()
                    quote = provider.get_quote(symbol_clean)
                    latency = (time.time() - start_time) * 1000
                    
                    if quote is not None:
                        is_valid, errors = DataQualityChecker.validate_quote(quote)
                        if is_valid:
                            provider.health.record_success(latency)
                            if last_failed_provider:
                                self._record_provider_switch(symbol_clean, last_failed_provider, provider.provider_name, last_failure_reason)
                            
                            self._quote_cache[symbol_clean] = quote
                            return quote
                        else:
                            reason = f"Data quality check failed: {errors}"
                            provider.health.record_failure(reason)
                            last_failed_provider = provider.provider_name
                            last_failure_reason = reason
                    else:
                        reason = "Quote returned None"
                        provider.health.record_failure(reason)
                        last_failed_provider = provider.provider_name
                        last_failure_reason = reason
                except Exception as e:
                    reason = f"Exception: {str(e)}"
                    provider.health.record_failure(reason)
                    last_failed_provider = provider.provider_name
                    last_failure_reason = reason

        # If all providers fail or are unavailable
        if symbol_clean in self._quote_cache:
            cached = self._quote_cache[symbol_clean]
            cached.data_state = DataState.STALE
            return cached

        return None

    def get_historical_data(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> pd.DataFrame:
        symbol_clean = symbol.upper().strip()
        cache_key = f"{symbol_clean}:{period}:{interval}"
        now = time.time()
        if cache_key in self._hist_cache:
            ts, df = self._hist_cache[cache_key]
            if now - ts < 60.0:  # 60 seconds TTL cache
                return df
        last_failed_provider = None
        last_failure_reason = None

        for provider in self.providers:
            if not provider.health.is_available():
                continue
                
            if provider.has_capability(ProviderCapability.HISTORICAL):
                try:
                    start_time = time.time()
                    df = provider.get_historical_ohlcv(symbol_clean, period=period, interval=interval)
                    latency = (time.time() - start_time) * 1000
                    
                    if not df.empty:
                        is_valid, errors = DataQualityChecker.validate_ohlcv_dataframe(df)
                        if not is_valid:
                            logger.warning(f"Data quality warnings for historical {symbol_clean} from {provider.provider_name}: {errors}")
                            df = df.drop_duplicates(subset=["timestamp"]).dropna(subset=["close"])
                        
                        provider.health.record_success(latency)
                        if last_failed_provider:
                            self._record_provider_switch(symbol_clean, last_failed_provider, provider.provider_name, last_failure_reason)
                        self._hist_cache[cache_key] = (now, df)
                        return df
                    else:
                        reason = "Empty DataFrame returned"
                        provider.health.record_failure(reason)
                        last_failed_provider = provider.provider_name
                        last_failure_reason = reason
                except Exception as e:
                    reason = f"Exception: {str(e)}"
                    provider.health.record_failure(reason)
                    last_failed_provider = provider.provider_name
                    last_failure_reason = reason

        return pd.DataFrame()

    def is_data_stale(self, symbol: str) -> bool:
        symbol_clean = symbol.upper().strip()
        if symbol_clean not in self._quote_cache:
            return True
        quote = self._quote_cache[symbol_clean]
        if not quote.timestamp:
            return True
        return (time.time() - quote.timestamp) > self.STALE_THRESHOLD_SEC

    def get_data_freshness(self, symbol: str) -> str:
        symbol_clean = symbol.upper().strip()
        if symbol_clean not in self._quote_cache:
            return 'EXPIRED'
        
        quote = self._quote_cache[symbol_clean]
        if not quote.timestamp:
            return 'EXPIRED'
            
        age = time.time() - quote.timestamp
        if age <= self.FRESH_THRESHOLD_SEC:
            return 'FRESH'
        elif age <= self.STALE_THRESHOLD_SEC:
            return 'STALE'
        else:
            return 'EXPIRED'


ingestion_engine = IngestionEngine()
