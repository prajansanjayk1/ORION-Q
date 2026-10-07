'use client';

import React, { useState, useEffect } from 'react';
import { fetchBacktestRun } from '../lib/api';
import { History, Play, TrendingUp, ShieldAlert, RefreshCw, BarChart2 } from 'lucide-react';

export const BacktestView: React.FC = () => {
  const [symbol, setSymbol] = useState<string>('AAPL');
  const [strategy, setStrategy] = useState<string>('ADAPTIVE HYBRID');
  const [period, setPeriod] = useState<string>('1y');
  const [data, setData] = useState<any>(null);
  const [loading, setLoading] = useState<boolean>(false);

  const runBacktest = async () => {
    setLoading(true);
    const res = await fetchBacktestRun(symbol, strategy, period);
    if (res) setData(res);
    setLoading(false);
  };

  useEffect(() => {
    runBacktest();
  }, [symbol, strategy, period]);

  const summary = data?.summary;
  const equityCurve = data?.equity_curve || [];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '20px' }}>
      {/* Configuration Header Panel */}
      <div className="panel" style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <History size={24} color="var(--color-cyan)" />
            <h1 style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
              Event-Driven Strategy Backtester
            </h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: '4px' }}>
            Realistic backtesting with 5.0 bps commission, 2.0 bps slippage, transaction penalties, and drawdown tracking.
          </p>
        </div>

        <div style={{ display: 'flex', gap: '12px', alignItems: 'center' }}>
          <select
            value={symbol}
            onChange={(e) => setSymbol(e.target.value)}
            style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-bright)', color: 'var(--text-primary)', padding: '6px 10px', borderRadius: '4px', fontSize: '12px' }}
          >
            <option value="AAPL">AAPL (US Equity)</option>
            <option value="RELIANCE">RELIANCE (India Equity)</option>
            <option value="NVDA">NVDA (US Equity)</option>
            <option value="TCS">TCS (India Equity)</option>
            <option value="SPY">SPY (S&P 500 ETF)</option>
          </select>

          <select
            value={strategy}
            onChange={(e) => setStrategy(e.target.value)}
            style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-bright)', color: 'var(--text-primary)', padding: '6px 10px', borderRadius: '4px', fontSize: '12px' }}
          >
            <option value="ADAPTIVE HYBRID">Adaptive ML Ensemble</option>
            <option value="SMA CROSSOVER">SMA Crossover (10/50)</option>
            <option value="RSI REVERSION">RSI Mean Reversion</option>
            <option value="BUY & HOLD">Buy & Hold Benchmark</option>
          </select>

          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-bright)', color: 'var(--text-primary)', padding: '6px 10px', borderRadius: '4px', fontSize: '12px' }}
          >
            <option value="1y">1 Year</option>
            <option value="2y">2 Years</option>
            <option value="6m">6 Months</option>
          </select>

          <button
            onClick={runBacktest}
            disabled={loading}
            style={{ background: 'linear-gradient(135deg, #06b6d4, #6366f1)', border: 'none', padding: '8px 16px', borderRadius: '4px', color: '#fff', fontWeight: 700, fontSize: '12px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            {loading ? <RefreshCw size={14} className="animate-spin" /> : <Play size={14} />} Execute Backtest
          </button>
        </div>
      </div>

      {/* Metric Cards Grid */}
      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(6, 1fr)', gap: '16px' }}>
          <div className="panel" style={{ padding: '12px 16px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>TOTAL RETURN</span>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)' }} className={summary.total_return_pct >= 0 ? 'positive' : 'negative'}>
              {summary.total_return_pct > 0 ? '+' : ''}{summary.total_return_pct}%
            </div>
          </div>
          <div className="panel" style={{ padding: '12px 16px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>CAGR</span>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-cyan)' }}>
              {summary.cagr_pct}%
            </div>
          </div>
          <div className="panel" style={{ padding: '12px 16px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>SHARPE RATIO</span>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-emerald)' }}>
              {summary.sharpe_ratio}
            </div>
          </div>
          <div className="panel" style={{ padding: '12px 16px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>MAX DRAWDOWN</span>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-rose)' }}>
              {summary.max_drawdown_pct}%
            </div>
          </div>
          <div className="panel" style={{ padding: '12px 16px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>WIN RATE</span>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--text-primary)' }}>
              {summary.win_rate_pct}%
            </div>
          </div>
          <div className="panel" style={{ padding: '12px 16px' }}>
            <span style={{ fontSize: '10px', color: 'var(--text-muted)' }}>PROFIT FACTOR</span>
            <div style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-purple)' }}>
              {summary.profit_factor}
            </div>
          </div>
        </div>
      )}

      {/* Cumulative Return & Equity Curve Visualizer */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <BarChart2 size={16} color="var(--color-cyan)" />
            <span>Cumulative Strategy Equity Curve vs Asset Performance</span>
          </div>
        </div>

        {equityCurve.length > 0 ? (
          <div style={{ height: '300px', width: '100%', position: 'relative', background: 'var(--bg-canvas)', borderRadius: '6px', padding: '16px', display: 'flex', flexDirection: 'column', justifyContent: 'flex-end' }}>
            <div style={{ display: 'flex', height: '100%', alignItems: 'flex-end', gap: '2px' }}>
              {equityCurve.map((eq: any, i: number) => {
                const heightPct = Math.min(100, Math.max(10, (eq.equity_curve / 2.0) * 100));
                const isGrowth = eq.equity_curve >= 1.0;
                return (
                  <div
                    key={i}
                    title={`${eq.timestamp}: ${eq.equity_curve.toFixed(3)}x`}
                    style={{
                      flex: 1,
                      height: `${heightPct}%`,
                      background: isGrowth ? 'var(--color-cyan)' : 'var(--color-rose)',
                      opacity: 0.8,
                      borderRadius: '1px'
                    }}
                  />
                );
              })}
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '10px', color: 'var(--text-muted)', marginTop: '8px' }}>
              <span>{equityCurve[0]?.timestamp}</span>
              <span>{equityCurve[Math.floor(equityCurve.length / 2)]?.timestamp}</span>
              <span>{equityCurve[equityCurve.length - 1]?.timestamp}</span>
            </div>
          </div>
        ) : (
          <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
            Click Execute Backtest to simulate strategy performance.
          </div>
        )}
      </div>
    </div>
  );
};
