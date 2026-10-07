import numpy as np
from typing import Dict, Any
from pydantic import BaseModel
from backend.app.services.conformal_engine import ConformalInterval
from backend.app.services.stability_engine import StabilityResult


class SignalOutput(BaseModel):
    signal: str  # STRONG BUY | BUY | HOLD | NO TRADE | SELL | STRONG SELL
    calibrated_probability: float
    expected_return_pct: float
    conformal_range: Dict[str, float]
    regime_name: str
    stability_level: str
    rationale: str


class SignalEngine:
    def generate_signal(
        self,
        calibrated_probs: np.ndarray,
        expected_return: float,
        conformal_interval: ConformalInterval,
        regime_name: str,
        stability: StabilityResult
    ) -> SignalOutput:
        # Extracted probabilities: [P_bear, P_neut, P_bull]
        if len(calibrated_probs.shape) > 1:
            latest_p = calibrated_probs[-1]
        else:
            latest_p = calibrated_probs

        if len(latest_p) == 3:
            p_bear, p_neut, p_bull = float(latest_p[0]), float(latest_p[1]), float(latest_p[2])
        else:
            p_bull = float(latest_p[1]) if len(latest_p) > 1 else float(latest_p[0])
            p_bear = 1.0 - p_bull

        ret_pct = float(expected_return * 100.0)
        c_width = conformal_interval.interval_width

        # NO TRADE triggers: High Vol Crisis OR Low Stability OR Excessive Conformal Interval Width
        if regime_name == "HIGH-VOL CRISIS":
            signal = "NO TRADE"
            rationale = "Market in High-Vol Crisis regime. Risk engine suspended long entry."
        elif stability.stability_level == "LOW":
            signal = "NO TRADE"
            rationale = "Low prediction stability across Parliament models."
        elif c_width > 0.15:  # Interval width > 15% return uncertainty
            signal = "NO TRADE"
            rationale = f"Conformal uncertainty range too wide ({c_width*100:.1f}%)."
        
        # Directive Classification Rules
        elif p_bull >= 0.65 and ret_pct > 1.5:
            signal = "STRONG BUY"
            rationale = f"High calibrated bullish probability ({p_bull*100:.1f}%) with positive forecast return ({ret_pct:+.2f}%)."
        elif p_bull >= 0.52 and ret_pct > 0.3:
            signal = "BUY"
            rationale = f"Moderate bullish probability ({p_bull*100:.1f}%) and positive expected return."
        elif p_bear >= 0.65 and ret_pct < -1.5:
            signal = "STRONG SELL"
            rationale = f"Elevated bearish probability ({p_bear*100:.1f}%) and negative return projection ({ret_pct:+.2f}%)."
        elif p_bear >= 0.52 and ret_pct < -0.3:
            signal = "SELL"
            rationale = f"Moderate bearish probability ({p_bear*100:.1f}%) with negative forecast return."
        else:
            signal = "HOLD"
            rationale = f"Neutral market probability distribution ({p_bull*100:.1f}% Bullish / {p_bear*100:.1f}% Bearish)."

        return SignalOutput(
            signal=signal,
            calibrated_probability=round(p_bull, 4),
            expected_return_pct=round(ret_pct, 2),
            conformal_range={
                "lower_bound_pct": round(conformal_interval.lower_bound * 100.0, 2),
                "upper_bound_pct": round(conformal_interval.upper_bound * 100.0, 2),
                "empirical_coverage": conformal_interval.empirical_coverage
            },
            regime_name=regime_name,
            stability_level=stability.stability_level,
            rationale=rationale
        )


signal_engine = SignalEngine()
