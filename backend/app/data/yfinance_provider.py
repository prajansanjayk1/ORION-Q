import time
from typing import List, Optional
import yfinance as yf
import pandas as pd
from backend.app.data.provider_adapter import BaseMarketDataProvider
from backend.app.schemas.market import ProviderCapability, ProviderCapabilities, MarketQuote, DataState, LatencyAudit, MarketSessionState
from backend.app.services.market_session_engine import market_session_engine


class YFinanceProvider(BaseMarketDataProvider):
    @property
    def provider_name(self) -> str:
        return "yfinance"

    @property
    def capabilities(self) -> ProviderCapabilities:
        return ProviderCapabilities(
            historical=True,
            delayed_quotes=True,
            market_status=True,
            corporate_actions=True
        )

    def _resolve_yf_symbol(self, symbol: str) -> str:
        symbol_upper = symbol.upper().strip()
        # Map common Indian tickers to .NS suffix for Yahoo Finance API
        indian_tickers = {
            "RELIANCE": "RELIANCE.NS",
            "TCS": "TCS.NS",
            "INFY": "INFY.NS",
            "HDFCBANK": "HDFCBANK.NS",
            "ICICIBANK": "ICICIBANK.NS",
            "BHARTIARTL": "BHARTIARTL.NS",
            "ITC": "ITC.NS",
            "SBIN": "SBIN.NS",
            "LTIM": "LTIM.NS",
            "TATAMOTORS": "TATAMOTORS.NS"
        }
        return indian_tickers.get(symbol_upper, symbol_upper)

    def _determine_exchange(self, symbol: str) -> str:
        symbol_upper = symbol.upper()
        if symbol_upper.endswith(".NS") or symbol_upper.endswith(".BO") or symbol_upper in ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"]:
            return "NSE"
        if symbol_upper in ["^NSEI", "^BSESN", "^NSEBANK", "^INDIAVIX"]:
            return "NSE"
        return "NASDAQ"  # Default US exchange for AAPL, NVDA, SPY, etc.

    def get_quote(self, symbol: str) -> Optional[MarketQuote]:
        ingestion_ts = time.time()
        raw_symbol = symbol.upper().strip()
        yf_symbol = self._resolve_yf_symbol(raw_symbol)
        exchange = self._determine_exchange(raw_symbol)
        session_info = market_session_engine.get_session(exchange)

        is_market_closed = session_info.status in [MarketSessionState.CLOSED, MarketSessionState.HOLIDAY]

        try:
            ticker = yf.Ticker(yf_symbol)
            fast_info = ticker.fast_info

            price = fast_info.get("lastPrice") or fast_info.get("regularMarketPrice")
            prev_close = fast_info.get("previousClose") or fast_info.get("regularMarketPreviousClose")

            # If price is missing or market is closed, fetch latest historical OHLCV bar
            if price is None or prev_close is None or price <= 0 or is_market_closed:
                hist = ticker.history(period="7d")
                if hist.empty:
                    return None

                latest = hist.iloc[-1]
                price = float(latest["Close"])
                prev_close = float(hist.iloc[-2]["Close"]) if len(hist) > 1 else price
                open_p = float(latest["Open"])
                high_p = float(latest["High"])
                low_p = float(latest["Low"])
                volume = float(latest["Volume"])

                if hasattr(latest.name, "timestamp"):
                    provider_ts = latest.name.timestamp()
                else:
                    provider_ts = time.time()
            else:
                price = float(price)
                prev_close = float(prev_close)
                open_p = float(fast_info.get("open", price))
                high_p = float(fast_info.get("dayHigh", price))
                low_p = float(fast_info.get("dayLow", price))
                volume = float(fast_info.get("lastVolume", 0))
                provider_ts = fast_info.get("last_trade_time") or time.time()

            change = price - prev_close
            percent_change = (change / prev_close * 100.0) if prev_close > 0 else 0.0

            data_state = DataState.CLOSED if is_market_closed else DataState.DELAYED

            processing_ts = time.time()
            latency = LatencyAudit(
                provider_timestamp=float(provider_ts),
                ingestion_timestamp=ingestion_ts,
                processing_timestamp=processing_ts,
                latency_ms=round((processing_ts - ingestion_ts) * 1000, 2)
            )

            return MarketQuote(
                symbol=raw_symbol,
                exchange=exchange,
                price=round(price, 2),
                change=round(change, 2),
                percent_change=round(percent_change, 2),
                open=round(open_p, 2),
                high=round(high_p, 2),
                low=round(low_p, 2),
                previous_close=round(prev_close, 2),
                volume=round(volume, 0),
                timestamp=processing_ts,
                data_state=data_state,
                provider_name=self.provider_name,
                latency_audit=latency
            )

        except Exception as e:
            try:
                ticker = yf.Ticker(yf_symbol)
                hist = ticker.history(period="7d")
                if hist.empty:
                    return None

                latest = hist.iloc[-1]
                price = float(latest["Close"])
                prev_close = float(hist.iloc[-2]["Close"]) if len(hist) > 1 else price
                change = price - prev_close
                percent_change = (change / prev_close * 100.0) if prev_close > 0 else 0.0

                processing_ts = time.time()
                return MarketQuote(
                    symbol=raw_symbol,
                    exchange=exchange,
                    price=round(price, 2),
                    change=round(change, 2),
                    percent_change=round(percent_change, 2),
                    open=round(float(latest["Open"]), 2),
                    high=round(float(latest["High"]), 2),
                    low=round(float(latest["Low"]), 2),
                    previous_close=round(prev_close, 2),
                    volume=round(float(latest["Volume"]), 0),
                    timestamp=processing_ts,
                    data_state=DataState.CLOSED,
                    provider_name=self.provider_name,
                    latency_audit=LatencyAudit(
                        provider_timestamp=processing_ts,
                        ingestion_timestamp=ingestion_ts,
                        processing_timestamp=processing_ts,
                        latency_ms=0.0
                    )
                )
            except Exception:
                return None

    def get_historical_ohlcv(
        self, symbol: str, period: str = "1y", interval: str = "1d"
    ) -> pd.DataFrame:
        try:
            yf_symbol = self._resolve_yf_symbol(symbol)
            ticker = yf.Ticker(yf_symbol)
            df = ticker.history(period=period, interval=interval)
            if df.empty:
                return pd.DataFrame()

            df = df.reset_index()
            df = df.rename(columns={
                "Date": "timestamp",
                "Datetime": "timestamp",
                "Open": "open",
                "High": "high",
                "Low": "low",
                "Close": "close",
                "Volume": "volume"
            })

            if "timestamp" in df.columns:
                df["timestamp"] = pd.to_datetime(df["timestamp"])
                df = df.sort_values("timestamp").reset_index(drop=True)

            required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
            existing_cols = [c for c in required_cols if c in df.columns]
            return df[existing_cols]

        except Exception:
            return pd.DataFrame()
