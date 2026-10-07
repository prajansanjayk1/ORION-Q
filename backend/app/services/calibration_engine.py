import numpy as np
from typing import Dict, Any, Tuple, Optional
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import brier_score_loss


class ProbabilityCalibrationEngine:
    """
    Empirical Probability Calibration Engine.
    Applies Platt scaling / multinomial logistic regression to raw out-of-fold ensemble probabilities.
    Calculates empirical Expected Calibration Error (ECE) and Brier Score.
    """
    def __init__(self, method: str = "platt"):
        self.method = method
        self.calibrator = None
        self.brier_score: Optional[float] = None
        self.ece: Optional[float] = None
        self.is_fitted: bool = False

    def fit(self, raw_probs: np.ndarray, y_true: np.ndarray) -> "ProbabilityCalibrationEngine":
        """
        Fits calibration model on validation set out-of-fold probabilities.
        """
        if len(raw_probs) == 0 or len(y_true) == 0:
            self.is_fitted = False
            return self

        if len(raw_probs.shape) == 1:
            raw_probs_2d = np.column_stack([1 - raw_probs, raw_probs])
        else:
            raw_probs_2d = raw_probs

        if len(np.unique(y_true)) < 2:
            self.is_fitted = False
            return self

        try:
            self.calibrator = LogisticRegression(C=1.0, solver="lbfgs", max_iter=500)
            self.calibrator.fit(raw_probs_2d, y_true)

            # Compute calibrated probabilities
            calibrated = self.calibrator.predict_proba(raw_probs_2d)

            # Compute Brier score
            if calibrated.shape[1] == 2:
                self.brier_score = float(brier_score_loss((y_true == 2).astype(int), calibrated[:, 1]))
            else:
                # Multiclass Brier score average
                one_hot = np.eye(calibrated.shape[1])[y_true]
                self.brier_score = float(np.mean(np.sum((calibrated - one_hot) ** 2, axis=1)))

            self.ece = float(self._compute_ece(calibrated, y_true))
            self.is_fitted = True
        except Exception:
            self.is_fitted = False

        return self

    def calibrate(self, raw_probs: np.ndarray) -> np.ndarray:
        if not self.is_fitted or self.calibrator is None:
            return raw_probs

        if len(raw_probs.shape) == 1:
            raw_probs_2d = np.column_stack([1 - raw_probs, raw_probs])
        else:
            raw_probs_2d = raw_probs

        try:
            return self.calibrator.predict_proba(raw_probs_2d)
        except Exception:
            return raw_probs

    def _compute_ece(self, probs: np.ndarray, y_true: np.ndarray, n_bins: int = 10) -> float:
        if len(probs.shape) > 1:
            confidences = np.max(probs, axis=1)
            predictions = np.argmax(probs, axis=1)
        else:
            confidences = probs
            predictions = (probs >= 0.5).astype(int)

        bin_boundaries = np.linspace(0, 1, n_bins + 1)
        ece = 0.0

        for i in range(n_bins):
            in_bin = (confidences > bin_boundaries[i]) & (confidences <= bin_boundaries[i+1])
            prop_in_bin = np.mean(in_bin)
            if prop_in_bin > 0:
                accuracy_in_bin = np.mean(predictions[in_bin] == y_true[in_bin])
                avg_confidence_in_bin = np.mean(confidences[in_bin])
                ece += np.abs(accuracy_in_bin - avg_confidence_in_bin) * prop_in_bin

        return float(ece)
