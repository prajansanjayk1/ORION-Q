import os
import time
import numpy as np
import pandas as pd
from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from backend.app.data.ingestion_engine import ingestion_engine
from backend.app.data.instrument_registry import instrument_registry
from backend.app.features.pipeline import FeaturePipeline
from backend.app.ml.targets import construct_targets
from backend.app.ml.preprocessing import LeakageSafePreprocessor, create_chronological_splits
from backend.app.ml.models import ModelParliament
from backend.app.ml.model_registry import model_registry
from backend.app.services.regime_engine import regime_engine, RegimeResult
from backend.app.services.explainability_engine import explainability_engine, ExplainabilityResult
from backend.app.services.counterfactual_engine import counterfactual_engine, CounterfactualResult
from backend.app.services.stability_engine import stability_engine, StabilityResult
from backend.app.services.signal_engine import signal_engine, SignalOutput
from backend.app.core.currencies import get_currency_for_exchange
from backend.app.core.logging import logger


class PredictionProvenance(BaseModel):
    prediction_id: str
    generated_at: str
    model_version: str
    feature_version: str
    calibration_version: str
    conformal_version: str
    data_status: str
    is_ensemble: bool = True


class QualityGateStatus(BaseModel):
    gate_passed: bool
    gate_failures: List[str] = Field(default_factory=list)


class IntelligenceAvailability(BaseModel):
    conformal: str  # AVAILABLE | LIMITED | CONFORMAL UNAVAILABLE
    calibration: str  # AVAILABLE | LIMITED | CALIBRATION UNAVAILABLE
    shap: str  # AVAILABLE | LIMITED | EXPLANATION UNAVAILABLE
    regime: str  # AVAILABLE | LIMITED | REGIME UNAVAILABLE
    available_history: int
    required_history: int = 40


class PredictionResult(BaseModel):
    symbol: str
    currency: str
    data_state: str
    quote_price: float
    market_session: str
    market_session_state: str
    regime: RegimeResult
    signal: SignalOutput
    stability: StabilityResult
    explainability: ExplainabilityResult
    counterfactuals: CounterfactualResult
    model_leaderboard: Dict[str, float]
    quality_gate: QualityGateStatus
    intelligence: IntelligenceAvailability
    provenance: PredictionProvenance


class PredictionEngine:
    def __init__(self):
        self._model_cache: Dict[str, Tuple[ModelParliament, LeakageSafePreprocessor]] = {}
        self._prediction_cache: Dict[str, Tuple[float, PredictionResult]] = {}

    def _train_or_get_model(self, symbol: str, df: pd.DataFrame) -> Tuple[ModelParliament, LeakageSafePreprocessor]:
        if symbol in self._model_cache:
            return self._model_cache[symbol]

        # Extract features and target
        df_feat, feature_cols = FeaturePipeline.extract_features(df)
        df_targeted = construct_targets(df_feat, horizon=5)
        df_clean = df_targeted.dropna().reset_index(drop=True)

        if len(df_clean) < 40:
            raise ValueError(f"Insufficient historical bars to train model for {symbol}")

        # Chronological split
        train_df, val_df, test_df = create_chronological_splits(df_clean, train_ratio=0.7, val_ratio=0.15)

        # Leakage-safe Preprocessor
        preprocessor = LeakageSafePreprocessor()
        X_train_scaled = preprocessor.fit_transform(train_df, feature_cols)

        y_train_class = train_df["target_class"].values
        y_train_ret = train_df["future_return"].values

        # Model Parliament
        parliament = ModelParliament(symbol=symbol)
        parliament.fit(X_train_scaled, y_train_class, y_train_ret, feature_names=preprocessor.selected_features)

        self._model_cache[symbol] = (parliament, preprocessor)
        return parliament, preprocessor

    def predict(self, symbol: str) -> Optional[PredictionResult]:
        symbol_clean = symbol.upper().strip()
        now = time.time()
        if symbol_clean in self._prediction_cache:
            ts, cached_res = self._prediction_cache[symbol_clean]
            if now - ts < 30.0:
                return cached_res
        quote = ingestion_engine.get_quote(symbol_clean)
        if not quote:
            return None

        hist_df = ingestion_engine.get_historical_data(symbol_clean, period="1y", interval="1d")
        if hist_df.empty:
            return None

        # Resolve instrument metadata and currency
        inst = instrument_registry.get_by_symbol(symbol_clean)
        currency = inst.currency if inst else get_currency_for_exchange(quote.exchange)

        # Detect market regime
        regime_res = regime_engine.detect_regime(hist_df)

        try:
            parliament, preprocessor = self._train_or_get_model(symbol_clean, hist_df)

            # Extract features for latest observation
            df_feat, feature_cols = FeaturePipeline.extract_features(hist_df)
            X_latest_scaled = preprocessor.transform(df_feat.iloc[[-1]])

            # Parliament predictions
            calibrated_probs, point_returns, conformal_interval = parliament.predict(X_latest_scaled)

            # Stability Analysis
            stability_res = stability_engine.calculate_stability(
                parliament.leaderboard, calibrated_probs, regime_res.regime_name
            )

            # Signal Engine
            latest_return = float(point_returns[-1]) if len(point_returns) > 0 else 0.0
            signal_res = signal_engine.generate_signal(
                calibrated_probs, latest_return, conformal_interval, regime_res.regime_name, stability_res
            )

            # Explainability & Counterfactuals
            shap_res = explainability_engine.explain_prediction(
                parliament, X_latest_scaled, preprocessor.selected_features
            )
            counterfactual_res = counterfactual_engine.analyze_counterfactuals(
                signal_res.signal, X_latest_scaled, preprocessor.selected_features
            )

            # Quality gate validation
            gate_failures = []
            if len(hist_df) < 40:
                gate_failures.append("Insufficient historical bar depth (< 40 sessions)")
            if quote.data_state.value == "DATA_UNAVAILABLE":
                gate_failures.append("Market data feed unavailable")

            quality_gate = QualityGateStatus(
                gate_passed=len(gate_failures) == 0,
                gate_failures=gate_failures
            )

            intelligence = IntelligenceAvailability(
                conformal=conformal_interval.status,
                calibration="AVAILABLE" if parliament.calibrator.is_fitted else "CALIBRATION UNAVAILABLE",
                shap="AVAILABLE" if len(shap_res.top_positive_drivers) > 0 else "EXPLANATION UNAVAILABLE",
                regime="AVAILABLE",
                available_history=len(hist_df),
                required_history=40
            )

            provenance = PredictionProvenance(
                prediction_id=f"PRED-{symbol_clean}-{int(time.time())}",
                generated_at=pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S UTC"),
                model_version="ORION-PARLIAMENT-1.1.0",
                feature_version="2.0.0",
                calibration_version="Platt Scaling (OOF)",
                conformal_version="Split Conformal 95%",
                data_status=quote.data_state.value,
                is_ensemble=True
            )

            res = PredictionResult(
                symbol=symbol_clean,
                currency=currency,
                data_state=quote.data_state.value,
                quote_price=quote.price,
                market_session=quote.exchange,
                market_session_state=quote.data_state.value,
                regime=regime_res,
                signal=signal_res,
                stability=stability_res,
                explainability=shap_res,
                counterfactuals=counterfactual_res,
                model_leaderboard=parliament.leaderboard,
                quality_gate=quality_gate,
                intelligence=intelligence,
                provenance=provenance
            )
            self._prediction_cache[symbol_clean] = (now, res)
            return res

        except Exception as e:
            logger.error(f"Prediction failed for {symbol}: {e}")
            return None


prediction_engine = PredictionEngine()
