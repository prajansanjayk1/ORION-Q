import pandas as pd
import numpy as np
from typing import Tuple


def construct_targets(df: pd.DataFrame, horizon: int = 5, upper_threshold: float = 0.01, lower_threshold: float = -0.01) -> pd.DataFrame:
    """
    Construct leakage-safe prediction targets:
    - future_return: Percentage return over next `horizon` bars.
    - target_class: 2 (BULLISH), 1 (NEUTRAL), 0 (BEARISH).
    
    Target generation uses strictly shifted prices.
    """
    df = df.copy()
    if "close" not in df.columns:
        raise ValueError("DataFrame must contain 'close' column")

    # Shift close price into the future for target calculation
    future_close = df["close"].shift(-horizon)
    df["future_return"] = (future_close - df["close"]) / df["close"]

    # Assign classification targets
    conditions = [
        (df["future_return"] > upper_threshold),
        (df["future_return"] < lower_threshold)
    ]
    choices = [2, 0]  # 2: BULLISH, 0: BEARISH
    df["target_class"] = np.select(conditions, choices, default=1)  # 1: NEUTRAL

    return df
