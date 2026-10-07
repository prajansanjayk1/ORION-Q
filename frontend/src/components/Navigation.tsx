'use client';

import React from 'react';
import {
  BarChart2,
  Monitor,
  Cpu,
  Briefcase,
  ShieldCheck,
  History,
  MessageSquareCode,
} from 'lucide-react';

interface NavProps {
  activeTab: string;
  setActiveTab: (tab: string) => void;
}

const TABS = [
  { id: 'home',      label: 'Market Overview',       icon: BarChart2 },
  { id: 'terminal',  label: 'Terminal UI',            icon: Monitor },
  { id: 'scanner',   label: 'Quantitative Scanner',   icon: Cpu },
  { id: 'portfolio', label: 'Portfolio & Risk',        icon: Briefcase },
  { id: 'registry',  label: 'Model Governance',       icon: ShieldCheck },
  { id: 'backtest',  label: 'Backtester',             icon: History },
  { id: 'copilot',   label: 'ORION-Q Copilot',        icon: MessageSquareCode },
];

export const Navigation: React.FC<NavProps> = ({ activeTab, setActiveTab }) => {
  return (
    <nav
      style={{
        display: 'flex',
        alignItems: 'stretch',
        background: 'var(--bg-header)',
        borderBottom: '1px solid var(--border-color)',
        padding: '0 12px',
        height: '38px',
        flexShrink: 0,
        overflowX: 'auto',
        scrollbarWidth: 'none',
      }}
    >
      {TABS.map((tab) => {
        const Icon = tab.icon;
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            onClick={() => setActiveTab(tab.id)}
            style={{
              display: 'inline-flex',
              alignItems: 'center',
              gap: '6px',
              padding: '0 14px',
              height: '38px',
              fontSize: '12px',
              fontWeight: isActive ? 600 : 400,
              color: isActive ? 'var(--color-cyan)' : 'var(--text-muted)',
              background: isActive ? 'rgba(0, 212, 232, 0.06)' : 'transparent',
              borderBottom: `2px solid ${isActive ? 'var(--color-cyan)' : 'transparent'}`,
              borderTop: 'none',
              borderLeft: 'none',
              borderRight: 'none',
              borderRadius: 0,
              cursor: 'pointer',
              whiteSpace: 'nowrap',
              letterSpacing: '0.01em',
              transition: 'color 0.15s ease, border-color 0.15s ease, background 0.15s ease',
              flexShrink: 0,
            }}
            onMouseEnter={(e) => {
              if (!isActive) {
                e.currentTarget.style.color = 'var(--text-secondary)';
                e.currentTarget.style.background = 'rgba(255,255,255,0.025)';
              }
            }}
            onMouseLeave={(e) => {
              if (!isActive) {
                e.currentTarget.style.color = 'var(--text-muted)';
                e.currentTarget.style.background = 'transparent';
              }
            }}
          >
            <Icon size={14} style={{ opacity: isActive ? 1 : 0.6 }} />
            <span>{tab.label}</span>
          </button>
        );
      })}
    </nav>
  );
};
