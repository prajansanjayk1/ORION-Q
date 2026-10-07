import pytz
from datetime import datetime
from typing import Optional, Dict, Any
import pandas as pd
from backend.app.schemas.market import MarketQuote, MarketBar, DataState
from backend.app.core.currencies import get_currency_for_exchange


class DataNormalizer:
    """Ensures all market data is in a consistent, normalized format."""

    @staticmethod
    def normalize_quote(quote: MarketQuote) -> MarketQuote:
        """Normalizes a quote to ensure consistent field values."""
        # Ensure currency is set
        if not quote.currency:
            quote.currency = get_currency_for_exchange(quote.exchange)

        # Ensure asset_type has a default
        if not quote.asset_type:
            quote.asset_type = "equity"

        # Normalize symbol (uppercase, strip whitespace)
        quote.symbol = quote.symbol.upper().strip()
        quote.exchange = quote.exchange.upper().strip()

        # Set source from provider_name if not set
        if not quote.source:
            quote.source = quote.provider_name

        return quote

    @staticmethod
    def normalize_timestamp(timestamp: float, target_tz: str = "UTC") -> str:
        """Converts epoch timestamp to ISO format in target timezone."""
        dt = datetime.fromtimestamp(timestamp, tz=pytz.UTC)
        target = pytz.timezone(target_tz)
        return dt.astimezone(target).isoformat()

    @staticmethod
    def normalize_historical_dataframe(df: pd.DataFrame) -> pd.DataFrame:
        """Normalizes a historical OHLCV DataFrame."""
        if df.empty:
            return df

        # Ensure required columns exist
        required = ["timestamp", "open", "high", "low", "close", "volume"]
        for col in required:
            if col not in df.columns:
                df[col] = None

        # Sort by timestamp
        df = df.sort_values("timestamp").reset_index(drop=True)

        # Remove exact duplicates by timestamp
        df = df.drop_duplicates(subset=["timestamp"], keep="last")

        # Ensure numeric types
        for col in ["open", "high", "low", "close", "volume"]:
            df[col] = pd.to_numeric(df[col], errors="coerce")

        return df

    @staticmethod
    def detect_adjusted_prices(df: pd.DataFrame) -> bool:
        """Heuristic to detect if prices appear to be adjusted for splits.
        Returns True if prices look adjusted (e.g., very small values relative to volume)."""
        if df.empty or "close" not in df.columns:
            return False
        # If there's a large price discontinuity, prices may be unadjusted
        returns = df["close"].pct_change().dropna()
        if returns.empty:
            return False
        # A return > 50% or < -50% may indicate a split in unadjusted data
        extreme_moves = (returns.abs() > 0.5).sum()
        return extreme_moves == 0  # If no extreme moves, likely adjusted
