'use client';

import React, { useState, useEffect } from 'react';
import { fetchPrediction } from '../lib/api';
import { PredictionResult } from '../types';
import { FinancialChart } from './FinancialChart';
import { MarketDepthVisualizer } from './MarketDepthVisualizer';
import { Cpu, ShieldCheck, Zap, AlertTriangle, Layers, BarChart2, RefreshCw, CheckCircle, XCircle, AlertCircle } from 'lucide-react';

interface DetailProps {
  symbol: string;
}

export const StockDetailView: React.FC<DetailProps> = ({ symbol }) => {
  const [data, setData] = useState<PredictionResult | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [showProvenance, setShowProvenance] = useState(false);

  useEffect(() => {
    async function loadStock() {
      setLoading(true);
      const res = await fetchPrediction(symbol);
      if (res && res.signal) {
        setData(res);
      } else {
        setData(null);
      }
      setLoading(false);
    }
    loadStock();
  }, [symbol]);

  if (loading) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
        <RefreshCw className="animate-spin" size={24} style={{ marginBottom: '12px' }} />
        <div>Computing ORION-Q Parliament & Conformal Intelligence for {symbol}...</div>
      </div>
    );
  }

  if (!data || !data.signal) {
    return (
      <div style={{ padding: '40px', textAlign: 'center', color: 'var(--color-rose)' }}>
        <AlertTriangle size={24} style={{ marginBottom: '12px' }} />
        <div>DATA UNAVAILABLE — Could not resolve prediction feed for {symbol}</div>
      </div>
    );
  }

  const signalStr = data.signal.signal || 'NO TRADE';
  const sigClass = `signal-${signalStr.toLowerCase().replace(/\s+/g, '-')}`;

  const topPosDrivers = data.explainability?.top_positive_drivers || [];
  const topNegDrivers = data.explainability?.top_negative_drivers || [];
  const flipFactors = data.counterfactuals?.flip_factors || [];
  const leaderboardEntries = data.model_leaderboard ? Object.entries(data.model_leaderboard) : [];

  const currSym = data.currency === 'INR' ? '₹' : data.currency === 'GBP' ? '£' : data.currency === 'JPY' ? '¥' : '$';

  const renderMarketBadge = () => {
    const s = data.market_session_state;
    if (s === 'OPEN') return <span className="badge badge-live">● OPEN</span>;
    if (s === 'PRE_MARKET') return <span className="badge" style={{ background: 'var(--color-cyan)', color: '#000' }}>PRE-MARKET</span>;
    if (s === 'POST_MARKET') return <span className="badge" style={{ background: 'var(--color-purple)', color: '#fff' }}>POST-MARKET</span>;
    if (s === 'HALTED') return <span className="badge" style={{ background: 'var(--color-amber)', color: '#000' }}>⚠ HALTED</span>;
    if (s === 'HOLIDAY') return <span className="badge badge-closed">HOLIDAY</span>;
    if (s === 'CLOSED') return <span className="badge badge-closed">MARKET CLOSED</span>;
    return <span className="badge badge-closed">SESSION UNKNOWN</span>;
  };

  const renderQualityIcon = (status?: string) => {
    if (status === 'AVAILABLE') return <CheckCircle size={14} color="var(--color-emerald)" />;
    if (status === 'LIMITED') return <AlertCircle size={14} color="var(--color-amber)" />;
    return <XCircle size={14} color="var(--color-rose)" />;
  };

  const getConsensusColor = (c: string) => {
    if (c === 'HIGH') return 'var(--color-emerald)';
    if (c === 'MEDIUM') return 'var(--color-amber)';
    return 'var(--color-rose)';
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '20px' }}>
      {/* Header Info */}
      <div className="panel" style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <h1 style={{ fontSize: '24px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-cyan)' }}>
              {data.symbol}
            </h1>
            {renderMarketBadge()}
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Exchange: {data.market_session}</span>
          </div>
          <div style={{ display: 'flex', gap: '24px', marginTop: '12px' }}>
            <div>
              <div style={{ fontSize: '10px', color: 'var(--text-muted)' }}>REGULAR SESSION</div>
              <div style={{ fontSize: '22px', fontWeight: 700, fontFamily: 'var(--font-mono)' }}>
                {currSym}{data.quote_price ? data.quote_price.toFixed(2) : '0.00'}
              </div>
            </div>
          </div>
        </div>

        {data.quality_gate?.gate_passed ? (
          <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>CALIBRATED BULLISH PROB</div>
              <div style={{ fontSize: '22px', fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-emerald)' }}>
                {data.signal.calibrated_probability !== undefined && data.signal.calibrated_probability !== null
                  ? `${(data.signal.calibrated_probability * 100).toFixed(1)}%`
                  : 'CALIBRATION UNAVAILABLE'}
              </div>
            </div>
            <div style={{ textAlign: 'right' }}>
              <div style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600 }}>EXPECTED RETURN</div>
              <div style={{ fontSize: '22px', fontWeight: 800, fontFamily: 'var(--font-mono)' }} className={(data.signal.expected_return_pct || 0) >= 0 ? 'positive' : 'negative'}>
                {(data.signal.expected_return_pct || 0) > 0 ? '+' : ''}{(data.signal.expected_return_pct || 0).toFixed(2)}%
              </div>
            </div>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
              <span style={{ fontSize: '11px', color: 'var(--text-muted)', fontWeight: 600, marginBottom: '4px' }}>RECOMMENDATION</span>
              <span className={`badge ${sigClass}`} style={{ fontSize: '14px', padding: '6px 14px' }}>
                {signalStr}
              </span>
            </div>
          </div>
        ) : (
          <div style={{ padding: '12px', background: 'rgba(244, 63, 94, 0.1)', border: '1px solid rgba(244, 63, 94, 0.3)', borderRadius: '6px', maxWidth: '300px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: 'var(--color-rose)', fontWeight: 700, fontSize: '12px', marginBottom: '8px' }}>
              <AlertTriangle size={14} />
              PREDICTION UNAVAILABLE
            </div>
            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '11px', color: 'var(--text-secondary)' }}>
              {data.quality_gate?.gate_failures?.map((f, i) => <li key={i}>{f}</li>)}
            </ul>
          </div>
        )}
      </div>

      {/* Main Grid: Interactive Chart & L2 Depth */}
      <div style={{ display: 'grid', gridTemplateColumns: '8fr 4fr', gap: '20px' }}>
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <BarChart2 size={16} color="var(--color-cyan)" />
              <span>Interactive Financial Chart — 95% Conformal Bounds</span>
            </div>
            {data.intelligence?.conformal === 'AVAILABLE' ? (
              <span style={{ fontSize: '11px', color: 'var(--color-cyan)', fontFamily: 'var(--font-mono)' }}>
                Empirical Coverage: {data.signal.conformal_range?.empirical_coverage || 95}%
              </span>
            ) : (
              <span style={{ fontSize: '11px', color: 'var(--color-rose)', fontWeight: 700 }}>
                CONFORMAL UNAVAILABLE
              </span>
            )}
          </div>
          <FinancialChart symbol={data.symbol} data={[]} currencySymbol={currSym} />
        </div>

        <MarketDepthVisualizer quotePrice={data.quote_price || 100.0} currencySymbol={currSym} />
      </div>

      {/* Grid of Intelligence Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3, 1fr)', gap: '20px' }}>
        {/* SHAP Drivers */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <Zap size={16} color="var(--color-amber)" />
              <span>SHAP Feature Drivers</span>
            </div>
          </div>
          {data.intelligence?.shap === 'AVAILABLE' ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '8px', fontSize: '12px' }}>
              <strong style={{ color: 'var(--color-emerald)' }}>Top Positive Drivers:</strong>
              {topPosDrivers.length > 0 ? topPosDrivers.map((d, i) => (
                <div key={i} style={{ background: 'rgba(16, 185, 129, 0.08)', padding: '6px 10px', borderRadius: '4px', borderLeft: '3px solid #10b981' }}>
                  <span style={{ fontWeight: 700 }}>{d.feature_name}</span>: {d.description}
                </div>
              )) : <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>None detected</div>}

              <strong style={{ color: 'var(--color-rose)', marginTop: '6px' }}>Top Negative Drivers:</strong>
              {topNegDrivers.length > 0 ? topNegDrivers.map((d, i) => (
                <div key={i} style={{ background: 'rgba(244, 63, 94, 0.08)', padding: '6px 10px', borderRadius: '4px', borderLeft: '3px solid #f43f5e' }}>
                  <span style={{ fontWeight: 700 }}>{d.feature_name}</span>: {d.description}
                </div>
              )) : <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>None detected</div>}
            </div>
          ) : (
            <div style={{ color: 'var(--text-muted)', fontSize: '12px', padding: '20px', textAlign: 'center' }}>
              EXPLANATION TEMPORARILY UNAVAILABLE
            </div>
          )}
        </div>

        {/* Counterfactual Analysis */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <Layers size={16} color="var(--color-cyan)" />
              <span>Counterfactual Flip Points</span>
            </div>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', fontSize: '12px' }}>
            <div style={{ fontSize: '11px', color: 'var(--text-muted)' }}>
              Target Reversal Signal: <strong style={{ color: 'var(--color-amber)' }}>{data.counterfactuals?.target_flip_signal || 'NEUTRAL'}</strong>
            </div>
            {flipFactors.length > 0 ? flipFactors.map((f, i) => (
              <div key={i} style={{ background: 'var(--bg-canvas)', padding: '8px 10px', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700 }}>
                  <span style={{ color: 'var(--color-cyan)' }}>{f.feature_name}</span>
                  <span style={{ color: f.required_direction === 'INCREASE' ? 'var(--color-emerald)' : 'var(--color-rose)' }}>
                    {f.required_direction}
                  </span>
                </div>
                <div style={{ fontSize: '11px', color: 'var(--text-secondary)', marginTop: '2px' }}>{f.description}</div>
              </div>
            )) : <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>No sensitivity factors calculated</div>}
          </div>
        </div>

        {/* Model Parliament Leaderboard */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <ShieldCheck size={16} color="var(--color-purple)" />
              <span>Parliament Leaderboard</span>
            </div>
            {data.signal?.model_consensus && (
              <span style={{ fontSize: '10px', fontWeight: 700, color: getConsensusColor(data.signal.model_consensus), background: 'var(--bg-canvas)', padding: '2px 6px', borderRadius: '4px' }}>
                {data.signal.model_consensus} CONSENSUS
              </span>
            )}
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
            {leaderboardEntries.length > 0 ? leaderboardEntries.map(([modelName, acc]) => (
              <div key={modelName} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', fontSize: '12px' }}>
                <span style={{ color: modelName === 'Stacked Ensemble' ? 'var(--color-cyan)' : 'var(--text-secondary)', fontWeight: modelName === 'Stacked Ensemble' ? 700 : 500 }}>
                  {modelName}
                </span>
                <span style={{ fontFamily: 'var(--font-mono)', fontWeight: 700, color: modelName === 'Stacked Ensemble' ? 'var(--color-emerald)' : 'var(--text-primary)' }}>
                  {acc.toFixed(1)}% OOS
                </span>
              </div>
            )) : <div style={{ color: 'var(--text-muted)', fontSize: '11px' }}>Leaderboard loading...</div>}
          </div>
        </div>
      </div>

      {/* Provenance Footer */}
      {data.provenance && (
        <div style={{ marginTop: '10px' }}>
          <button 
            onClick={() => setShowProvenance(!showProvenance)}
            style={{ background: 'transparent', border: 'none', color: 'var(--text-muted)', fontSize: '11px', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '6px' }}
          >
            <Cpu size={12} /> {showProvenance ? 'Hide' : 'Show'} Prediction Provenance
          </button>
          {showProvenance && (
            <div className="panel" style={{ marginTop: '10px', display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '12px', fontSize: '10px', background: 'var(--bg-canvas)' }}>
              <div><span style={{ color: 'var(--text-secondary)' }}>Prediction ID:</span> <br/>{data.provenance.prediction_id}</div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Generated At:</span> <br/>{data.provenance.generated_at}</div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Model Version:</span> <br/>{data.provenance.model_version}</div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Feature Version:</span> <br/>{data.provenance.feature_version}</div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Calibration:</span> <br/>{data.provenance.calibration_version}</div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Conformal:</span> <br/>{data.provenance.conformal_version}</div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Data Status:</span> <br/>{data.provenance.data_status}</div>
              <div><span style={{ color: 'var(--text-secondary)' }}>Ensemble:</span> <br/>{data.provenance.is_ensemble ? 'YES' : 'NO'}</div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};
