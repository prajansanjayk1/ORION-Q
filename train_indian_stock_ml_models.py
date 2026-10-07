import sys
from backend.app.core.config import settings
from backend.app.data.ingestion_engine import ingestion_engine
from backend.app.services.prediction_engine import prediction_engine


def main():
    print("=" * 60)
    print("ORION-Q MODEL PARLIAMENT TRAINING PIPELINE (INDIAN EQUITIES - NSE/BSE)")
    print("=" * 60)

    symbols = settings.DEFAULT_INDIA_SYMBOLS[:5]
    print(f"Training models for target Indian symbols: {symbols}\n")

    for symbol in symbols:
        print(f"Fetching historical data & fitting model parliament for: {symbol}...")
        hist_df = ingestion_engine.get_historical_data(symbol, period="2y", interval="1d")
        if hist_df.empty:
            print(f"FAILED: Could not retrieve historical data for {symbol}\n")
            continue

        pred = prediction_engine.predict(symbol)
        if pred:
            print(f"SUCCESS: {symbol}")
            print(f"  - Signal: {pred.signal.signal}")
            print(f"  - Calibrated Bullish Prob: {pred.signal.calibrated_probability * 100:.1f}%")
            print(f"  - 95% Conformal Interval: [{pred.signal.conformal_range['lower_bound_pct']:+.2f}%, {pred.signal.conformal_range['upper_bound_pct']:+.2f}%]")
            print(f"  - Regime: {pred.regime.regime_name}")
            print(f"  - Leaderboard (Stacked OOS Acc): {pred.model_leaderboard.get('Stacked Ensemble', 0.0):.1f}%\n")
        else:
            print(f"FAILED: Model training error for {symbol}\n")

    print("All Indian models trained successfully.")


if __name__ == "__main__":
    main()
