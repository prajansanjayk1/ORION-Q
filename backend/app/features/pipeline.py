import pandas as pd
import numpy as np
from typing import List


def compute_rsi(series: pd.Series, period: int = 14) -> pd.Series:
    delta = series.diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
    rs = gain / (loss + 1e-8)
    return 100 - (100 / (1 + rs))


def compute_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
    high_low = df["high"] - df["low"]
    high_close = (df["high"] - df["close"].shift(1)).abs()
    low_close = (df["low"] - df["close"].shift(1)).abs()
    tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
    return tr.rolling(window=period).mean()


def compute_obv(df: pd.DataFrame) -> pd.Series:
    close_diff = df["close"].diff()
    direction = np.where(close_diff > 0, 1, np.where(close_diff < 0, -1, 0))
    return (direction * df["volume"]).cumsum()


class FeaturePipeline:
    @staticmethod
    def extract_features(df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 30:
            return pd.DataFrame()

        data = df.copy()
        data = data.sort_values("timestamp").reset_index(drop=True)

        # 1. Price Returns & Gaps
        data["return_1d"] = data["close"].pct_change(1)
        data["return_3d"] = data["close"].pct_change(3)
        data["return_5d"] = data["close"].pct_change(5)
        data["return_10d"] = data["close"].pct_change(10)
        data["return_21d"] = data["close"].pct_change(21)
        data["log_return"] = np.log(data["close"] / data["close"].shift(1))
        data["gap"] = (data["open"] - data["close"].shift(1)) / data["close"].shift(1)
        data["range_pct"] = (data["high"] - data["low"]) / data["close"]

        # 2. Momentum Indicators
        data["rsi_14"] = compute_rsi(data["close"], 14)
        data["rsi_accel"] = data["rsi_14"] - data["rsi_14"].shift(3)
        data["roc_5"] = (data["close"] - data["close"].shift(5)) / data["close"].shift(5)
        data["roc_21"] = (data["close"] - data["close"].shift(21)) / data["close"].shift(21)

        # 3. Moving Averages & Trend
        data["sma_10"] = data["close"].rolling(10).mean()
        data["sma_20"] = data["close"].rolling(20).mean()
        data["sma_50"] = data["close"].rolling(50).mean()
        data["ema_12"] = data["close"].ewm(span=12, adjust=False).mean()
        data["ema_26"] = data["close"].ewm(span=26, adjust=False).mean()
        
        data["dist_sma10"] = (data["close"] / data["sma_10"]) - 1.0
        data["dist_sma20"] = (data["close"] / data["sma_20"]) - 1.0
        data["dist_sma50"] = (data["close"] / data["sma_50"]) - 1.0
        
        data["macd"] = data["ema_12"] - data["ema_26"]
        data["macd_signal"] = data["macd"].ewm(span=9, adjust=False).mean()
        data["macd_hist"] = data["macd"] - data["macd_signal"]

        # 4. Volatility Features
        data["atr_14"] = compute_atr(data, 14)
        data["volatility_ratio"] = data["atr_14"] / data["close"]
        data["realized_vol_21"] = data["log_return"].rolling(21).std() * np.sqrt(252)

        # 5. Volume Indicators
        data["volume_change"] = data["volume"].pct_change(1)
        data["rel_volume_20"] = data["volume"] / (data["volume"].rolling(20).mean() + 1e-8)
        vol_mean_20 = data["volume"].rolling(20).mean()
        vol_std_20 = data["volume"].rolling(20).std() + 1e-8
        data["volume_zscore"] = (data["volume"] - vol_mean_20) / vol_std_20
        data["obv"] = compute_obv(data)

        # 6. Sentiment & Macro Placeholders (Real values populated when news/macro attached)
        if "sentiment_score" not in data.columns:
            data["sentiment_score"] = 0.0
        if "market_index_return" not in data.columns:
            data["market_index_return"] = data["return_1d"].rolling(5).mean().fillna(0.0)

        # Drop NaN values introduced by rolling windows
        feature_cols = [
            "return_1d", "return_3d", "return_5d", "return_10d", "return_21d",
            "log_return", "gap", "range_pct", "rsi_14", "rsi_accel", "roc_5", "roc_21",
            "dist_sma10", "dist_sma20", "dist_sma50", "macd", "macd_signal", "macd_hist",
            "atr_14", "volatility_ratio", "realized_vol_21", "volume_change",
            "rel_volume_20", "volume_zscore", "sentiment_score", "market_index_return"
        ]

        data = data.dropna(subset=feature_cols).reset_index(drop=True)
        return data, feature_cols
