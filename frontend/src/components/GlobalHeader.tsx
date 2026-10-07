'use client';

import React, { useState, useEffect } from 'react';
import { GlobalMarketStatus, MarketMode, ConnectionState } from '../types';
import { fetchMarketSession } from '../lib/api';
import { Search, Activity, Globe, Wifi, WifiOff, Sun, Moon } from 'lucide-react';
import { wsClient } from '../lib/websocket';

interface HeaderProps {
  mode: MarketMode;
  setMode: (mode: MarketMode) => void;
  onSearchSymbol: (symbol: string) => void;
  latencyMs: number;
  isLightTheme?: boolean;
  onToggleTheme?: () => void;
}

export const GlobalHeader: React.FC<HeaderProps> = ({ mode, setMode, onSearchSymbol, latencyMs, isLightTheme = false, onToggleTheme }) => {
  const [status, setStatus] = useState<GlobalMarketStatus | null>(null);
  const [searchInput, setSearchInput] = useState('');
  const [connState, setConnState] = useState<ConnectionState>('DISCONNECTED');
  const [localTime, setLocalTime] = useState('');

  useEffect(() => {
    async function loadSession() {
      const data = await fetchMarketSession(mode);
      if (data) setStatus(data);
    }
    loadSession();
    const interval = setInterval(loadSession, 15000);
    const timeInterval = setInterval(() => {
      setLocalTime(new Date().toLocaleTimeString('en-IN', { hour12: false }));
    }, 1000);
    return () => {
      clearInterval(interval);
      clearInterval(timeInterval);
    };
  }, [mode]);

  useEffect(() => {
    wsClient.connect(null, (state) => setConnState(state));
  }, []);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (searchInput.trim()) {
      onSearchSymbol(searchInput.trim().toUpperCase());
      setSearchInput('');
    }
  };

  const connColor =
    connState === 'CONNECTED' ? 'var(--color-emerald)' :
    connState === 'DEGRADED' ? 'var(--color-amber)' :
    connState === 'CONNECTING' || connState === 'RECONNECTING' ? 'var(--color-cyan)' :
    'var(--color-rose)';

  const connLabel =
    connState === 'CONNECTED' ? 'LIVE' :
    connState === 'DEGRADED' ? 'DEGRADED' :
    connState === 'CONNECTING' ? 'CONNECTING' :
    connState === 'RECONNECTING' ? 'RECONNECTING' :
    'OFFLINE';

  const ConnIcon = connState === 'DISCONNECTED' ? WifiOff : Wifi;

  return (
    <header
      className="terminal-header"
      style={{
        background: 'var(--bg-header)',
        borderBottom: '1px solid var(--border-color)',
        height: '44px',
        display: 'flex',
        alignItems: 'center',
        padding: '0 14px',
        gap: '12px',
      }}
    >
      {/* ── LEFT: Logo + Subtitle ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '10px', flexShrink: 0 }}>
        <div style={{
          background: 'linear-gradient(135deg, #00d4e8 0%, #a855f7 100%)',
          padding: '4px 10px',
          borderRadius: '5px',
          fontWeight: 800,
          letterSpacing: '0.1em',
          color: '#000',
          fontSize: '13px',
          fontFamily: 'var(--font-mono)',
          lineHeight: 1,
        }}>
          ORION-Q
        </div>
        <span style={{
          fontSize: '10px',
          color: 'var(--text-muted)',
          fontWeight: 600,
          letterSpacing: '0.07em',
          fontFamily: 'var(--font-mono)',
          lineHeight: 1,
        }}>
          QUANTITATIVE TERMINAL v1.1
        </span>
      </div>

      {/* Divider */}
      <div style={{ width: '1px', height: '20px', background: 'var(--border-color)', flexShrink: 0 }} />

      {/* ── CENTER: Mode Switcher ── */}
      <div style={{
        display: 'flex',
        background: 'rgba(10, 14, 26, 0.8)',
        border: '1px solid var(--border-color)',
        borderRadius: '5px',
        padding: '2px',
        gap: '1px',
        flexShrink: 0,
      }}>
        {(['AUTO', 'INDIA', 'US', 'GLOBAL'] as MarketMode[]).map((m) => (
          <button
            key={m}
            onClick={() => setMode(m)}
            style={{
              padding: '3px 10px',
              fontSize: '11px',
              fontWeight: mode === m ? 700 : 500,
              borderRadius: '3px',
              background: mode === m ? 'var(--color-cyan)' : 'transparent',
              color: mode === m ? '#000' : 'var(--text-muted)',
              border: 'none',
              cursor: 'pointer',
              fontFamily: 'var(--font-mono)',
              letterSpacing: '0.05em',
              transition: 'all 0.15s ease',
            }}
          >
            {m}
          </button>
        ))}
      </div>

      {/* ── SEARCH (grows to fill center) ── */}
      <form
        onSubmit={handleSearchSubmit}
        style={{ position: 'relative', flex: 1, minWidth: '160px', maxWidth: '280px' }}
      >
        <Search
          size={13}
          style={{
            position: 'absolute',
            left: '9px',
            top: '50%',
            transform: 'translateY(-50%)',
            color: 'var(--text-muted)',
            pointerEvents: 'none',
          }}
        />
        <input
          type="text"
          placeholder="Search ticker…"
          value={searchInput}
          onChange={(e) => setSearchInput(e.target.value)}
          style={{
            width: '100%',
            background: 'rgba(10,14,26,0.8)',
            border: '1px solid var(--border-color)',
            borderRadius: '4px',
            padding: '5px 10px 5px 28px',
            color: 'var(--text-primary)',
            fontSize: '12px',
            outline: 'none',
            height: '28px',
            fontFamily: 'var(--font-sans)',
            transition: 'border-color 0.15s ease',
          }}
          onFocus={(e) => (e.target.style.borderColor = 'rgba(0,212,232,0.5)')}
          onBlur={(e) => (e.target.style.borderColor = 'var(--border-color)')}
        />
      </form>

      {/* Spacer */}
      <div style={{ flex: 1 }} />

      {/* ── RIGHT CLUSTER ── */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '14px', flexShrink: 0 }}>
        {/* Time */}
        <span style={{ fontFamily: 'var(--font-mono)', fontSize: '12px', color: 'var(--text-muted)', letterSpacing: '0.03em' }}>
          {localTime}
        </span>

        {/* India Session */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <span style={{ fontSize: '13px', lineHeight: 1 }}>🇮🇳</span>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>NSE</span>
          <span className={`badge ${status?.india_session?.status === 'OPEN' ? 'badge-live' : 'badge-closed'}`}>
            {status?.india_session?.status === 'OPEN' ? '● OPEN' : status?.india_session?.status || 'CLOSED'}
          </span>
        </div>

        {/* US Session */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px' }}>
          <span style={{ fontSize: '13px', lineHeight: 1 }}>🇺🇸</span>
          <span style={{ fontSize: '10px', color: 'var(--text-muted)', fontFamily: 'var(--font-mono)', fontWeight: 600 }}>NYSE</span>
          <span className={`badge ${status?.us_session?.status === 'OPEN' ? 'badge-live' : 'badge-closed'}`}>
            {status?.us_session?.status === 'OPEN' ? '● OPEN' : status?.us_session?.status || 'CLOSED'}
          </span>
        </div>

        {/* Focus Badge */}
        <div style={{
          display: 'flex', alignItems: 'center', gap: '4px',
          background: 'rgba(0,212,232,0.08)',
          border: '1px solid rgba(0,212,232,0.2)',
          padding: '3px 8px',
          borderRadius: '4px',
        }}>
          <Globe size={11} color="var(--color-cyan)" />
          <span style={{ fontSize: '10px', color: 'var(--color-cyan)', fontWeight: 700, fontFamily: 'var(--font-mono)', letterSpacing: '0.06em' }}>
            {status?.active_market || 'GLOBAL'}
          </span>
        </div>

        {/* Connection Badge */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '5px', fontFamily: 'var(--font-mono)', fontSize: '10px' }}>
          <ConnIcon size={12} color={connColor} />
          <span style={{ color: connColor, fontWeight: 700, letterSpacing: '0.05em' }}>{connLabel}</span>
        </div>

        {/* Theme Toggle Button */}
        {onToggleTheme && (
          <button
            onClick={onToggleTheme}
            title={isLightTheme ? 'Switch to Dark Terminal' : 'Switch to Light Mode'}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '4px',
              padding: '4px 8px',
              borderRadius: '4px',
              border: '1px solid var(--border-color)',
              background: 'var(--bg-canvas)',
              color: isLightTheme ? '#f59e0b' : 'var(--color-cyan)',
              fontSize: '11px',
              fontWeight: 600,
              cursor: 'pointer',
              transition: 'all 0.15s ease',
            }}
          >
            {isLightTheme ? <Moon size={12} /> : <Sun size={12} />}
            <span style={{ fontSize: '10px', fontFamily: 'var(--font-mono)' }}>
              {isLightTheme ? 'DARK' : 'LIGHT'}
            </span>
          </button>
        )}

        {/* Latency */}
        <div style={{ display: 'flex', alignItems: 'center', gap: '4px', fontFamily: 'var(--font-mono)', fontSize: '10px', color: 'var(--text-muted)' }}>
          <Activity size={11} color={connState === 'CONNECTED' ? 'var(--color-emerald)' : 'var(--text-muted)'} />
          <span>
            LAT:{' '}
            <strong style={{ color: connState === 'CONNECTED' && latencyMs > 0 ? 'var(--color-emerald)' : 'var(--text-muted)' }}>
              {connState === 'CONNECTED' && latencyMs > 0 ? `${latencyMs}ms` : '---'}
            </strong>
          </span>
        </div>
      </div>
    </header>
  );
};
