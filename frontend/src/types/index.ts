export type DataState = 'LIVE' | 'DELAYED' | 'LAST_VERIFIED' | 'PRE_MARKET' | 'POST_MARKET' | 'HALTED' | 'HOLIDAY' | 'CLOSED' | 'STALE' | 'DATA_UNAVAILABLE' | 'PROVIDER_ERROR' | 'DATA_QUALITY_REJECTED';

export type MarketSessionState = 'PRE_MARKET' | 'OPEN' | 'POST_MARKET' | 'CLOSED' | 'HALTED' | 'HOLIDAY' | 'SPECIAL_SESSION' | 'UNKNOWN';

export type MarketMode = 'AUTO' | 'INDIA' | 'US' | 'GLOBAL';

export type ModelConsensus = 'HIGH' | 'MEDIUM' | 'LOW';

export type ConnectionState = 'CONNECTING' | 'CONNECTED' | 'RECONNECTING' | 'DISCONNECTED' | 'DEGRADED';

export interface LatencyAudit {
  provider_timestamp: number;
  ingestion_timestamp: number;
  processing_timestamp: number;
  websocket_timestamp?: number;
  frontend_received_timestamp?: number;
  latency_ms?: number;
}

export interface MarketQuote {
  symbol: string;
  exchange: string;
  price: number;
  change: number;
  percent_change: number;
  open: number;
  high: number;
  low: number;
  previous_close: number;
  volume: number;
  timestamp: number;
  data_state: DataState;
  provider_name: string;
  latency_audit?: LatencyAudit;
  
  asset_type: string;
  currency: string;
  instrument_id?: string;
  market_session: MarketSessionState;
  source: string;
  is_stale: boolean;
  is_verified: boolean;
  regular_close?: number;
  after_hours_price?: number;
  after_hours_change?: number;
  after_hours_change_percent?: number;
  after_hours_timestamp?: number;
  market_cap?: number;
  pe_ratio?: number;
  day_high?: number;
  day_low?: number;
}

export interface MarketSessionInfo {
  exchange: string;
  status: MarketSessionState;
  session: string;
  active_market: string;
  server_time: string;
  exchange_time: string;
  next_open?: string;
  next_close?: string;
  last_close?: string;
  
  holiday_name?: string;
  is_shortened_session: boolean;
  halt_reason?: string;
  session_status_conflict: boolean;
  timezone: string;
  currency: string;
}

export interface GlobalMarketStatus {
  active_market: string;
  mode: MarketMode;
  india_session: MarketSessionInfo;
  us_session: MarketSessionInfo;
  timestamp: number;
  
  uk_session?: MarketSessionInfo;
  japan_session?: MarketSessionInfo;
  hongkong_session?: MarketSessionInfo;
  all_markets_closed: boolean;
  after_hours_available: boolean;
}

export interface ConformalRange {
  lower_bound_pct: number;
  upper_bound_pct: number;
  empirical_coverage: number;
}

export interface SignalOutput {
  signal: 'STRONG BUY' | 'BUY' | 'HOLD' | 'NO TRADE' | 'SELL' | 'STRONG SELL';
  calibrated_probability: number;
  expected_return_pct: number;
  conformal_range: ConformalRange;
  regime_name: string;
  stability_level: 'HIGH' | 'MEDIUM' | 'LOW';
  rationale: string;
  model_consensus: ModelConsensus;
}

export interface RegimeScores {
  trend_score: number;
  momentum_score: number;
  volatility_score: number;
  liquidity_score: number;
  sentiment_score: number;
  macro_risk_score: number;
}

export interface RegimeResult {
  regime_name: string;
  confidence: number;
  scores: RegimeScores;
  description: string;
}

export interface FeatureDriver {
  feature_name: string;
  impact: number;
  direction: 'POSITIVE' | 'NEGATIVE';
  description: string;
}

export interface ExplainabilityResult {
  top_positive_drivers: FeatureDriver[];
  top_negative_drivers: FeatureDriver[];
}

export interface FlipFactor {
  feature_name: string;
  current_value: number;
  required_direction: 'INCREASE' | 'DECREASE';
  sensitivity_score: number;
  description: string;
}

export interface CounterfactualResult {
  current_prediction: string;
  target_flip_signal: string;
  flip_factors: FlipFactor[];
}

export interface StabilityResult {
  stability_level: 'HIGH' | 'MEDIUM' | 'LOW';
  model_agreement_pct: number;
  temporal_variance: number;
  regime_consistency: boolean;
  score: number;
}

export interface PredictionProvenance {
  prediction_id: string;
  symbol: string;
  generated_at: string;
  data_timestamp: string;
  model_version: string;
  feature_version: string;
  dataset_version: string;
  regime_version: string;
  calibration_version: string;
  conformal_version: string;
  data_status: DataState;
  feature_count: number;
  training_observations: number;
  is_ensemble: boolean;
  model_count: number;
}

export interface PredictionQualityGate {
  live_data: boolean;
  data_quality_pass: boolean;
  sufficient_history: boolean;
  correct_feature_schema: boolean;
  model_healthy: boolean;
  calibration_available: boolean;
  conformal_available: boolean;
  regime_valid: boolean;
  model_consensus_acceptable: boolean;
  uncertainty_acceptable: boolean;
  gate_passed: boolean;
  gate_failures: string[];
}

export interface DataQualityScore {
  feed_freshness: number;
  historical_coverage: number;
  feature_completeness: number;
  news_freshness: number;
  market_liquidity: number;
  model_health: number;
  overall_score: number;
}

export interface IntelligenceAvailability {
  prediction: string;
  calibration: string;
  conformal: string;
  shap: string;
  news_catalyst: string;
  regime: string;
  risk: string;
  backtesting: string;
  required_history?: number;
  available_history?: number;
}

export interface PredictionResult {
  symbol: string;
  data_state: DataState;
  quote_price: number;
  market_session: string;
  regime: RegimeResult;
  signal: SignalOutput;
  stability: StabilityResult;
  explainability: ExplainabilityResult;
  counterfactuals: CounterfactualResult;
  model_leaderboard: Record<string, number>;
  
  currency?: string;
  after_hours_price?: number;
  after_hours_change_percent?: number;
  market_session_state?: MarketSessionState;
  provenance: PredictionProvenance;
  quality_gate: PredictionQualityGate;
  data_quality: DataQualityScore;
  intelligence: IntelligenceAvailability;
}
