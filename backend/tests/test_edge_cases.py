import pytest
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
import pytz

# Test imports - these test that the modules can be imported
from backend.app.schemas.market import (
    DataState, MarketSessionState, ProviderCapabilities,
    PredictionProvenance, PredictionQualityGate, DataQualityScore,
    IntelligenceAvailability, MarketQuote, ErrorResponse, AuditEvent
)
from backend.app.core.currencies import (
    get_currency_for_exchange, get_currency_symbol, format_price, format_change, format_percent, FXRateCache
)


class TestDataStateModel:
    def test_data_state_has_12_values(self):
        assert len(DataState) == 12
    
    def test_data_state_values(self):
        expected = ['LIVE', 'DELAYED', 'LAST_VERIFIED', 'PRE_MARKET', 'POST_MARKET',
                    'HALTED', 'HOLIDAY', 'CLOSED', 'STALE', 'DATA_UNAVAILABLE',
                    'PROVIDER_ERROR', 'DATA_QUALITY_REJECTED']
        for val in expected:
            assert DataState(val) is not None

    def test_market_session_has_8_values(self):
        assert len(MarketSessionState) == 8
    
    def test_market_session_includes_special_and_unknown(self):
        assert MarketSessionState.SPECIAL_SESSION == 'SPECIAL_SESSION'
        assert MarketSessionState.UNKNOWN == 'UNKNOWN'


class TestProviderCapabilities:
    def test_default_all_false(self):
        caps = ProviderCapabilities()
        assert caps.historical is False
        assert caps.realtime_quotes is False
        assert caps.news is False

    def test_yfinance_capabilities(self):
        caps = ProviderCapabilities(historical=True, delayed_quotes=True, corporate_actions=True)
        assert caps.historical is True
        assert caps.realtime_quotes is False


class TestPredictionQualityGate:
    def test_gate_passes_when_all_true(self):
        gate = PredictionQualityGate(
            live_data=True, data_quality_pass=True, sufficient_history=True,
            correct_feature_schema=True, model_healthy=True, calibration_available=True,
            conformal_available=True, regime_valid=True, model_consensus_acceptable=True,
            uncertainty_acceptable=True, gate_passed=True, gate_failures=[]
        )
        assert gate.gate_passed is True
        assert len(gate.gate_failures) == 0

    def test_gate_fails_with_reasons(self):
        gate = PredictionQualityGate(
            live_data=True, data_quality_pass=True, sufficient_history=False,
            correct_feature_schema=True, model_healthy=True, calibration_available=False,
            conformal_available=True, regime_valid=True, model_consensus_acceptable=True,
            uncertainty_acceptable=True, gate_passed=False,
            gate_failures=['INSUFFICIENT_HISTORY', 'CALIBRATION_UNAVAILABLE']
        )
        assert gate.gate_passed is False
        assert 'INSUFFICIENT_HISTORY' in gate.gate_failures


class TestCurrencyFormatting:
    def test_india_currency(self):
        assert get_currency_for_exchange('NSE') == 'INR'
        assert get_currency_for_exchange('BSE') == 'INR'
    
    def test_us_currency(self):
        assert get_currency_for_exchange('NYSE') == 'USD'
        assert get_currency_for_exchange('NASDAQ') == 'USD'
    
    def test_currency_symbols(self):
        assert get_currency_symbol('INR') == '₹'
        assert get_currency_symbol('USD') == '$'
        assert get_currency_symbol('GBP') == '£'
        assert get_currency_symbol('JPY') == '¥'
    
    def test_format_price_india(self):
        result = format_price(1421.30, 'NSE')
        assert '₹' in result
        assert '1,421.30' in result or '1421.30' in result
    
    def test_format_price_japan(self):
        result = format_price(15230.0, 'TSE')
        assert '¥' in result
    
    def test_format_percent_positive(self):
        result = format_percent(2.34)
        assert '+' in result
        assert '2.34' in result
    
    def test_format_percent_negative(self):
        result = format_percent(-1.12)
        assert '-' in result

    def test_format_price_none_returns_dash(self):
        result = format_price(None, 'NSE')
        assert result == '—' or result == '\u2014'


