import pandas as pd
import numpy as np
from typing import Dict, List, Any
from pydantic import BaseModel


class Trade(BaseModel):
    entry_index: int
    exit_index: int
    entry_price: float
    exit_price: float
    return_pct: float
    type: str  # LONG | SHORT


class BacktestSummary(BaseModel):
    strategy_name: str
    total_return_pct: float
    cagr_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    max_drawdown_pct: float
    win_rate_pct: float
    trades_count: int
    profit_factor: float
    commission_bps: float
    slippage_bps: float


class BacktestEngine:
    def run_backtest(
        self,
        df: pd.DataFrame,
        strategy: str = "ADAPTIVE HYBRID",
        commission_bps: float = 5.0,
        slippage_bps: float = 2.0
    ) -> Tuple[BacktestSummary, pd.DataFrame]:
        if df.empty or len(df) < 30:
            empty_summary = BacktestSummary(
                strategy_name=strategy, total_return_pct=0.0, cagr_pct=0.0,
                sharpe_ratio=0.0, sortino_ratio=0.0, max_drawdown_pct=0.0,
                win_rate_pct=0.0, trades_count=0, profit_factor=1.0,
                commission_bps=commission_bps, slippage_bps=slippage_bps
            )
            return empty_summary, pd.DataFrame()

        data = df.copy()
        comm = commission_bps / 10000.0
        slip = slippage_bps / 10000.0
        total_cost = comm + slip

        # Generate signals based on strategy
        if strategy == "SMA CROSSOVER":
            sma10 = data["close"].rolling(10).mean()
            sma50 = data["close"].rolling(50).mean()
            data["signal"] = np.where(sma10 > sma50, 1, 0)
        elif strategy == "RSI REVERSION":
            delta = data["close"].diff()
            gain = delta.where(delta > 0, 0).rolling(14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
            rs = gain / (loss + 1e-8)
            rsi = 100 - (100 / (1 + rs))
            data["signal"] = np.where(rsi < 30, 1, np.where(rsi > 70, 0, 0))
        elif strategy == "BUY & HOLD":
            data["signal"] = 1
        else:  # ADAPTIVE HYBRID / ML ENSEMBLE
            ret21 = data["close"].pct_change(21)
            vol21 = data["close"].pct_change().rolling(21).std()
            data["signal"] = np.where((ret21 > 0) & (vol21 < 0.025), 1, 0)

        # Calculate position transitions and returns
        data["position"] = data["signal"].shift(1).fillna(0)
        data["asset_return"] = data["close"].pct_change().fillna(0)
        
        # Deduct transaction cost on position changes
        pos_change = (data["position"] != data["position"].shift(1)).astype(int)
        cost_penalty = pos_change * total_cost
        
        data["strategy_return"] = (data["position"] * data["asset_return"]) - cost_penalty
        data["equity_curve"] = (1.0 + data["strategy_return"]).cumprod()

        # Compute summary metrics
        total_ret = float((data["equity_curve"].iloc[-1] - 1.0) * 100.0)
        n_days = max(1, len(data))
        cagr = float(((data["equity_curve"].iloc[-1]) ** (252.0 / n_days) - 1.0) * 100.0)

        strat_rets = data["strategy_return"].dropna()
        mean_ret = strat_rets.mean()
        std_ret = strat_rets.std() + 1e-8

        sharpe = float((mean_ret / std_ret) * np.sqrt(252))

        neg_rets = strat_rets[strat_rets < 0]
        downside_std = neg_rets.std() + 1e-8
        sortino = float((mean_ret / downside_std) * np.sqrt(252))

        # Max Drawdown
        peak = data["equity_curve"].cummax()
        drawdown = (data["equity_curve"] - peak) / peak
        max_dd = float(drawdown.min() * 100.0)

        # Win Rate & Trades
        winning_days = (strat_rets > 0).sum()
        trades_count = int(pos_change.sum())
        win_rate = float((winning_days / len(strat_rets)) * 100.0) if len(strat_rets) > 0 else 0.0

        gross_profit = strat_rets[strat_rets > 0].sum()
        gross_loss = abs(strat_rets[strat_rets < 0].sum()) + 1e-8
        profit_factor = float(gross_profit / gross_loss)

        summary = BacktestSummary(
            strategy_name=strategy,
            total_return_pct=round(total_ret, 2),
            cagr_pct=round(cagr, 2),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            max_drawdown_pct=round(max_dd, 2),
            win_rate_pct=round(win_rate, 1),
            trades_count=trades_count,
            profit_factor=round(profit_factor, 2),
            commission_bps=commission_bps,
            slippage_bps=slippage_bps
        )

        return summary, data[["timestamp", "close", "position", "equity_curve"]]


backtest_engine = BacktestEngine()
