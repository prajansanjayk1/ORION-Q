import numpy as np
import pandas as pd
from typing import List, Dict, Any
from pydantic import BaseModel


class FeatureDriver(BaseModel):
    feature_name: str
    impact: float
    direction: str  # POSITIVE | NEGATIVE
    description: str


class ExplainabilityResult(BaseModel):
    top_positive_drivers: List[FeatureDriver]
    top_negative_drivers: List[FeatureDriver]


class ExplainabilityEngine:
    def explain_prediction(
        self, model, X_sample: np.ndarray, feature_names: List[str]
    ) -> ExplainabilityResult:
        if len(feature_names) == 0 or X_sample.shape[1] != len(feature_names):
            return ExplainabilityResult(top_positive_drivers=[], top_negative_drivers=[])

        # Calculate empirical feature importances & sample feature deviations
        sample = X_sample[-1]
        
        # Use model feature importances if available, else linear coefficients
        if hasattr(model, "clf_rf") and hasattr(model.clf_rf, "feature_importances_"):
            importances = model.clf_rf.feature_importances_
        else:
            importances = np.ones(len(feature_names)) / len(feature_names)

        drivers = []
        for feat, val, imp in zip(feature_names, sample, importances):
            impact = float(val * imp)
            direction = "POSITIVE" if impact >= 0 else "NEGATIVE"
            desc = f"{feat.replace('_', ' ').title()} ({val:+.2f}) contributing to {direction.lower()} signal trajectory."
            drivers.append(FeatureDriver(
                feature_name=feat,
                impact=round(impact, 4),
                direction=direction,
                description=desc
            ))

        # Sort by absolute impact
        pos_drivers = sorted([d for d in drivers if d.direction == "POSITIVE"], key=lambda x: abs(x.impact), reverse=True)[:4]
        neg_drivers = sorted([d for d in drivers if d.direction == "NEGATIVE"], key=lambda x: abs(x.impact), reverse=True)[:4]

        return ExplainabilityResult(
            top_positive_drivers=pos_drivers,
            top_negative_drivers=neg_drivers
        )


explainability_engine = ExplainabilityEngine()
