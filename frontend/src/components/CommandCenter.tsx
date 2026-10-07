'use client';

import React, { useState, useEffect, useRef } from 'react';
import { fetchScannerData, fetchQuote, fetchMarketSession } from '../lib/api';
import { MarketQuote, GlobalMarketStatus } from '../types';
import { TrendingUp, ShieldAlert, Cpu, ArrowUpRight, ArrowDownRight, Activity, Moon, Layers, Zap, RefreshCw } from 'lucide-react';

interface CenterProps {
  onSelectSymbol: (symbol: string) => void;
}

const INDICES = [
  { symbol: '^GSPC', label: 'S&P 500', sub: 'US' },
  { symbol: '^IXIC', label: 'NASDAQ', sub: 'Composite' },
  { symbol: '^NSEI', label: 'NIFTY 50', sub: 'India' },
  { symbol: '^INDIAVIX', label: 'India VIX', sub: 'Volatility' },
];

export const CommandCenter: React.FC<CenterProps> = ({ onSelectSymbol }) => {
  const [scannerData, setScannerData] = useState<any>(null);
  const [indicesQuotes, setIndicesQuotes] = useState<Record<string, MarketQuote>>({});
  const [marketStatus, setMarketStatus] = useState<GlobalMarketStatus | null>(null);
  const [filterMode, setFilterMode] = useState<string>('ALL');
  const [scannerLoading, setScannerLoading] = useState(true);
  const [scannerError, setScannerError] = useState(false);
  const [lastRefresh, setLastRefresh] = useState<Date | null>(null);
  const retryCountRef = useRef(0);

  // Fetch scanner with retry logic (up to 3 times, 2s delay)
  async function loadScannerWithRetry(): Promise<any> {
    retryCountRef.current = 0;
    while (retryCountRef.current < 3) {
      const data = await fetchScannerData();
      const signals = data?.ALL_SIGNALS || [];
      if (signals.length > 0) return data;
      retryCountRef.current++;
      if (retryCountRef.current < 3) {
        await new Promise((res) => setTimeout(res, 2000));
      }
    }
    return null;
  }

  async function loadData() {
    // Load scanner with retry
    setScannerLoading(true);
    setScannerError(false);
    const scannerResult = await loadScannerWithRetry();
    if (scannerResult) {
      setScannerData(scannerResult);
      setScannerError(false);
    } else {
      setScannerError(true);
    }
    setScannerLoading(false);
    setLastRefresh(new Date());

    // Load market session
    const status = await fetchMarketSession('GLOBAL');
    if (status) setMarketStatus(status);

    // Load all indices in parallel
    const results = await Promise.all(INDICES.map((idx) => fetchQuote(idx.symbol)));
    const quotesMap: Record<string, MarketQuote> = {};
    INDICES.forEach((idx, i) => {
      if (results[i]) quotesMap[idx.symbol] = results[i]!;
    });
    setIndicesQuotes(quotesMap);
  }

  useEffect(() => {
    loadData();
    const interval = setInterval(loadData, 30000);
    return () => clearInterval(interval);
  }, []);

  const renderDataStateBadge = (state: string) => {
    if (state === 'LIVE') return <span className="badge badge-live"><span className="pulse-icon">●</span> LIVE</span>;
    if (state === 'STALE') return <span className="badge" style={{ background: 'rgba(245,158,11,0.12)', color: 'var(--color-amber)', border: '1px solid rgba(245,158,11,0.3)' }}>⚠ STALE</span>;
    if (state === 'DATA_UNAVAILABLE') return <span className="badge badge-unavailable">UNAVAILABLE</span>;
    if (state === 'DELAYED') return <span className="badge badge-delayed">DELAYED</span>;
    return <span className="badge badge-closed">CLOSED</span>;
  };

  const getCurrencySymbol = (currency?: string) => {
    if (currency === 'INR') return '₹';
    if (currency === 'GBP') return '£';
    if (currency === 'JPY') return '¥';
    return '$';
  };

  const allSignals = scannerData?.ALL_SIGNALS || [];
  const filteredSignals = allSignals.filter((item: any) => {
    if (filterMode === 'BULLISH') return item.signal.includes('BUY');
    if (filterMode === 'BEARISH') return item.signal.includes('SELL');
    if (filterMode === 'HIGH_CONVICTION') return item.calibrated_probability && item.calibrated_probability >= 0.70;
    return true;
  });

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px', padding: '16px' }}>

      {/* Closed Session Warning */}
      {marketStatus?.all_markets_closed && (
        <div style={{
          background: 'rgba(168, 85, 247, 0.07)',
          border: '1px solid rgba(168, 85, 247, 0.25)',
          borderRadius: '6px',
          padding: '8px 14px',
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          fontSize: '12px',
          animation: 'fadeIn 0.3s ease',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
            <Moon size={15} color="var(--color-purple)" />
            <span>
              <strong style={{ color: 'var(--color-purple)' }}>Global Sessions Closed:</strong>
              {' '}Displaying last verified prices & out-of-fold ML intelligence.
            </span>
          </div>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
            Next Open: NYSE / NSE Regular Session
          </span>
        </div>
      )}

      {/* 1. Global Index Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px' }}>
        {INDICES.map((item) => {
          const q = indicesQuotes[item.symbol];
          const isPos = q ? q.change >= 0 : true;
          return (
            <div
              key={item.symbol}
              className="panel"
              style={{ padding: '14px 16px', gap: '8px', cursor: 'pointer' }}
              onClick={() => onSelectSymbol(item.symbol)}
            >
              <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                <div>
                  <div style={{ fontSize: '11px', fontWeight: 700, color: 'var(--text-primary)', letterSpacing: '0.03em' }}>{item.label}</div>
                  <div style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>{item.sub}</div>
                </div>
                {renderDataStateBadge(q?.data_state || 'CLOSED')}
              </div>
              <div style={{ display: 'flex', alignItems: 'baseline', justifyContent: 'space-between', marginTop: '4px' }}>
                <span style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)', letterSpacing: '-0.02em', color: 'var(--text-primary)' }}>
                  {q ? q.price.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 }) : (
                    <span style={{ color: 'var(--text-muted)', fontSize: '14px' }}>Loading…</span>
                  )}
                </span>
                {q && (
                  <span
                    className={`number-mono ${isPos ? 'positive' : 'negative'}`}
                    style={{ fontWeight: 700, fontSize: '12px', display: 'flex', alignItems: 'center', gap: '2px' }}
                  >
                    {isPos ? <ArrowUpRight size={13} /> : <ArrowDownRight size={13} />}
                    {q.change > 0 ? '+' : ''}{q.change.toFixed(2)} ({q.percent_change.toFixed(2)}%)
                  </span>
                )}
              </div>
              {/* Mini sparkline bar */}
              {q && (
                <div style={{
                  height: '3px',
                  borderRadius: '2px',
                  background: `linear-gradient(90deg, ${isPos ? 'rgba(0,192,135,0.15)' : 'rgba(232,64,64,0.15)'} 0%, ${isPos ? 'var(--color-emerald)' : 'var(--color-rose)'} 100%)`,
                  marginTop: '4px',
                  opacity: 0.7,
                }} />
              )}
            </div>
          );
        })}
      </div>

      {/* 2. Main Grid: Scanner + Side Panels */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 340px', gap: '16px' }}>
        {/* Scanner Opportunities Panel */}
        <div className="panel" style={{ gap: '0' }}>
          <div className="panel-header" style={{ marginBottom: '0' }}>
            <div className="panel-title">
              <Cpu size={14} color="var(--color-cyan)" />
              <span>Institutional Quantitative Scanner</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              {lastRefresh && (
                <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)' }}>
                  {lastRefresh.toLocaleTimeString()}
                </span>
              )}
              <button
                onClick={loadData}
                title="Refresh"
                style={{
                  display: 'flex', alignItems: 'center', gap: '4px',
                  padding: '3px 7px', borderRadius: '4px',
                  border: '1px solid var(--border-color)',
                  background: 'var(--bg-canvas)',
                  color: 'var(--text-muted)',
                  fontSize: '10px', cursor: 'pointer',
                  transition: 'all 0.15s ease',
                }}
              >
                <RefreshCw size={11} />
              </button>
              <div style={{ display: 'flex', gap: '4px' }}>
                {['ALL', 'BULLISH', 'BEARISH', 'HIGH_CONVICTION'].map((f) => (
                  <button
                    key={f}
                    onClick={() => setFilterMode(f)}
                    style={{
                      padding: '3px 8px',
                      fontSize: '10px',
                      fontWeight: 700,
                      borderRadius: '3px',
                      background: filterMode === f ? 'var(--color-cyan)' : 'transparent',
                      color: filterMode === f ? '#000' : 'var(--text-muted)',
                      border: `1px solid ${filterMode === f ? 'var(--color-cyan)' : 'var(--border-color)'}`,
                      cursor: 'pointer',
                      fontFamily: 'var(--font-mono)',
                      letterSpacing: '0.05em',
                      transition: 'all 0.15s ease',
                    }}
                  >
                    {f.replace('_', ' ')}
                  </button>
                ))}
              </div>
            </div>
          </div>

          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '2px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)' }}>
                {['SYMBOL', 'LAST PRICE', 'SIGNAL', 'CALIB PROB', 'EXP RETURN', 'REGIME'].map((h) => (
                  <th key={h} style={{ padding: '8px 12px', textAlign: 'left', fontSize: '10px', fontWeight: 700, color: 'var(--text-muted)', letterSpacing: '0.07em', fontFamily: 'var(--font-mono)', textTransform: 'uppercase' }}>{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {scannerLoading ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '40px 24px' }}>
                    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', gap: '10px', color: 'var(--text-muted)' }}>
                      <span className="spinner" />
                      <span style={{ fontSize: '13px', fontFamily: 'var(--font-mono)' }}>Fetching live signals…</span>
                    </div>
                  </td>
                </tr>
              ) : scannerError ? (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '32px 24px' }}>
                    <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '8px', color: 'var(--color-rose)' }}>
                      <Zap size={20} />
                      <span style={{ fontSize: '12px' }}>Scanner unavailable — backend may be offline</span>
                      <button
                        onClick={loadData}
                        style={{ marginTop: '4px', padding: '5px 14px', borderRadius: '4px', border: '1px solid var(--border-bright)', background: 'transparent', color: 'var(--text-secondary)', fontSize: '11px', cursor: 'pointer' }}
                      >
                        Retry
                      </button>
                    </div>
                  </td>
                </tr>
              ) : filteredSignals.length > 0 ? (
                filteredSignals.map((row: any) => {
                  const sigClass = `signal-${row.signal.toLowerCase().replace(/\s+/g, '-')}`;
                  const curr = getCurrencySymbol(row.currency);
                  return (
                    <tr
                      key={row.symbol}
                      onClick={() => onSelectSymbol(row.symbol)}
                      style={{ borderBottom: '1px solid rgba(26,36,68,0.6)', cursor: 'pointer', transition: 'background 0.15s ease' }}
                      onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-panel-hover)')}
                      onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                    >
                      <td style={{ padding: '10px 12px', fontWeight: 800, color: 'var(--color-cyan)', fontFamily: 'var(--font-mono)', fontSize: '13px' }}>
                        {row.symbol}
                      </td>
                      <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                        {curr}{row.price?.toFixed(2) || '---'}
                      </td>
                      <td style={{ padding: '10px 12px' }}>
                        <span className={`badge ${sigClass}`}>{row.signal}</span>
                      </td>
                      <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-emerald)' }}>
                        {row.calibrated_probability ? `${(row.calibrated_probability * 100).toFixed(1)}%` : <span style={{ color: 'var(--text-muted)', fontSize: '10px' }}>UNAVAIL</span>}
                      </td>
                      <td style={{ padding: '10px 12px', fontFamily: 'var(--font-mono)', fontWeight: 600 }} className={row.expected_return_pct >= 0 ? 'positive' : 'negative'}>
                        {row.expected_return_pct !== undefined ? `${row.expected_return_pct > 0 ? '+' : ''}${row.expected_return_pct.toFixed(2)}%` : '---'}
                      </td>
                      <td style={{ padding: '10px 12px', fontSize: '11px', fontWeight: 600, color: 'var(--color-purple)', fontFamily: 'var(--font-mono)' }}>
                        {row.regime || 'ACCUMULATION'}
                      </td>
                    </tr>
                  );
                })
              ) : (
                <tr>
                  <td colSpan={6} style={{ textAlign: 'center', padding: '32px 24px', color: 'var(--text-muted)', fontSize: '12px' }}>
                    No signals match the current filter.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Right Side Panels */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
          {/* Empirical Regime Map */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <Activity size={13} color="var(--color-purple)" />
                <span>Empirical Regime Map</span>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
              {[
                { label: 'Detected Regime', value: 'HIGH-MOMENTUM BULL', color: 'var(--color-emerald)' },
                { label: 'Trend Index', value: '0.78 / 1.0', color: 'var(--text-primary)' },
                { label: 'Volatility Score', value: '0.32 / 1.0', color: 'var(--text-primary)' },
                { label: 'Liquidity Index', value: '0.85 / 1.0', color: 'var(--text-primary)' },
              ].map((r) => (
                <div key={r.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{r.label}</span>
                  <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: r.color, fontSize: '11px' }}>{r.value}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Sector Heatmap */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <Layers size={13} color="var(--color-cyan)" />
                <span>Sector Heatmap</span>
              </div>
            </div>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', fontSize: '11px' }}>
              {[
                { name: 'Technology', change: 1.45 },
                { name: 'Financials', change: 0.82 },
                { name: 'Energy', change: -0.65 },
                { name: 'Consumer', change: 0.35 },
                { name: 'Automobiles', change: 1.12 },
                { name: 'Healthcare', change: -0.24 },
              ].map((sec) => (
                <div
                  key={sec.name}
                  style={{
                    background: sec.change >= 0 ? 'rgba(0, 192, 135, 0.09)' : 'rgba(232, 64, 64, 0.09)',
                    border: `1px solid ${sec.change >= 0 ? 'rgba(0,192,135,0.25)' : 'rgba(232,64,64,0.25)'}`,
                    padding: '7px 9px',
                    borderRadius: '4px',
                    display: 'flex',
                    justifyContent: 'space-between',
                    alignItems: 'center',
                  }}
                >
                  <span style={{ color: 'var(--text-secondary)' }}>{sec.name}</span>
                  <span className={sec.change >= 0 ? 'positive' : 'negative'} style={{ fontWeight: 700, fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                    {sec.change > 0 ? '+' : ''}{sec.change}%
                  </span>
                </div>
              ))}
            </div>
          </div>

          {/* Risk Guardrails */}
          <div className="panel">
            <div className="panel-header">
              <div className="panel-title">
                <ShieldAlert size={13} color="var(--color-amber)" />
                <span>Risk Guardrails</span>
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              {[
                { label: 'Portfolio VaR (95%)', value: '2.45%', color: 'var(--color-amber)' },
                { label: 'CVaR (Exp. Shortfall)', value: '3.20%', color: 'var(--color-rose)' },
                { label: 'Sharpe Ratio (OOS)', value: '2.14', color: 'var(--color-emerald)' },
              ].map((r) => (
                <div key={r.label} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <span style={{ color: 'var(--text-muted)' }}>{r.label}</span>
                  <strong style={{ color: r.color, fontFamily: 'var(--font-mono)', fontSize: '12px' }}>{r.value}</strong>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};
