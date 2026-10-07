import time
from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any
import pandas as pd
from backend.app.schemas.market import (
    MarketQuote, ProviderCapability, ProviderCapabilities
)


class ProviderHealthStatus:
    """Tracks the health and failure history of a provider."""
    def __init__(self, provider_name: str):
        self.provider_name = provider_name
        self.is_healthy: bool = True
        self.consecutive_failures: int = 0
        self.total_failures: int = 0
        self.last_failure_reason: Optional[str] = None
        self.last_failure_timestamp: Optional[float] = None
        self.last_success_timestamp: Optional[float] = None
        self.is_rate_limited: bool = False
        self.rate_limit_reset_at: Optional[float] = None
        self.average_latency_ms: float = 0.0
        self._latency_samples: List[float] = []

    def record_success(self, latency_ms: float):
        self.is_healthy = True
        self.consecutive_failures = 0
        self.last_success_timestamp = time.time()
        self.is_rate_limited = False
        self._latency_samples.append(latency_ms)
        if len(self._latency_samples) > 100:
            self._latency_samples = self._latency_samples[-100:]
        self.average_latency_ms = sum(self._latency_samples) / len(self._latency_samples)

    def record_failure(self, reason: str):
        self.consecutive_failures += 1
        self.total_failures += 1
        self.last_failure_reason = reason
        self.last_failure_timestamp = time.time()
        if self.consecutive_failures >= 3:
            self.is_healthy = False

    def record_rate_limit(self, retry_after_seconds: Optional[float] = None):
        self.is_rate_limited = True
        if retry_after_seconds:
            self.rate_limit_reset_at = time.time() + retry_after_seconds
        else:
            self.rate_limit_reset_at = time.time() + 60  # default 60s backoff

    def is_available(self) -> bool:
        if self.is_rate_limited:
            if self.rate_limit_reset_at and time.time() > self.rate_limit_reset_at:
                self.is_rate_limited = False
                return True
            return False
        return self.is_healthy

    def to_dict(self) -> Dict[str, Any]:
        return {
            "provider_name": self.provider_name,
            "is_healthy": self.is_healthy,
            "is_available": self.is_available(),
            "consecutive_failures": self.consecutive_failures,
            "total_failures": self.total_failures,
            "last_failure_reason": self.last_failure_reason,
            "is_rate_limited": self.is_rate_limited,
            "average_latency_ms": round(self.average_latency_ms, 2)
        }


class BaseMarketDataProvider(ABC):
    """Abstract base class for all market data providers."""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        pass

    @property
    @abstractmethod
    def capabilities(self) -> ProviderCapabilities:
        pass

    def __init__(self):
        self.health = ProviderHealthStatus(self.__class__.__name__)
        self._timeout_seconds: float = 10.0

    def has_capability(self, capability: ProviderCapability) -> bool:
        cap_map = {
            ProviderCapability.HISTORICAL: self.capabilities.historical,
            ProviderCapability.DELAYED_QUOTE: self.capabilities.delayed_quotes,
            ProviderCapability.REALTIME_QUOTE: self.capabilities.realtime_quotes,
            ProviderCapability.TRADE_STREAM: self.capabilities.trade_stream,
            ProviderCapability.BAR_STREAM: self.capabilities.bar_stream,
            ProviderCapability.MARKET_STATUS: self.capabilities.market_status,
            ProviderCapability.PRE_MARKET_DATA: self.capabilities.pre_market,
            ProviderCapability.AFTER_HOURS_DATA: self.capabilities.after_hours,
            ProviderCapability.NEWS: self.capabilities.news,
            ProviderCapability.CORPORATE_ACTIONS: self.capabilities.corporate_actions,
        }
        return cap_map.get(capability, False)

    @abstractmethod
    def get_quote(self, symbol: str) -> Optional[MarketQuote]:
        pass

    @abstractmethod
    def get_historical_ohlcv(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> pd.DataFrame:
        pass

    def get_provider_health(self) -> Dict[str, Any]:
        return self.health.to_dict()
