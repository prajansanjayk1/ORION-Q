import sys
import json
from backend.app.services.prediction_engine import prediction_engine


def main():
    symbol = sys.argv[1] if len(sys.argv) > 1 else "AAPL"
    print(f"Executing ORION-Q Intelligence Terminal query for symbol: {symbol}\n")

    pred = prediction_engine.predict(symbol)
    if not pred:
        print(f"ERROR: Could not resolve prediction for symbol '{symbol}'. Data feeds may be unavailable.")
        sys.exit(1)

    print("=" * 70)
    print(f"  ORION-Q INSTITUTIONAL TERMINAL INTELLIGENCE: {pred.symbol}")
    print("=" * 70)
    print(f"Price:                ${pred.quote_price:.2f}")
    print(f"Data Feed State:      {pred.data_state}")
    print(f"Exchange Session:     {pred.market_session}")
    print("-" * 70)
    print(f"SIGNAL:               {pred.signal.signal}")
    print(f"Rationale:            {pred.signal.rationale}")
    print(f"Calibrated Prob:      {pred.signal.calibrated_probability * 100:.1f}% Bullish")
    print(f"Expected Return:      {pred.signal.expected_return_pct:+.2f}%")
    print(f"95% Conformal Range:  [{pred.signal.conformal_range['lower_bound_pct']:+.2f}%, {pred.signal.conformal_range['upper_bound_pct']:+.2f}%] (Coverage: {pred.signal.conformal_range['empirical_coverage']:.1f}%)")
    print("-" * 70)
    print(f"Regime:               {pred.regime.regime_name}")
    print(f"Stability:            {pred.stability.stability_level} (Model Agreement: {pred.stability.model_agreement_pct}%)")
    print("-" * 70)
    print("Top Positive SHAP Drivers:")
    for d in pred.explainability.top_positive_drivers:
        print(f"  + {d.feature_name}: {d.description}")
    print("\nTop Negative SHAP Drivers:")
    for d in pred.explainability.top_negative_drivers:
        print(f"  - {d.feature_name}: {d.description}")
    print("=" * 70)


if __name__ == "__main__":
    main()
