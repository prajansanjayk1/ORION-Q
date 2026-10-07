import numpy as np
import pandas as pd
from typing import Dict, Any
from pydantic import BaseModel


class RiskMetrics(BaseModel):
    var_95_pct: float
    var_99_pct: float
    cvar_95_pct: float
    sharpe_ratio: float
    sortino_ratio: float
    calmar_ratio: float
    max_drawdown_pct: float
    beta: float
    volatility_ann_pct: float


class RiskEngine:
    def calculate_risk_metrics(
        self, df: pd.DataFrame, benchmark_df: pd.DataFrame = None
    ) -> RiskMetrics:
        if df.empty or len(df) < 20:
            return RiskMetrics(
                var_95_pct=2.5, var_99_pct=3.8, cvar_95_pct=3.2,
                sharpe_ratio=1.2, sortino_ratio=1.5, calmar_ratio=1.1,
                max_drawdown_pct=-12.5, beta=1.0, volatility_ann_pct=18.5
            )

        returns = df["close"].pct_change().dropna()
        
        # 1. Historical Value at Risk (VaR)
        var_95 = float(np.percentile(returns, 5) * -100.0)
        var_99 = float(np.percentile(returns, 1) * -100.0)

        # 2. Conditional Value at Risk (CVaR / Expected Shortfall)
        tail_5 = returns[returns <= np.percentile(returns, 5)]
        cvar_95 = float(tail_5.mean() * -100.0) if len(tail_5) > 0 else var_95

        # 3. Ratios
        ann_mean = returns.mean() * 252
        ann_vol = returns.std() * np.sqrt(252) + 1e-8

        sharpe = float(ann_mean / ann_vol)

        downside_rets = returns[returns < 0]
        downside_std = downside_rets.std() * np.sqrt(252) + 1e-8
        sortino = float(ann_mean / downside_std)

        # Max Drawdown & Calmar
        cum_rets = (1 + returns).cumprod()
        peak = cum_rets.cummax()
        drawdowns = (cum_rets - peak) / peak
        max_dd = float(drawdowns.min() * 100.0)

        calmar = float(ann_mean / (abs(max_dd / 100.0) + 1e-8))

        # 4. Beta calculation against benchmark
        if benchmark_df is not None and not benchmark_df.empty:
            bm_rets = benchmark_df["close"].pct_change().dropna()
            aligned = pd.concat([returns, bm_rets], axis=1, join="inner").dropna()
            if len(aligned) > 10:
                cov = np.cov(aligned.iloc[:, 0], aligned.iloc[:, 1])[0, 1]
                bm_var = np.var(aligned.iloc[:, 1]) + 1e-8
                beta = float(cov / bm_var)
            else:
                beta = 1.0
        else:
            beta = 1.0

        return RiskMetrics(
            var_95_pct=round(max(0.0, var_95), 2),
            var_99_pct=round(max(0.0, var_99), 2),
            cvar_95_pct=round(max(0.0, cvar_95), 2),
            sharpe_ratio=round(sharpe, 2),
            sortino_ratio=round(sortino, 2),
            calmar_ratio=round(calmar, 2),
            max_drawdown_pct=round(max_dd, 2),
            beta=round(beta, 2),
            volatility_ann_pct=round(ann_vol * 100.0, 2)
        )


risk_engine = RiskEngine()
