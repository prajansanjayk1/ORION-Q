import time
from typing import Dict, Any, List
from datetime import datetime
import pytz
from backend.app.core.logging import logger


class SystemHealthMonitor:
    """Aggregates health status across all ORION-Q subsystems."""

    def __init__(self):
        self._subsystem_status: Dict[str, Dict[str, Any]] = {}
        self._startup_time: str = datetime.now(pytz.utc).isoformat()
        self._is_degraded: bool = False

    def update_subsystem(self, name: str, status: str, details: Dict[str, Any] = None):
        """Update status for a subsystem. status: HEALTHY, DEGRADED, UNAVAILABLE, ERROR"""
        self._subsystem_status[name] = {
            "status": status,
            "details": details or {},
            "last_checked": datetime.now(pytz.utc).isoformat()
        }
        self._is_degraded = any(
            s["status"] in ("DEGRADED", "UNAVAILABLE", "ERROR")
            for s in self._subsystem_status.values()
        )

    def get_overall_status(self) -> Dict[str, Any]:
        """Get aggregated system health."""
        statuses = {name: info["status"] for name, info in self._subsystem_status.items()}
        if any(s == "ERROR" for s in statuses.values()):
            overall = "ERROR"
        elif any(s in ("DEGRADED", "UNAVAILABLE") for s in statuses.values()):
            overall = "DEGRADED"
        else:
            overall = "HEALTHY"

        return {
            "overall_status": overall,
            "is_degraded": self._is_degraded,
            "startup_time": self._startup_time,
            "subsystems": self._subsystem_status,
            "checked_at": datetime.now(pytz.utc).isoformat()
        }

    def check_provider_health(self, providers: List[Dict]) -> str:
        """Check health of data providers and update subsystem."""
        healthy = sum(1 for p in providers if p.get("is_healthy", False))
        total = len(providers)
        if healthy == 0:
            status = "ERROR"
        elif healthy < total:
            status = "DEGRADED"
        else:
            status = "HEALTHY"
        self.update_subsystem("data_providers", status, {
            "healthy": healthy, "total": total, "providers": providers
        })
        return status

    def check_ml_health(self, model_health_status: str) -> str:
        """Update ML subsystem health."""
        self.update_subsystem("ml_pipeline", model_health_status)
        return model_health_status

    def check_websocket_health(self, active_connections: int, total_subscriptions: int) -> str:
        """Update WebSocket subsystem health."""
        status = "HEALTHY" if active_connections >= 0 else "DEGRADED"
        self.update_subsystem("websocket", status, {
            "active_connections": active_connections,
            "total_subscriptions": total_subscriptions
        })
        return status

    def is_system_healthy(self) -> bool:
        return not self._is_degraded


health_monitor = SystemHealthMonitor()
