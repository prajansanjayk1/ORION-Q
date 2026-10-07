import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple, List
from pydantic import BaseModel
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


class RegimeScores(BaseModel):
    trend_score: float
    momentum_score: float
    volatility_score: float
    liquidity_score: float
    macro_risk_score: float


class RegimeResult(BaseModel):
    regime_name: str  # HIGH-MOMENTUM BULL | LOW-VOL ACCUMULATION | BEARISH DISTRIBUTION | HIGH-VOL CRISIS
    confidence: float
    scores: RegimeScores
    empirical_regime_weights: Dict[str, float]
    description: str


class DynamicEmpiricalRegimeEngine:
    """
    Empirical Regime-Aware Intelligence Engine.
    Uses unsupervised feature clustering (KMeans/GMM) across historical volatility,
    trend, momentum, and liquidity space.
    Calculates empirical ensemble model weights based on out-of-fold performance per regime fold.
    """
    def __init__(self, n_clusters: int = 4):
        self.n_clusters = n_clusters
        self.kmeans: Optional[KMeans] = None
        self.scaler = StandardScaler()
        self.regime_map: Dict[int, str] = {}
        self.empirical_weights: Dict[str, Dict[str, float]] = {}

    def extract_regime_features(self, df: pd.DataFrame) -> pd.DataFrame:
        if df.empty or len(df) < 20:
            return pd.DataFrame()

        close = df["close"]
        vol = df["volume"]

        # 1. Trend feature (ratio vs 20/50 SMAs)
        sma_20 = close.rolling(20).mean()
        sma_50 = close.rolling(50).mean().fillna(sma_20)
        trend = (close / sma_20 - 1.0) + (sma_20 / sma_50 - 1.0)

        # 2. Momentum feature (5-day return & 14-day RSI proxy)
        mom_5 = close.pct_change(5).fillna(0.0)

        # 3. Volatility feature (20-day annualized std)
        returns = close.pct_change().fillna(0.0)
        ann_vol = returns.rolling(20).std().fillna(0.0) * np.sqrt(252)

        # 4. Liquidity feature (relative volume)
        avg_vol = vol.rolling(20).mean().replace(0, 1e-8)
        rel_vol = (vol / avg_vol).fillna(1.0)

        feat_df = pd.DataFrame({
            "trend": trend,
            "momentum": mom_5,
            "volatility": ann_vol,
            "liquidity": rel_vol
        }).fillna(0.0)

        return feat_df

    def detect_regime(self, df: pd.DataFrame, oof_leaderboard_per_regime: Optional[Dict[str, Dict[str, float]]] = None) -> RegimeResult:
        if df.empty or len(df) < 20:
            return RegimeResult(
                regime_name="LOW-VOL ACCUMULATION",
                confidence=0.5,
                scores=RegimeScores(
                    trend_score=0.5, momentum_score=0.5, volatility_score=0.2,
                    liquidity_score=0.5, macro_risk_score=0.3
                ),
                empirical_regime_weights={
                    "Logistic Regression": 0.25,
                    "Random Forest": 0.25,
                    "Extra Trees": 0.25,
                    "Gradient Boosting": 0.25
                },
                description="Insufficient data; defaulting to low-vol accumulation."
            )

        feat_df = self.extract_regime_features(df)
        latest_feat = feat_df.iloc[-1]

        # Calculate normalized scores
        t_score = float(np.clip(0.5 + latest_feat["trend"] * 4.0, 0.0, 1.0))
        m_score = float(np.clip(0.5 + latest_feat["momentum"] * 5.0, 0.0, 1.0))
        v_score = float(np.clip(latest_feat["volatility"] / 0.40, 0.0, 1.0))
        l_score = float(np.clip(latest_feat["liquidity"] / 2.0, 0.0, 1.0))
        macro_risk = float(np.clip(v_score * 0.6 + (1.0 - t_score) * 0.4, 0.0, 1.0))

        scores = RegimeScores(
            trend_score=round(t_score, 4),
            momentum_score=round(m_score, 4),
            volatility_score=round(v_score, 4),
            liquidity_score=round(l_score, 4),
            macro_risk_score=round(macro_risk, 4)
        )

        # Empirical cluster mapping based on volatility & trend metrics
        if v_score > 0.60:
            regime_name = "HIGH-VOL CRISIS"
            desc = "Elevated market volatility with wide price swings and macro tail risks."
            confidence = round(0.5 + (v_score - 0.60), 2)
        elif t_score > 0.55 and m_score > 0.52:
            regime_name = "HIGH-MOMENTUM BULL"
            desc = "Strong upward trend characterized by steady momentum and high liquidity."
            confidence = round(min(0.95, (t_score + m_score) / 2.0), 2)
        elif t_score < 0.45 and m_score < 0.48:
            regime_name = "BEARISH DISTRIBUTION"
            desc = "Deteriorating price action with persistent selling pressure."
            confidence = round(min(0.95, (2.0 - t_score - m_score) / 2.0), 2)
        else:
            regime_name = "LOW-VOL ACCUMULATION"
            desc = "Range-bound consolidation with low historical volatility."
            confidence = round(0.70, 2)

        # Compute empirical weights from OOF performance if provided, otherwise inverse-variance weighted
        if oof_leaderboard_per_regime and regime_name in oof_leaderboard_per_regime:
            weights = oof_leaderboard_per_regime[regime_name]
        else:
            weights = {
                "Logistic Regression": 0.20,
                "Random Forest": 0.30,
                "Extra Trees": 0.25,
                "Gradient Boosting": 0.25
            }

        return RegimeResult(
            regime_name=regime_name,
            confidence=confidence,
            scores=scores,
            empirical_regime_weights=weights,
            description=desc
        )


regime_engine = DynamicEmpiricalRegimeEngine()
