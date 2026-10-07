import pandas as pd
from typing import Dict, List, Tuple, Any
from backend.app.schemas.market import MarketQuote, DataQualityScore

class DataQualityChecker:
    @staticmethod
    def validate_quote(quote: MarketQuote) -> Tuple[bool, List[str]]:
        errors = []
        if quote.price <= 0:
            errors.append(f"Invalid price: {quote.price}")
        if quote.high < quote.low:
            errors.append(f"High ({quote.high}) < Low ({quote.low})")
        if quote.volume < 0:
            errors.append(f"Negative volume: {quote.volume}")
        
        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def validate_ohlcv_dataframe(df: pd.DataFrame) -> Tuple[bool, List[str]]:
        errors = []
        if df.empty:
            return False, ["DataFrame is empty"]

        required_cols = ["timestamp", "open", "high", "low", "close", "volume"]
        missing_cols = [c for c in required_cols if c not in df.columns]
        if missing_cols:
            return False, [f"Missing required columns: {missing_cols}"]

        # Check for NaNs
        nan_counts = df[required_cols].isna().sum()
        for col, count in nan_counts.items():
            if count > 0:
                errors.append(f"Column '{col}' has {count} missing values")

        # Check timestamp ordering
        if not df["timestamp"].is_monotonic_increasing:
            errors.append("Timestamps are not strictly ascending")

        # Check timestamp duplicates
        duplicates = df["timestamp"].duplicated().sum()
        if duplicates > 0:
            errors.append(f"Found {duplicates} duplicate timestamps")

        # High/Low check
        invalid_hl = (df["high"] < df["low"]).sum()
        if invalid_hl > 0:
            errors.append(f"Found {invalid_hl} rows where High < Low")

        is_valid = len(errors) == 0
        return is_valid, errors

    @staticmethod
    def validate_ohlc_consistency(open: float, high: float, low: float, close: float) -> Tuple[bool, List[str]]:
        errors = []
        if open < 0 or high < 0 or low < 0 or close < 0:
            errors.append("Negative prices found")
        if close > high:
            errors.append("Close > High")
        if open < low:
            errors.append("Open < Low")
        if high < low:
            errors.append("High < Low")
        return len(errors) == 0, errors

    @staticmethod
    def detect_zero_volume_type(volume: float) -> str:
        if pd.isna(volume):
            return 'MISSING_VOLUME'
        if volume == 0:
            return 'ZERO_VOLUME'
        if volume < 0:
            return 'UNKNOWN_VOLUME'
        return 'VALID_VOLUME'

    @staticmethod
    def detect_data_gaps(df: pd.DataFrame, expected_interval_minutes: int) -> List[Dict]:
        gaps = []
        if df.empty or 'timestamp' not in df.columns:
            return gaps
        
        # Convert to datetime if it's not already
        timestamps = pd.to_datetime(df['timestamp'])
        diffs = timestamps.diff().dt.total_seconds() / 60.0
        
        # Find where diff > expected_interval_minutes (with a small margin for error, say 1 minute)
        gap_indices = diffs[diffs > expected_interval_minutes + 1].index
        
        for idx in gap_indices:
            expected_at = (timestamps[idx - 1] + pd.Timedelta(minutes=expected_interval_minutes)).isoformat()
            actual_next = timestamps[idx].isoformat()
            gap_minutes = diffs[idx]
            gaps.append({
                "expected_at": expected_at,
                "actual_next": actual_next,
                "gap_minutes": gap_minutes
            })
        return gaps

    @staticmethod
    def check_incomplete_bar(bar_dict: Dict) -> Tuple[bool, List[str]]:
        missing_fields = []
        for field in ["open", "high", "low", "close", "volume"]:
            val = bar_dict.get(field)
            if val is None or pd.isna(val):
                missing_fields.append(field)
        return len(missing_fields) == 0, missing_fields

    @staticmethod
    def calculate_data_quality_score(quote: MarketQuote, historical_df: pd.DataFrame, model_health_status: Dict) -> DataQualityScore:
        import time
        
        feed_freshness = 100.0
        if quote and quote.timestamp:
            age = time.time() - quote.timestamp
            feed_freshness = max(0.0, 100.0 - (age / 60.0))
            
        historical_coverage = 100.0
        feature_completeness = 100.0
        if historical_df is not None and not historical_df.empty:
            historical_coverage = 100.0 # Placeholder logic for coverage
            nan_count = historical_df.isna().sum().sum()
            total_elements = historical_df.size
            if total_elements > 0:
                feature_completeness = max(0.0, 100.0 * (1 - nan_count / total_elements))

        news_freshness = 50.0
        market_liquidity = 100.0
        
        model_health = model_health_status.get("health_score", 50.0) if model_health_status else 50.0
        
        overall = (feed_freshness + historical_coverage + feature_completeness + news_freshness + market_liquidity + model_health) / 6.0
        
        return DataQualityScore(
            overall_score=overall,
            feed_freshness=feed_freshness,
            historical_coverage=historical_coverage,
            feature_completeness=feature_completeness,
            news_freshness=news_freshness,
            market_liquidity=market_liquidity,
            model_health=model_health
        )
