from enum import Enum
from typing import Dict, Any, Optional
from pydantic import BaseModel, Field
import time


class EventType(str, Enum):
    PRICE_UPDATE = "PRICE_UPDATE"
    MARKET_STATUS = "MARKET_STATUS"
    REGIME_UPDATE = "REGIME_UPDATE"
    PREDICTION_UPDATE = "PREDICTION_UPDATE"
    NEWS_CATALYST = "NEWS_CATALYST"
    SIGNAL_UPDATE = "SIGNAL_UPDATE"
    ALERT = "ALERT"
    PORTFOLIO_UPDATE = "PORTFOLIO_UPDATE"
    HEARTBEAT = "HEARTBEAT"


class WSEvent(BaseModel):
    event_type: EventType
    symbol: Optional[str] = None
    data: Dict[str, Any]
    websocket_timestamp: float = Field(default_factory=time.time)
