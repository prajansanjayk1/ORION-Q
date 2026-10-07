import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import pytz
from backend.app.schemas.market import AuditEvent
from backend.app.core.logging import logger


# Event types per spec §94
EVENT_TYPES = [
    "market_open", "market_close", "provider_switch", "provider_failure",
    "data_gap", "model_loaded", "model_failed", "model_promoted",
    "model_rolled_back", "regime_change", "prediction_generated",
    "alert_triggered", "websocket_connect", "websocket_disconnect",
    "session_status_conflict", "data_quality_rejected", "clock_skew_detected",
    "provider_rate_limited", "model_drift_detected", "calibration_drift",
    "stale_data_detected", "all_providers_failed"
]


class AuditLogger:
    """Structured event audit log for ORION-Q.
    Records all important system events with timestamps and details."""

    def __init__(self, max_events: int = 10000):
        self._events: List[AuditEvent] = []
        self._max_events = max_events

    def log_event(self, event_type: str, details: Dict[str, Any],
                  severity: str = "INFO") -> AuditEvent:
        """Record an audit event."""
        event = AuditEvent(
            event_type=event_type,
            timestamp=datetime.now(pytz.utc).isoformat(),
            details=details,
            severity=severity
        )
        self._events.append(event)
        if len(self._events) > self._max_events:
            self._events = self._events[-self._max_events:]

        # Also log to standard logger
        log_msg = f"[AUDIT] {event_type}: {json.dumps(details, default=str)}"
        if severity == "CRITICAL":
            logger.critical(log_msg)
        elif severity == "ERROR":
            logger.error(log_msg)
        elif severity == "WARNING":
            logger.warning(log_msg)
        else:
            logger.info(log_msg)

        return event

    def get_events(self, event_type: str = None, limit: int = 100,
                   severity: str = None) -> List[AuditEvent]:
        """Query recent events, optionally filtered by type and severity."""
        filtered = self._events
        if event_type:
            filtered = [e for e in filtered if e.event_type == event_type]
        if severity:
            filtered = [e for e in filtered if e.severity == severity]
        return filtered[-limit:]

    def get_recent(self, limit: int = 50) -> List[Dict]:
        """Get recent events as dicts for API response."""
        return [e.model_dump() for e in self._events[-limit:]]

    # Convenience methods for common events
    def log_market_open(self, exchange: str, session_time: str):
        self.log_event("market_open", {"exchange": exchange, "session_time": session_time})

    def log_market_close(self, exchange: str, session_time: str):
        self.log_event("market_close", {"exchange": exchange, "session_time": session_time})

    def log_provider_failure(self, provider: str, reason: str, symbol: str = None):
        self.log_event("provider_failure", {"provider": provider, "reason": reason, "symbol": symbol}, severity="ERROR")

    def log_provider_switch(self, symbol: str, from_provider: str, to_provider: str, reason: str):
        self.log_event("provider_switch", {
            "symbol": symbol, "from": from_provider, "to": to_provider, "reason": reason
        }, severity="WARNING")

    def log_data_gap(self, symbol: str, expected_at: str, actual_next: str, gap_minutes: float):
        self.log_event("data_gap", {
            "symbol": symbol, "expected_at": expected_at, "actual_next": actual_next, "gap_minutes": gap_minutes
        }, severity="WARNING")

    def log_model_loaded(self, symbol: str, model_version: str):
        self.log_event("model_loaded", {"symbol": symbol, "model_version": model_version})

    def log_model_failed(self, symbol: str, reason: str):
        self.log_event("model_failed", {"symbol": symbol, "reason": reason}, severity="ERROR")

    def log_regime_change(self, symbol: str, from_regime: str, to_regime: str):
        self.log_event("regime_change", {
            "symbol": symbol, "from": from_regime, "to": to_regime
        }, severity="WARNING")

    def log_prediction(self, symbol: str, signal: str, probability: float):
        self.log_event("prediction_generated", {
            "symbol": symbol, "signal": signal, "probability": probability
        })

    def log_alert(self, symbol: str, alert_type: str, message: str):
        self.log_event("alert_triggered", {
            "symbol": symbol, "alert_type": alert_type, "message": message
        })

    def log_stale_data(self, symbol: str, age_seconds: float):
        self.log_event("stale_data_detected", {
            "symbol": symbol, "age_seconds": age_seconds
        }, severity="WARNING")

    def log_clock_skew(self, skew_seconds: float, provider: str):
        self.log_event("clock_skew_detected", {
            "skew_seconds": skew_seconds, "provider": provider
        }, severity="WARNING")


audit_logger = AuditLogger()