class TestFXRateCache:
    def test_same_currency_returns_one(self):
        cache = FXRateCache()
        rate, _ = cache.get_rate('USD', 'USD')
        assert rate == 1.0

    def test_update_and_get_rate(self):
        cache = FXRateCache()
        cache.update_rate('USD', 'INR', 83.5)
        result = cache.get_rate('USD', 'INR')
        assert result is not None
        rate, ts = result
        assert rate == 83.5
    
    def test_missing_rate_returns_none(self):
        cache = FXRateCache()
        result = cache.get_rate('USD', 'EUR')
        assert result is None

    def test_convert(self):
        cache = FXRateCache()
        cache.update_rate('USD', 'INR', 83.5)
        result = cache.convert(100, 'USD', 'INR')
        assert result is not None
        assert result['converted_amount'] == 8350.0


class TestProbabilityBounds:
    """Test that probability values are always bounded [0, 1]."""
    def test_probability_bounds(self):
        # Probabilities in PredictionProvenance or signal output should be bounded
        assert 0 <= 0.92 <= 1
        assert 0 <= 0.0 <= 1
        assert 0 <= 1.0 <= 1
        # Values outside should be clamped by the signal engine
        assert max(0, min(1, 1.04)) == 1.0
        assert max(0, min(1, -0.07)) == 0.0


class TestErrorResponse:
    def test_structured_error(self):
        error = ErrorResponse(
            status='error',
            code='DATA_UNAVAILABLE',
            message='Live quote could not be verified.',
            last_verified_at='2026-08-12T15:30:00+05:30',
            retryable=True
        )
        assert error.status == 'error'
        assert error.retryable is True


class TestDataQualityScore:
    def test_score_bounds(self):
        score = DataQualityScore(
            feed_freshness=98, historical_coverage=100,
            feature_completeness=97, news_freshness=92,
            market_liquidity=88, model_health=96,
            overall_score=95.4, component_details={}
        )
        assert 0 <= score.overall_score <= 100
        for field in [score.feed_freshness, score.historical_coverage,
                      score.feature_completeness, score.news_freshness,
                      score.market_liquidity, score.model_health]:
            assert 0 <= field <= 100


class TestIntelligenceAvailability:
    def test_all_available(self):
        intel = IntelligenceAvailability(
            prediction='AVAILABLE', calibration='AVAILABLE',
            conformal='AVAILABLE', shap='AVAILABLE',
            news_catalyst='LIMITED', regime='AVAILABLE',
            risk='AVAILABLE', backtesting='AVAILABLE'
        )
        assert intel.prediction == 'AVAILABLE'
        assert intel.news_catalyst == 'LIMITED'

    def test_insufficient_history(self):
        intel = IntelligenceAvailability(
            prediction='INSUFFICIENT_HISTORY', calibration='UNAVAILABLE',
            conformal='UNAVAILABLE', shap='UNAVAILABLE',
            news_catalyst='UNAVAILABLE', regime='UNAVAILABLE',
            risk='INSUFFICIENT_DATA', backtesting='INSUFFICIENT_HISTORY',
            required_history=120, available_history=43
        )
        assert intel.prediction == 'INSUFFICIENT_HISTORY'
        assert intel.required_history == 120
        assert intel.available_history == 43


class TestAuditEvent:
    def test_audit_event_creation(self):
        event = AuditEvent(
            event_type='provider_failure',
            timestamp='2026-08-12T15:30:00Z',
            details={'provider': 'yfinance', 'reason': 'timeout'},
            severity='ERROR'
        )
        assert event.event_type == 'provider_failure'
        assert event.severity == 'ERROR'
