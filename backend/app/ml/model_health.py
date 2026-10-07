import numpy as np
from typing import Dict, List, Optional, Any
from datetime import datetime
import pytz
from backend.app.schemas.market import ModelHealthStatus
from backend.app.core.logging import logger


class ModelHealthMonitor:
    """Monitors ML model health: calibration drift, performance drift, feature drift."""

    def __init__(self):
        self._rolling_predictions: List[Dict] = []  # recent predictions for drift detection
        self._rolling_actuals: List[Dict] = []  # recent actuals for performance tracking
        self._feature_baselines: Dict[str, Dict] = {}  # feature name -> {mean, std}
        self._calibration_history: List[Dict] = []  # brier score, ECE over time
        self._performance_history: List[Dict] = []  # accuracy, F1 over time
        self._max_history = 500

    def record_prediction(self, symbol: str, prediction: Dict):
        """Record a prediction for drift monitoring."""
        self._rolling_predictions.append({
            "symbol": symbol,
            "timestamp": datetime.now(pytz.utc).isoformat(),
            **prediction
        })
        if len(self._rolling_predictions) > self._max_history:
            self._rolling_predictions = self._rolling_predictions[-self._max_history:]

    def record_actual(self, symbol: str, actual_return: float, predicted_direction: str):
        """Record actual outcome for performance tracking."""
        self._rolling_actuals.append({
            "symbol": symbol,
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "actual_return": actual_return,
            "predicted_direction": predicted_direction
        })
        if len(self._rolling_actuals) > self._max_history:
            self._rolling_actuals = self._rolling_actuals[-self._max_history:]

    def set_feature_baseline(self, feature_name: str, mean: float, std: float):
        """Set the training-time baseline statistics for a feature."""
        self._feature_baselines[feature_name] = {"mean": mean, "std": std}

    def detect_feature_drift(self, current_features: Dict[str, float], threshold: float = 3.0) -> Dict[str, Any]:
        """Detect feature drift using z-score from training baseline.
        Returns dict with drift_detected flag and drifted features."""
        drifted = []
        for feat_name, feat_value in current_features.items():
            if feat_name in self._feature_baselines:
                baseline = self._feature_baselines[feat_name]
                if baseline["std"] > 0:
                    z_score = abs(feat_value - baseline["mean"]) / baseline["std"]
                    if z_score > threshold:
                        drifted.append({"feature": feat_name, "z_score": round(z_score, 2), "value": feat_value})
        return {"drift_detected": len(drifted) > 0, "drifted_features": drifted, "features_checked": len(current_features)}

    def detect_calibration_drift(self, recent_brier: float, recent_ece: float,
                                  brier_threshold: float = 0.3, ece_threshold: float = 0.15) -> Dict[str, Any]:
        """Detect calibration drift based on Brier score and ECE thresholds."""
        self._calibration_history.append({
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "brier_score": recent_brier,
            "ece": recent_ece
        })
        drift = recent_brier > brier_threshold or recent_ece > ece_threshold
        if drift:
            logger.warning(f"Calibration drift detected: Brier={recent_brier:.4f}, ECE={recent_ece:.4f}")
        return {"calibration_drift_detected": drift, "brier_score": recent_brier, "ece": recent_ece}

    def detect_performance_drift(self, rolling_accuracy: float, rolling_f1: float,
                                   accuracy_threshold: float = 0.45, f1_threshold: float = 0.4) -> Dict[str, Any]:
        """Detect performance drift based on rolling accuracy and F1."""
        self._performance_history.append({
            "timestamp": datetime.now(pytz.utc).isoformat(),
            "accuracy": rolling_accuracy,
            "f1": rolling_f1
        })
        drift = rolling_accuracy < accuracy_threshold or rolling_f1 < f1_threshold
        if drift:
            logger.warning(f"Performance drift detected: Accuracy={rolling_accuracy:.4f}, F1={rolling_f1:.4f}")
        return {"performance_drift_detected": drift, "rolling_accuracy": rolling_accuracy, "rolling_f1": rolling_f1}

    def get_health_status(self, model_name: str = "ensemble") -> ModelHealthStatus:
        """Aggregate health status from all drift signals."""
        feature_drift = len(self._feature_baselines) > 0 and any(
            d.get("drift_detected", False)
            for d in [self.detect_feature_drift({})]
        )

        cal_drift = False
        perf_drift = False
        brier = None
        ece = None
        accuracy = None

        if self._calibration_history:
            latest_cal = self._calibration_history[-1]
            brier = latest_cal["brier_score"]
            ece = latest_cal["ece"]
            cal_drift = brier > 0.3 or ece > 0.15

        if self._performance_history:
            latest_perf = self._performance_history[-1]
            accuracy = latest_perf["accuracy"]
            perf_drift = accuracy < 0.45

        any_drift = feature_drift or cal_drift or perf_drift
        status = "DRIFT_DETECTED" if any_drift else "HEALTHY"
        if not self._calibration_history and not self._performance_history:
            status = "UNAVAILABLE" if not self._rolling_predictions else "HEALTHY"

        return ModelHealthStatus(
            status=status,
            brier_score=brier,
            ece=ece,
            rolling_accuracy=accuracy,
            feature_drift_detected=feature_drift,
            calibration_drift_detected=cal_drift,
            performance_drift_detected=perf_drift,
            last_evaluated_at=datetime.now(pytz.utc).isoformat()
        )


model_health_monitor = ModelHealthMonitor()
