import numpy as np
import pandas as pd
from typing import List, Dict, Any
from pydantic import BaseModel


class FlipFactor(BaseModel):
    feature_name: str
    current_value: float
    required_direction: str  # INCREASE | DECREASE
    sensitivity_score: float
    description: str


class CounterfactualResult(BaseModel):
    current_prediction: str
    target_flip_signal: str
    flip_factors: List[FlipFactor]


class CounterfactualEngine:
    def analyze_counterfactuals(
        self, current_signal: str, X_sample: np.ndarray, feature_names: List[str]
    ) -> CounterfactualResult:
        if len(feature_names) == 0 or X_sample.shape[1] != len(feature_names):
            return CounterfactualResult(
                current_prediction=current_signal,
                target_flip_signal="NEUTRAL",
                flip_factors=[]
            )

        sample = X_sample[-1]

        # Identify key features sensitive to signal reversal (e.g. RSI, Volatility, Dist SMA)
        flip_candidates = ["rsi_14", "volatility_ratio", "macd_hist", "dist_sma20", "volume_zscore"]
        factors = []

        target_flip = "BEARISH" if "BUY" in current_signal else "BULLISH"

        for idx, feat in enumerate(feature_names):
            if feat in flip_candidates:
                val = float(sample[idx])
                if "BUY" in current_signal:
                    req_dir = "DECREASE" if feat in ["rsi_14", "macd_hist"] else "INCREASE"
                    desc = f"A drop in {feat.upper()} below key threshold would trigger signal downgrade."
                else:
                    req_dir = "INCREASE" if feat in ["rsi_14", "macd_hist"] else "DECREASE"
                    desc = f"An expansion in {feat.upper()} above key threshold would flip signal to Bullish."

                factors.append(FlipFactor(
                    feature_name=feat,
                    current_value=round(val, 2),
                    required_direction=req_dir,
                    sensitivity_score=round(float(np.abs(val) * 0.5 + 0.5), 2),
                    description=desc
                ))

        return CounterfactualResult(
            current_prediction=current_signal,
            target_flip_signal=target_flip,
            flip_factors=factors[:4]
        )


counterfactual_engine = CounterfactualEngine()
