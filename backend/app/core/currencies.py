"""
Currency registry, formatting, and caching system for ORION-Q.
"""

from typing import Dict, Optional, Tuple
from datetime import datetime, timezone
import pytz

# Mapping of exchange codes to base currency codes
EXCHANGE_CURRENCY_MAP = {
    "NSE": "INR",
    "BSE": "INR",
    "NYSE": "USD",
    "NASDAQ": "USD",
    "LSE": "GBP",
    "TSE": "JPY",
    "HKEX": "HKD"
}

# Mapping of currency codes to display symbols
CURRENCY_SYMBOLS = {
    "INR": "₹",
    "USD": "$",
    "GBP": "£",
    "JPY": "¥",
    "HKD": "HK$"
}

# Standard decimal places for each currency
CURRENCY_DECIMAL_PLACES = {
    "INR": 2,
    "USD": 2,
    "GBP": 2,
    "JPY": 0,
    "HKD": 2
}

def get_currency_for_exchange(exchange: str) -> str:
    """Returns the base currency code for a given exchange."""
    return EXCHANGE_CURRENCY_MAP.get(exchange.upper(), "USD")

def get_currency_symbol(currency_code: str) -> str:
    """Returns the display symbol for a given currency code."""
    return CURRENCY_SYMBOLS.get(currency_code.upper(), "$")

def format_price(price: Optional[float], exchange: str) -> str:
    """Formats a price with the correct currency symbol and decimal places."""
    if price is None:
        return "—"
    currency = get_currency_for_exchange(exchange)
    symbol = get_currency_symbol(currency)
    decimals = CURRENCY_DECIMAL_PLACES.get(currency, 2)
    return f"{symbol}{price:,.{decimals}f}"

def format_change(change: float, exchange: str) -> str:
    """Formats a price change with the correct currency symbol, decimal places, and sign."""
    currency = get_currency_for_exchange(exchange)
    symbol = get_currency_symbol(currency)
    decimals = CURRENCY_DECIMAL_PLACES.get(currency, 2)
    sign = "+" if change > 0 else ""
    return f"{sign}{symbol}{change:,.{decimals}f}"

def format_percent(percent: float) -> str:
    """Formats a percentage with sign and 2 decimal places."""
    sign = "+" if percent > 0 else ""
    return f"{sign}{percent:,.2f}%"

class FXRateCache:
    """
    In-memory cache for foreign exchange rates.
    Rates are injected by the ingestion layer.
    """
    def __init__(self):
        # Format: { "USD_INR": (rate, datetime_object) }
        self._rates: Dict[str, Tuple[float, datetime]] = {}

    def _get_key(self, from_currency: str, to_currency: str) -> str:
        return f"{from_currency.upper()}_{to_currency.upper()}"

    def update_rate(self, from_currency: str, to_currency: str, rate: float) -> None:
        """Stores or updates the rate with the current timestamp."""
        key = self._get_key(from_currency, to_currency)
        self._rates[key] = (rate, datetime.now(timezone.utc))

    def get_rate(self, from_currency: str, to_currency: str) -> Optional[Tuple[float, str]]:
        """
        Returns a tuple of (rate, iso_timestamp) if available.
        """
        if from_currency.upper() == to_currency.upper():
            return 1.0, datetime.now(timezone.utc).isoformat()

        key = self._get_key(from_currency, to_currency)
        if key in self._rates:
            rate, timestamp = self._rates[key]
            return rate, timestamp.isoformat()
        
        # Check reverse rate as fallback
        reverse_key = self._get_key(to_currency, from_currency)
        if reverse_key in self._rates:
            rate, timestamp = self._rates[reverse_key]
            return 1.0 / rate, timestamp.isoformat()

        return None

    def convert(self, amount: float, from_currency: str, to_currency: str) -> Optional[Dict]:
        """
        Converts amount and returns dict with result, rate, and timestamp.
        """
        if from_currency.upper() == to_currency.upper():
            return {
                "converted_amount": amount,
                "rate": 1.0,
                "rate_timestamp": datetime.now(timezone.utc).isoformat()
            }

        rate_info = self.get_rate(from_currency, to_currency)
        if rate_info is None:
            return None

        rate, timestamp = rate_info
        return {
            "converted_amount": amount * rate,
            "rate": rate,
            "rate_timestamp": timestamp
        }

    def is_rate_stale(self, from_currency: str, to_currency: str, max_age_seconds: int = 3600) -> bool:
        """
        Returns True if the rate is older than max_age_seconds or missing.
        """
        key = self._get_key(from_currency, to_currency)
        rate_entry = self._rates.get(key)
        
        if rate_entry is None:
            reverse_key = self._get_key(to_currency, from_currency)
            rate_entry = self._rates.get(reverse_key)
            if rate_entry is None:
                return True

        _, timestamp = rate_entry
        age = (datetime.now(timezone.utc) - timestamp).total_seconds()
        return age > max_age_seconds
