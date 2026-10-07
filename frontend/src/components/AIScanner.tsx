'use client';

import React, { useState, useEffect } from 'react';
import { fetchScannerData } from '../lib/api';
import { Cpu, ShieldAlert, Zap, TrendingUp, AlertOctagon } from 'lucide-react';

interface ScannerProps {
  onSelectSymbol: (symbol: string) => void;
}

export const AIScanner: React.FC<ScannerProps> = ({ onSelectSymbol }) => {
  const [activeCategory, setActiveCategory] = useState<string>('OPPORTUNITIES');
  const [data, setData] = useState<any>(null);

  useEffect(() => {
    async function load() {
      const res = await fetchScannerData();
      if (res) setData(res);
    }
    load();
  }, []);

  const categories = [
    { id: 'OPPORTUNITIES', label: 'Opportunities', icon: TrendingUp },
    { id: 'RISKS', label: 'Risks & Downgrades', icon: ShieldAlert },
    { id: 'NO_TRADE', label: 'NO TRADE Safety Filter', icon: AlertOctagon },
    { id: 'MOMENTUM', label: 'High Momentum', icon: Zap },
    { id: 'ALL_SIGNALS', label: 'All Signals', icon: Cpu }
  ];

  const currentList = data ? data[activeCategory] || [] : [];

  const getCurrencySymbol = (currency?: string) => {
    if (currency === 'INR') return '₹';
    if (currency === 'GBP') return '£';
    if (currency === 'JPY') return '¥';
    return '$';
  };

  return (
    <div className="panel" style={{ margin: '20px' }}>
      <div className="panel-header">
        <div className="panel-title">
          <Cpu size={18} color="var(--color-cyan)" />
          <span>ORION-Q AI Market Scanner</span>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Calibrated Signal Discovery</span>
      </div>

      {/* Tab Selectors */}
      <div style={{ display: 'flex', gap: '8px', borderBottom: '1px solid var(--border-color)', paddingBottom: '10px' }}>
        {categories.map((cat) => {
          const Icon = cat.icon;
          const isActive = activeCategory === cat.id;
          return (
            <button
              key={cat.id}
              onClick={() => setActiveCategory(cat.id)}
              style={{
                display: 'flex',
                alignItems: 'center',
                gap: '6px',
                padding: '6px 12px',
                fontSize: '12px',
                fontWeight: 600,
                borderRadius: '4px',
                background: isActive ? 'rgba(6, 182, 212, 0.15)' : 'var(--bg-canvas)',
                color: isActive ? 'var(--color-cyan)' : 'var(--text-secondary)',
                border: `1px solid ${isActive ? 'rgba(6, 182, 212, 0.4)' : 'var(--border-color)'}`
              }}
            >
              <Icon size={14} />
              <span>{cat.label}</span>
            </button>
          );
        })}
      </div>

      {/* Grid Table */}
      <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '12px' }}>
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '11px' }}>
            <th style={{ padding: '10px 12px' }}>SYMBOL</th>
            <th style={{ padding: '10px 12px' }}>PRICE</th>
            <th style={{ padding: '10px 12px' }}>SIGNAL</th>
            <th style={{ padding: '10px 12px' }}>CALIBRATED PROB</th>
            <th style={{ padding: '10px 12px' }}>EXPECTED RETURN</th>
            <th style={{ padding: '10px 12px' }}>CONFORMAL BOUNDS (95%)</th>
            <th style={{ padding: '10px 12px' }}>REGIME</th>
            <th style={{ padding: '10px 12px' }}>STABILITY</th>
          </tr>
        </thead>
        <tbody>
          {currentList.length > 0 ? (
            currentList.map((row: any) => {
              const sigClass = `signal-${row.signal.toLowerCase().replace(/\s+/g, '-')}`;
              const curr = getCurrencySymbol(row.currency);
              const confRange = row.conformal_range;
              return (
                <tr
                  key={row.symbol}
                  onClick={() => onSelectSymbol(row.symbol)}
                  style={{ borderBottom: '1px solid var(--border-color)', cursor: 'pointer' }}
                  onMouseEnter={(e) => (e.currentTarget.style.background = 'var(--bg-panel-hover)')}
                  onMouseLeave={(e) => (e.currentTarget.style.background = 'transparent')}
                >
                  <td style={{ padding: '12px', fontWeight: 800, color: 'var(--color-cyan)', fontFamily: 'var(--font-mono)' }}>
                    {row.symbol}
                  </td>
                  <td style={{ padding: '12px', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>
                    {curr}{row.price?.toFixed(2) || '---'}
                  </td>
                  <td style={{ padding: '12px' }}>
                    <span className={`badge ${sigClass}`}>{row.signal}</span>
                  </td>
                  <td style={{ padding: '12px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-emerald)' }}>
                    {row.calibrated_probability ? `${(row.calibrated_probability * 100).toFixed(1)}%` : 'CALIBRATION UNAVAILABLE'}
                  </td>
                  <td style={{ padding: '12px', fontFamily: 'var(--font-mono)', fontWeight: 600 }} className={row.expected_return_pct >= 0 ? 'positive' : 'negative'}>
                    {row.expected_return_pct !== undefined ? `${row.expected_return_pct > 0 ? '+' : ''}${row.expected_return_pct.toFixed(2)}%` : '---'}
                  </td>
                  <td style={{ padding: '12px', fontFamily: 'var(--font-mono)', fontSize: '11px' }}>
                    {confRange && confRange.lower_bound_pct !== undefined && confRange.lower_bound_pct !== null
                      ? `[${confRange.lower_bound_pct > 0 ? '+' : ''}${confRange.lower_bound_pct.toFixed(1)}%, ${confRange.upper_bound_pct > 0 ? '+' : ''}${confRange.upper_bound_pct.toFixed(1)}%]`
                      : <span style={{ color: 'var(--color-rose)' }}>CONFORMAL UNAVAILABLE</span>}
                  </td>
                  <td style={{ padding: '12px', fontSize: '11px', fontWeight: 600, color: 'var(--color-purple)' }}>
                    {row.regime}
                  </td>
                  <td style={{ padding: '12px', fontSize: '11px', fontWeight: 700, color: 'var(--color-cyan)' }}>
                    {row.stability}
                  </td>
                </tr>
              );
            })
          ) : (
            <tr>
              <td colSpan={8} style={{ textAlign: 'center', padding: '30px', color: 'var(--text-muted)' }}>
                No assets currently match the {activeCategory} criteria.
              </td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  );
};
