'use client';

import React from 'react';
import { Layers } from 'lucide-react';

interface DepthProps {
  quotePrice: number;
  currencySymbol: string;
}

export const MarketDepthVisualizer: React.FC<DepthProps> = ({ quotePrice, currencySymbol }) => {
  // Generate realistic order book levels around current quote price
  const generateBids = () => {
    const bids = [];
    for (let i = 1; i <= 5; i++) {
      const p = quotePrice - i * (quotePrice * 0.001);
      const vol = Math.floor(200 + Math.sin(i * 1.5) * 150 + i * 80);
      bids.push({ price: p, volume: vol });
    }
    return bids;
  };

  const generateAsks = () => {
    const asks = [];
    for (let i = 1; i <= 5; i++) {
      const p = quotePrice + i * (quotePrice * 0.001);
      const vol = Math.floor(180 + Math.cos(i * 1.2) * 140 + i * 75);
      asks.push({ price: p, volume: vol });
    }
    return asks;
  };

  const bids = generateBids();
  const asks = generateAsks();

  const maxVol = Math.max(...bids.map(b => b.volume), ...asks.map(a => a.volume));

  return (
    <div className="panel">
      <div className="panel-header">
        <div className="panel-title">
          <Layers size={16} color="var(--color-cyan)" />
          <span>Market Depth & Order Flow</span>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>L2 Order Book Stream</span>
      </div>

      <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
        {/* Bids Column */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--color-emerald)', fontWeight: 700, paddingBottom: '6px', borderBottom: '1px solid var(--border-color)' }}>
            <span>BID PRICE</span>
            <span>QTY</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '6px' }}>
            {bids.map((b, i) => {
              const pct = (b.volume / maxVol) * 100;
              return (
                <div key={i} style={{ position: 'relative', display: 'flex', justifyContent: 'space-between', padding: '4px 6px', borderRadius: '3px' }}>
                  <div style={{ position: 'absolute', right: 0, top: 0, bottom: 0, width: `${pct}%`, background: 'rgba(16, 185, 129, 0.12)', borderRadius: '3px' }} />
                  <span style={{ color: 'var(--color-emerald)', fontWeight: 600, zIndex: 1 }}>{currencySymbol}{b.price.toFixed(2)}</span>
                  <span style={{ color: 'var(--text-primary)', zIndex: 1 }}>{b.volume}</span>
                </div>
              );
            })}
          </div>
        </div>

        {/* Asks Column */}
        <div>
          <div style={{ display: 'flex', justifyContent: 'space-between', color: 'var(--color-rose)', fontWeight: 700, paddingBottom: '6px', borderBottom: '1px solid var(--border-color)' }}>
            <span>ASK PRICE</span>
            <span>QTY</span>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '4px', marginTop: '6px' }}>
            {asks.map((a, i) => {
              const pct = (a.volume / maxVol) * 100;
              return (
                <div key={i} style={{ position: 'relative', display: 'flex', justifyContent: 'space-between', padding: '4px 6px', borderRadius: '3px' }}>
                  <div style={{ position: 'absolute', left: 0, top: 0, bottom: 0, width: `${pct}%`, background: 'rgba(244, 63, 94, 0.12)', borderRadius: '3px' }} />
                  <span style={{ color: 'var(--color-rose)', fontWeight: 600, zIndex: 1 }}>{currencySymbol}{a.price.toFixed(2)}</span>
                  <span style={{ color: 'var(--text-primary)', zIndex: 1 }}>{a.volume}</span>
                </div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
};
