import pytest
import pandas as pd
import numpy as np
from backend.app.ml.targets import construct_targets
from backend.app.ml.preprocessing import LeakageSafePreprocessor, create_chronological_splits
from backend.app.features.pipeline import FeaturePipeline


def test_leakage_target_construction():
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "open": np.linspace(100, 200, 100),
        "high": np.linspace(102, 202, 100),
        "low": np.linspace(98, 198, 100),
        "close": np.linspace(100, 200, 100),
        "volume": np.full(100, 1000)
    })

    targeted = construct_targets(df, horizon=5)
    
    # Assert future_return uses future shifted close
    # At row 0, close = 100, at row 5, close = 105.0505...
    # Return at index 0 should equal (close[5] - close[0]) / close[0]
    expected_ret = (df.loc[5, "close"] - df.loc[0, "close"]) / df.loc[0, "close"]
    assert np.isclose(targeted.loc[0, "future_return"], expected_ret)

    # Last 5 rows must have NaN target due to shift
    assert targeted["future_return"].tail(5).isna().all()


def test_leakage_preprocessor_fitting():
    dates = pd.date_range("2024-01-01", periods=100, freq="D")
    df = pd.DataFrame({
        "timestamp": dates,
        "open": np.random.randn(100) + 100,
        "high": np.random.randn(100) + 102,
        "low": np.random.randn(100) + 98,
        "close": np.random.randn(100) + 100,
        "volume": np.random.randint(1000, 5000, 100)
    })

    df_feat, feature_cols = FeaturePipeline.extract_features(df)
    train_df, val_df, test_df = create_chronological_splits(df_feat, train_ratio=0.7, val_ratio=0.15)

    preprocessor = LeakageSafePreprocessor()
    preprocessor.fit(train_df, feature_cols)

    assert preprocessor.is_fitted
    # Scaler mean/scale parameters must be derived ONLY from train set length
    assert len(preprocessor.scaler.center_) == len(preprocessor.selected_features)

    # Transforming val_df should use pre-fitted scaler parameters without modifying scaler
    val_scaled = preprocessor.transform(val_df)
    assert val_scaled.shape[1] == len(preprocessor.selected_features)
