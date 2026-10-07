from enum import Enum
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field

class DataState(str, Enum):
    LIVE = "LIVE"
    DELAYED = "DELAYED"
    LAST_VERIFIED = "LAST_VERIFIED"
    PRE_MARKET = "PRE_MARKET"
    POST_MARKET = "POST_MARKET"
    HALTED = "HALTED"
    HOLIDAY = "HOLIDAY"
    CLOSED = "CLOSED"
    STALE = "STALE"
    DATA_UNAVAILABLE = "DATA_UNAVAILABLE"
    PROVIDER_ERROR = "PROVIDER_ERROR"
    DATA_QUALITY_REJECTED = "DATA_QUALITY_REJECTED"


class MarketSessionState(str, Enum):
    PRE_MARKET = "PRE_MARKET"
    OPEN = "OPEN"
    POST_MARKET = "POST_MARKET"
    CLOSED = "CLOSED"
    HALTED = "HALTED"
    HOLIDAY = "HOLIDAY"
    SPECIAL_SESSION = "SPECIAL_SESSION"
    UNKNOWN = "UNKNOWN"


class ProviderCapability(str, Enum):
    HISTORICAL = "historical"
    DELAYED_QUOTE = "delayed_quote"
    REALTIME_QUOTE = "realtime_quote"
    TRADE_STREAM = "trade_stream"
    BAR_STREAM = "bar_stream"
    MARKET_STATUS = "market_status"
    PRE_MARKET_DATA = "pre_market_data"
    AFTER_HOURS_DATA = "after_hours_data"
    NEWS = "news"
    CORPORATE_ACTIONS = "corporate_actions"


class ProviderCapabilities(BaseModel):
    historical: bool = False
    delayed_quotes: bool = False
    realtime_quotes: bool = False
    trade_stream: bool = False
    bar_stream: bool = False
    market_status: bool = False
    pre_market: bool = False
    after_hours: bool = False
    news: bool = False
    corporate_actions: bool = False


class LatencyAudit(BaseModel):
    provider_timestamp: float
    ingestion_timestamp: float
    processing_timestamp: float
    websocket_timestamp: Optional[float] = None
    frontend_received_timestamp: Optional[float] = None
    latency_ms: Optional[float] = None
    e2e_latency_ms: Optional[float] = None


class MarketQuote(BaseModel):
    symbol: str
    exchange: str
    price: float
    change: float
    percent_change: float
    open: float
    high: float
    low: float
    previous_close: float
    volume: float
    timestamp: float
    data_state: DataState
    provider_name: str
    latency_audit: Optional[LatencyAudit] = None

    asset_type: str = "equity"
    currency: str = "USD"
    instrument_id: Optional[str] = None
    market_session: MarketSessionState = MarketSessionState.CLOSED
    source: str = ""
    is_stale: bool = False
    is_verified: bool = False
    regular_close: Optional[float] = None
    after_hours_price: Optional[float] = None
    after_hours_change: Optional[float] = None
    after_hours_change_percent: Optional[float] = None
    after_hours_timestamp: Optional[float] = None
    market_cap: Optional[float] = None
    pe_ratio: Optional[float] = None
    day_high: Optional[float] = None
    day_low: Optional[float] = None


class MarketBar(BaseModel):
    symbol: str
    timestamp: float
    open: float
    high: float
    low: float
    close: float
    volume: float
    data_state: DataState
    is_complete: bool = True
    source: str = ""


class MarketSessionInfo(BaseModel):
    exchange: str
    status: MarketSessionState
    session: str
    active_market: str
    server_time: str
    exchange_time: str
    next_open: Optional[str] = None
    next_close: Optional[str] = None
    last_close: Optional[str] = None
    holiday_name: Optional[str] = None
    is_shortened_session: bool = False
    halt_reason: Optional[str] = None
    session_status_conflict: bool = False
    timezone: str = ""
    currency: str = ""


class GlobalMarketStatus(BaseModel):
    active_market: str
    mode: str
    india_session: MarketSessionInfo
    us_session: MarketSessionInfo
    timestamp: float
    uk_session: Optional[MarketSessionInfo] = None
    japan_session: Optional[MarketSessionInfo] = None
    hongkong_session: Optional[MarketSessionInfo] = None
    all_markets_closed: bool = False
    after_hours_available: bool = False


class PredictionProvenance(BaseModel):
    prediction_id: str
    symbol: str
    generated_at: str
    data_timestamp: str
    model_version: str
    feature_version: str
    dataset_version: str
    regime_version: str
    calibration_version: str
    conformal_version: str
    data_status: DataState
    feature_count: int
    training_observations: int
    is_ensemble: bool
    model_count: int


class PredictionQualityGate(BaseModel):
    live_data: bool
    data_quality_pass: bool
    sufficient_history: bool
    correct_feature_schema: bool
    model_healthy: bool
    calibration_available: bool
    conformal_available: bool
    regime_valid: bool
    model_consensus_acceptable: bool
    uncertainty_acceptable: bool
    gate_passed: bool
    gate_failures: List[str]


class DataQualityScore(BaseModel):
    feed_freshness: float
    historical_coverage: float
    feature_completeness: float
    news_freshness: float
    market_liquidity: float
    model_health: float
    overall_score: float
    component_details: Dict[str, Any]


class IntelligenceAvailability(BaseModel):
    prediction: str
    calibration: str
    conformal: str
    shap: str
    news_catalyst: str
    regime: str
    risk: str
    backtesting: str
    required_history: Optional[int] = None
    available_history: Optional[int] = None


class InstrumentIdentity(BaseModel):
    instrument_id: str
    current_symbol: str
    exchange: str
    asset_type: str
    company_name: str
    previous_symbols: List[str] = Field(default_factory=list)
    is_delisted: bool = False
    is_halted: bool = False
    ipo_date: Optional[str] = None
    delisted_date: Optional[str] = None
    currency: str
    sector: Optional[str] = None
    industry: Optional[str] = None


class AuditEvent(BaseModel):
    event_type: str
    timestamp: str
    details: Dict[str, Any]
    severity: str


class ErrorResponse(BaseModel):
    status: str = "error"
    code: str
    message: str
    last_verified_at: Optional[str] = None
    retryable: bool = False
