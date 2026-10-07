import re
from typing import Dict, Any, List
from pydantic import BaseModel
from backend.app.services.prediction_engine import prediction_engine
from backend.app.data.ingestion_engine import ingestion_engine


class CopilotRequest(BaseModel):
    query: str


class CopilotResponse(BaseModel):
    response_text: str
    evidence_sections: List[Dict[str, Any]]
    data_state: str
    confidence: str
    disclaimers: List[str]
    sources_used: List[str]


class CopilotEngine:
    KNOWN_SYMBOLS = ["AAPL", "NVDA", "MSFT", "RELIANCE", "RELIANCE.NS", "TCS", "TCS.NS", "INFY", "INFY.NS", "HDFCBANK", "TSLA", "GOOGL", "AMZN", "META", "SPY"]

    def _extract_symbol(self, query: str) -> str:
        query_upper = query.upper()
        for sym in self.KNOWN_SYMBOLS:
            if sym in query_upper:
                return "RELIANCE.NS" if sym == "RELIANCE" else ("TCS.NS" if sym == "TCS" else ("INFY.NS" if sym == "INFY" else sym))

        # Check regex match for standard tickers
        match = re.search(r'\b[A-Z]{2,6}(\.NS)?\b', query_upper)
        if match:
            return match.group(0)
        return "AAPL"

    def ask(self, request: CopilotRequest) -> CopilotResponse:
        sym = self._extract_symbol(request.query)
        pred = prediction_engine.predict(sym)

        if not pred:
            return CopilotResponse(
                response_text="I cannot produce a reliable quantitative explanation because the required live market / model evidence is unavailable.",
                evidence_sections=[],
                data_state="UNAVAILABLE",
                confidence="INSUFFICIENT_DATA",
                disclaimers=["This system does not provide financial advice."],
                sources_used=[]
            )

        sig = pred.signal
        reg = pred.regime
        stab = pred.stability
        shap = pred.explainability

        pos_drivers = ", ".join([d.feature_name for d in shap.top_positive_drivers[:2]]) or "technical indicators"
        neg_drivers = ", ".join([d.feature_name for d in shap.top_negative_drivers[:2]]) or "momentum bounds"

        # Check if user asks "Should I buy?"
        query_lower = request.query.lower()
        if "should i buy" in query_lower or "should i sell" in query_lower:
            response_text = f"Based on quantitative evidence for {pred.symbol}, the current signal is {sig.signal} with a {sig.calibrated_probability * 100:.1f}% probability under a {reg.regime_name} regime. However, this is not financial advice."
        else:
            response_text = f"Quantitative Analysis for {pred.symbol} indicates a {sig.signal} signal with {sig.calibrated_probability * 100:.1f}% confidence."

        evidence_sections = [
            {
                "type": "FACTUAL_DATA",
                "content": {
                    "price": f"${pred.quote_price:.2f}",
                    "feed": pred.data_state,
                    "market_status": "OPEN" # Mocking for now
                }
            },
            {
                "type": "MODEL_OUTPUT",
                "content": {
                    "signal": sig.signal,
                    "probability": f"{sig.calibrated_probability * 100:.1f}%",
                    "expected_return": f"{sig.expected_return_pct:+.2f}%",
                    "conformal_range": f"[{getattr(sig.conformal_range, 'lower_bound_pct', 0.0):+.2f}%, {getattr(sig.conformal_range, 'upper_bound_pct', 0.0):+.2f}%]",
                    "regime": reg.regime_name,
                    "stability": stab.stability_level,
                    "positive_drivers": pos_drivers,
                    "negative_drivers": neg_drivers
                }
            },
            {
                "type": "GENERAL_EXPLANATION",
                "content": {
                    "context": "The model uses conformal prediction to estimate uncertainty and SHAP values for feature attribution."
                }
            }
        ]

        return CopilotResponse(
            response_text=response_text,
            evidence_sections=evidence_sections,
            data_state=pred.data_state,
            confidence="HIGH" if sig.calibrated_probability > 0.6 else "MEDIUM",
            disclaimers=[
                "This system does not provide financial advice.",
                "Predictions are based on historical and real-time data but do not guarantee future performance."
            ],
            sources_used=["ORION-Q Prediction Engine", "Live Market Feed"]
        )


copilot_engine = CopilotEngine()
