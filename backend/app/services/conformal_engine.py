import numpy as np
from typing import Dict, Any, Optional
from pydantic import BaseModel


class ConformalInterval(BaseModel):
    point_forecast: float
    lower_bound: Optional[float] = None
    upper_bound: Optional[float] = None
    confidence_level: float = 0.95
    empirical_coverage: Optional[float] = None
    interval_width: Optional[float] = None
    status: str = "AVAILABLE"  # AVAILABLE | CONFORMAL UNAVAILABLE


class ConformalEngine:
    """
    Genuine Inductive Conformal Prediction Engine.
    Computes non-conformity scores (residuals) on out-of-fold validation sets.
    Returns CONFORMAL UNAVAILABLE if calibration set is missing or empty.
    """
    def __init__(self, alpha: float = 0.05):
        self.alpha = alpha
        self.q_hat: Optional[float] = None
        self.empirical_coverage: Optional[float] = None
        self.is_calibrated: bool = False

    def calibrate(self, y_val_true: np.ndarray, y_val_pred: np.ndarray) -> "ConformalEngine":
        """
        Calibrates quantile q_hat using true non-conformity residuals.
        """
        if len(y_val_true) == 0 or len(y_val_pred) == 0:
            self.is_calibrated = False
            self.q_hat = None
            self.empirical_coverage = None
            return self

        residuals = np.abs(y_val_true - y_val_pred)
        n = len(residuals)
        if n < 5:  # Require at least 5 residuals for valid conformal calibration
            self.is_calibrated = False
            self.q_hat = None
            self.empirical_coverage = None
            return self

        q_level = np.ceil((n + 1) * (1 - self.alpha)) / n
        q_level = min(1.0, max(0.0, q_level))
        self.q_hat = float(np.quantile(residuals, q_level))

        # Check empirical coverage on calibration set
        covered = np.sum(residuals <= self.q_hat) / n
        self.empirical_coverage = round(float(covered) * 100.0, 1)
        self.is_calibrated = True
        return self

    def predict_interval(self, point_forecast: float) -> ConformalInterval:
        if not self.is_calibrated or self.q_hat is None:
            return ConformalInterval(
                point_forecast=round(point_forecast, 4),
                lower_bound=None,
                upper_bound=None,
                confidence_level=0.95,
                empirical_coverage=None,
                interval_width=None,
                status="CONFORMAL UNAVAILABLE"
            )

        lower = point_forecast - self.q_hat
        upper = point_forecast + self.q_hat
        width = upper - lower

        return ConformalInterval(
            point_forecast=round(point_forecast, 4),
            lower_bound=round(lower, 4),
            upper_bound=round(upper, 4),
            confidence_level=0.95,
            empirical_coverage=self.empirical_coverage,
            interval_width=round(width, 4),
            status="AVAILABLE"
        )
