'use client';

import React, { useState, useEffect } from 'react';
import { GlobalHeader } from '../components/GlobalHeader';
import { TickerTape } from '../components/TickerTape';
import { Navigation } from '../components/Navigation';
import { CommandCenter } from '../components/CommandCenter';
import { StockDetailView } from '../components/StockDetailView';
import { AIScanner } from '../components/AIScanner';
import { PortfolioView } from '../components/PortfolioView';
import { ModelRegistryView } from '../components/ModelRegistryView';
import { BacktestView } from '../components/BacktestView';
import { CopilotView } from '../components/CopilotView';
import { MarketMode } from '../types';
import { MarketWSClient } from '../lib/websocket';

export default function Home() {
  const [activeTab, setActiveTab] = useState<string>('home');
  const [marketMode, setMarketMode] = useState<MarketMode>('AUTO');
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AAPL');
  const [latencyMs, setLatencyMs] = useState<number>(24);

  useEffect(() => {
    document.body.classList.remove('light-theme');
  }, []);

  useEffect(() => {
    const wsClient = new MarketWSClient();
    wsClient.connect((event: any) => {
      if (event.websocket_timestamp && event.frontend_received_timestamp) {
        const measured = Math.round((event.frontend_received_timestamp - event.websocket_timestamp) * 1000);
        if (measured >= 0 && measured < 1000) {
          setLatencyMs(measured);
        }
      }
    });

    return () => {
      wsClient.close();
    };
  }, []);

  const handleSelectSymbol = (symbol: string) => {
    setSelectedSymbol(symbol);
    setActiveTab('terminal');
  };

  return (
    <div className="terminal-layout">
      {/* Global Header */}
      <GlobalHeader
        mode={marketMode}
        setMode={setMarketMode}
        onSearchSymbol={handleSelectSymbol}
        latencyMs={latencyMs}
      />

      {/* Real Live Ticker Tape */}
      <TickerTape onSelectSymbol={handleSelectSymbol} />

      {/* Main Navigation */}
      <Navigation activeTab={activeTab} setActiveTab={setActiveTab} />

      {/* View Switcher */}
      <main style={{ flex: 1 }}>
        {activeTab === 'home' && <CommandCenter onSelectSymbol={handleSelectSymbol} />}
        {activeTab === 'terminal' && <StockDetailView symbol={selectedSymbol} />}
        {activeTab === 'scanner' && <AIScanner onSelectSymbol={handleSelectSymbol} />}
        {activeTab === 'portfolio' && <PortfolioView />}
        {activeTab === 'registry' && <ModelRegistryView />}
        {activeTab === 'backtest' && <BacktestView />}
        {activeTab === 'copilot' && <CopilotView />}
      </main>
    </div>
  );
}
