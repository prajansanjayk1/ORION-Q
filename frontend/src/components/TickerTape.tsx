'use client';

import React, { useState, useEffect } from 'react';
import { MarketQuote } from '../types';
import { fetchQuote } from '../lib/api';
import { wsClient } from '../lib/websocket';
import { ArrowUpRight, ArrowDownRight } from 'lucide-react';

interface TapeProps {
  onSelectSymbol: (symbol: string) => void;
}

const DEFAULT_TICKERS = [
  'RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK',
  'AAPL', 'MSFT', 'NVDA', 'GOOGL', 'AMZN', 'META', 'TSLA', 'SPY'
];

export const TickerTape: React.FC<TapeProps> = ({ onSelectSymbol }) => {
  const [quotes, setQuotes] = useState<Record<string, MarketQuote>>({});

  useEffect(() => {
    async function loadQuotes() {
      const qMap: Record<string, MarketQuote> = {};
      for (const s of DEFAULT_TICKERS) {
        const q = await fetchQuote(s);
        if (q) qMap[s] = q;
      }
      setQuotes(qMap);
    }
    loadQuotes();

    wsClient.subscribe(DEFAULT_TICKERS);

    const handleMessage = (evt: any) => {
      if (evt.type === 'PRICE_UPDATE' && evt.symbol) {
        const qData: MarketQuote = evt.data;
        setQuotes((prev) => ({
          ...prev,
          [evt.symbol]: qData
        }));
      }
    };

    wsClient.connect(handleMessage, null);
    return () => {
      wsClient.unsubscribe(DEFAULT_TICKERS);
    };
  }, []);

  const getCurrSymbol = (exchange?: string, currency?: string) => {
    if (currency === 'INR' || exchange === 'NSE' || exchange === 'BSE') return '₹';
    if (currency === 'GBP' || exchange === 'LSE') return '£';
    if (currency === 'JPY' || exchange === 'TSE') return '¥';
    return '$';
  };

  return (
    <div style={{
      width: '100%',
      background: 'var(--bg-canvas)',
      borderBottom: '1px solid var(--border-color)',
      overflow: 'hidden',
      whiteSpace: 'nowrap',
      display: 'flex',
      alignItems: 'center',
      padding: '6px 0',
      fontSize: '11px',
      fontFamily: 'var(--font-mono)'
    }}>
      <div style={{
        display: 'inline-flex',
        gap: '24px',
        animation: 'scrollTape 40s linear infinite'
      }}>
        {DEFAULT_TICKERS.concat(DEFAULT_TICKERS).map((sym, idx) => {
          const q = quotes[sym];
          const curr = getCurrSymbol(q?.exchange, q?.currency);
          const isPos = q ? q.change >= 0 : true;

          return (
            <div
              key={`${sym}-${idx}`}
              onClick={() => onSelectSymbol(sym)}
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '8px',
                cursor: 'pointer',
                padding: '2px 8px',
                borderRadius: '4px',
                background: 'var(--bg-panel-hover)',
                transition: 'background 0.2s ease'
              }}
            >
              <span style={{ fontWeight: 800, color: 'var(--color-cyan)' }}>{sym}</span>
              <span>{curr}{q ? q.price.toFixed(2) : '---'}</span>
              <span className={q ? (isPos ? 'positive' : 'negative') : ''} style={{ display: 'flex', alignItems: 'center', fontWeight: 700 }}>
                {q && (isPos ? <ArrowUpRight size={12} /> : <ArrowDownRight size={12} />)}
                {q ? `${q.change > 0 ? '+' : ''}${q.percent_change.toFixed(2)}%` : '---'}
              </span>
              <span style={{
                fontSize: '9px',
                padding: '1px 4px',
                borderRadius: '2px',
                background: q?.data_state === 'LIVE' ? 'rgba(16,185,129,0.2)' : 'rgba(6,182,212,0.2)',
                color: q?.data_state === 'LIVE' ? 'var(--color-emerald)' : 'var(--color-cyan)'
              }}>
                ● 1s TICK
              </span>
            </div>
          );
        })}
      </div>
    </div>
  );
};
