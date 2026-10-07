import numpy as np
from typing import Dict, Any
from pydantic import BaseModel


class StabilityResult(BaseModel):
    stability_level: str  # HIGH | MEDIUM | LOW
    model_agreement_pct: float
    temporal_variance: float
    regime_consistency: bool
    score: float


class StabilityEngine:
    def calculate_stability(
        self, leaderboard: Dict[str, float], calibrated_probs: np.ndarray, regime_name: str
    ) -> StabilityResult:
        # 1. Model agreement based on OOS leaderboard dispersion
        accuracies = list(leaderboard.values()) if leaderboard else [75.0]
        std_acc = float(np.std(accuracies))
        model_agreement = float(np.clip(100.0 - std_acc * 2.0, 50.0, 100.0))

        # 2. Probability temporal variance
        p_latest = calibrated_probs[-1] if len(calibrated_probs) > 0 else np.array([0.3, 0.4, 0.3])
        p_max = float(np.max(p_latest))
        temporal_var = float(np.var(p_latest))

        # 3. Regime consistency check
        regime_ok = regime_name != "HIGH-VOL CRISIS"

        # Overall Stability Score (0.0 to 1.0)
        overall_score = (model_agreement / 100.0) * 0.5 + (p_max) * 0.3 + (0.2 if regime_ok else 0.0)
        overall_score = float(np.clip(overall_score, 0.0, 1.0))

        if overall_score >= 0.75:
            level = "HIGH"
        elif overall_score >= 0.55:
            level = "MEDIUM"
        else:
            level = "LOW"

        return StabilityResult(
            stability_level=level,
            model_agreement_pct=round(model_agreement, 1),
            temporal_variance=round(temporal_var, 4),
            regime_consistency=regime_ok,
            score=round(overall_score, 2)
        )


stability_engine = StabilityEngine()
