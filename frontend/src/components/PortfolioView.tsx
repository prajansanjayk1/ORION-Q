'use client';

import React, { useState, useEffect } from 'react';
import { fetchPortfolioIntelligence } from '../lib/api';
import { Briefcase, ShieldAlert, DollarSign, PieChart, Activity } from 'lucide-react';

export const PortfolioView: React.FC = () => {
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    async function load() {
      const res = await fetchPortfolioIntelligence();
      if (res) setData(res);
    }
    load();
  }, []);

  if (!data) {
    return <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>Loading Portfolio Risk Engine...</div>;
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '20px' }}>
      {/* Portfolio Value Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '16px' }}>
        <div className="panel">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>TOTAL PORTFOLIO VALUE</div>
          <div style={{ fontSize: '24px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-cyan)', marginTop: '4px' }}>
            ${data.total_value.toLocaleString()}
          </div>
        </div>

        <div className="panel">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>UNREALIZED P&L</div>
          <div style={{ fontSize: '24px', fontWeight: 800, fontFamily: 'var(--font-mono)', marginTop: '4px' }} className={data.total_unrealized_pnl >= 0 ? 'positive' : 'negative'}>
            {data.total_unrealized_pnl > 0 ? '+' : ''}${data.total_unrealized_pnl.toLocaleString()} ({data.total_unrealized_pnl_pct.toFixed(2)}%)
          </div>
        </div>

        <div className="panel">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>VALUE AT RISK (95% VaR)</div>
          <div style={{ fontSize: '24px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-amber)', marginTop: '4px' }}>
            {data.risk_metrics.var_95_pct.toFixed(2)}%
          </div>
        </div>

        <div className="panel">
          <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>SHARPE RATIO</div>
          <div style={{ fontSize: '24px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-emerald)', marginTop: '4px' }}>
            {data.risk_metrics.sharpe_ratio.toFixed(2)}
          </div>
        </div>
      </div>

      {/* Holdings & Risk Breakdown */}
      <div style={{ display: 'grid', gridTemplateColumns: '8fr 4fr', gap: '20px' }}>
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <Briefcase size={16} color="var(--color-cyan)" />
              <span>Active Institutional Positions</span>
            </div>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '8px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '11px' }}>
                <th style={{ padding: '8px 12px' }}>SYMBOL</th>
                <th style={{ padding: '8px 12px' }}>QTY</th>
                <th style={{ padding: '8px 12px' }}>AVG PRICE</th>
                <th style={{ padding: '8px 12px' }}>CURRENT PRICE</th>
                <th style={{ padding: '8px 12px' }}>MARKET VALUE</th>
                <th style={{ padding: '8px 12px' }}>UNREALIZED P&L</th>
                <th style={{ padding: '8px 12px' }}>WEIGHT</th>
                <th style={{ padding: '8px 12px' }}>FEED</th>
              </tr>
            </thead>
            <tbody>
              {data.positions.map((p: any) => (
                <tr key={p.symbol} style={{ borderBottom: '1px solid var(--border-color)' }}>
                  <td style={{ padding: '10px 12px', fontWeight: 700, color: 'var(--color-cyan)', fontFamily: 'var(--font-mono)' }}>{p.symbol}</td>
                  <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)' }}>{p.quantity}</td>
                  <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)' }}>${p.avg_price.toFixed(2)}</td>
                  <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)' }}>${p.current_price.toFixed(2)}</td>
                  <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)' }}>${p.market_value.toLocaleString()}</td>
                  <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', fontWeight: 600 }} className={p.unrealized_pnl >= 0 ? 'positive' : 'negative'}>
                    {p.unrealized_pnl > 0 ? '+' : ''}${p.unrealized_pnl.toFixed(2)} ({p.unrealized_pnl_pct.toFixed(2)}%)
                  </td>
                  <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{p.weight_pct.toFixed(1)}%</td>
                  <td style={{ padding: '10px 12px' }}>
                    <span className={`badge ${p.data_state === 'LIVE' ? 'badge-live' : 'badge-closed'}`}>{p.data_state}</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Portfolio Risk Engine Metrics */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <ShieldAlert size={16} color="var(--color-amber)" />
              <span>Risk Analytics & Ratios</span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', fontSize: '12px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Value at Risk (99% VaR):</span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-rose)' }}>{data.risk_metrics.var_99_pct.toFixed(2)}%</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>CVaR (Expected Shortfall):</span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-rose)' }}>{data.risk_metrics.cvar_95_pct.toFixed(2)}%</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Sortino Ratio:</span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-emerald)' }}>{data.risk_metrics.sortino_ratio.toFixed(2)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Calmar Ratio:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>{data.risk_metrics.calmar_ratio.toFixed(2)}</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Max Drawdown:</span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-rose)' }}>{data.risk_metrics.max_drawdown_pct.toFixed(2)}%</strong>
            </div>
            <div style={{ display: 'flex', justifyContent: 'space-between' }}>
              <span style={{ color: 'var(--text-secondary)' }}>Portfolio Beta:</span>
              <strong style={{ fontFamily: 'var(--font-mono)' }}>{data.risk_metrics.beta.toFixed(2)}</strong>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
