import pytest
import numpy as np
from backend.app.services.calibration_engine import ProbabilityCalibrationEngine
from backend.app.services.conformal_engine import ConformalEngine


def test_probability_calibration():
    np.random.seed(42)
    raw_probs = np.random.uniform(0.3, 0.8, 100)
    y_true = (raw_probs + np.random.normal(0, 0.1, 100) > 0.5).astype(int)

    engine = ProbabilityCalibrationEngine()
    engine.fit(raw_probs, y_true)

    calibrated = engine.calibrate(raw_probs)
    assert calibrated.shape == (100, 2)
    assert 0.0 <= engine.brier_score <= 1.0
    assert 0.0 <= engine.ece <= 1.0


def test_conformal_prediction():
    np.random.seed(42)
    y_true = np.random.normal(0, 0.02, 100)
    y_pred = np.random.normal(0, 0.01, 100)

    engine = ConformalEngine(alpha=0.05)
    engine.calibrate(y_true, y_pred)

    interval = engine.predict_interval(point_forecast=0.01)
    assert interval.lower_bound < interval.point_forecast < interval.upper_bound
    assert interval.interval_width > 0.0
    assert interval.empirical_coverage >= 90.0
