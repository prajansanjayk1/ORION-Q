'use client';

import React, { useState, useEffect } from 'react';
import { fetchModelRegistryChampions, fetchModelHistory, fetchModelEvaluation } from '../lib/api';
import { ShieldCheck, Cpu, RefreshCw, Layers, CheckCircle2, History, BarChart2, Activity, Zap, FileSpreadsheet } from 'lucide-react';
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
  Legend
} from 'recharts';

export const ModelRegistryView: React.FC = () => {
  const [champions, setChampions] = useState<Record<string, any>>({});
  const [selectedSymbol, setSelectedSymbol] = useState<string>('AAPL');
  const [history, setHistory] = useState<any[]>([]);
  const [evaluationSuite, setEvaluationSuite] = useState<any>(null);
  const [selectedModel, setSelectedModel] = useState<string>('Stacked Ensemble');
  const [loading, setLoading] = useState<boolean>(true);

  useEffect(() => {
    async function loadData() {
      setLoading(true);
      const champData = await fetchModelRegistryChampions();
      if (champData) setChampions(champData);

      const histData = await fetchModelHistory(selectedSymbol);
      if (histData) setHistory(histData);

      const evalData = await fetchModelEvaluation(selectedSymbol);
      if (evalData && evalData.evaluation_suite) {
        setEvaluationSuite(evalData.evaluation_suite);
      } else {
        setEvaluationSuite(null);
      }
      setLoading(false);
    }
    loadData();
  }, [selectedSymbol]);

  const championList = Object.entries(champions);

  // Format ROC points for Recharts multi-line plotting
  const formatRocDataForRecharts = () => {
    if (!evaluationSuite || !evaluationSuite.roc_curves) return [];
    
    // std 11 points (fpr 0.0 to 1.0)
    const points: any[] = Array.from({ length: 11 }, (_, idx) => ({
      fpr: round(idx * 0.1),
      randomChance: round(idx * 0.1)
    }));

    evaluationSuite.roc_curves.forEach((roc: any) => {
      roc.points.forEach((pt: any, idx: number) => {
        if (idx < points.length) {
          points[idx][roc.model_name] = pt.tpr;
        }
      });
    });

    return points;
  };

  const round = (val: number) => Math.round(val * 100) / 100;

  // Selected Confusion Matrix
  const currentCM = evaluationSuite?.confusion_matrices?.[selectedModel] || null;
  const detailedMetrics = evaluationSuite?.detailed_metrics || {};

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px', padding: '20px' }}>
      {/* Header Panel */}
      <div className="panel" style={{ flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <ShieldCheck size={24} color="var(--color-cyan)" />
            <h1 style={{ fontSize: '20px', fontWeight: 800, fontFamily: 'var(--font-mono)' }}>
              Institutional Model Governance & Evaluation Suite
            </h1>
          </div>
          <p style={{ color: 'var(--text-secondary)', fontSize: '12px', marginTop: '4px' }}>
            Out-of-fold ROC Curves, confusion matrices, precision/recall evaluation metrics, and walk-forward cross-validation lineage.
          </p>
        </div>
        <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
          <select
            value={selectedSymbol}
            onChange={(e) => setSelectedSymbol(e.target.value)}
            style={{
              background: 'var(--bg-canvas)',
              border: '1px solid var(--border-bright)',
              padding: '6px 12px',
              borderRadius: '4px',
              color: 'var(--text-primary)',
              fontSize: '12px',
              fontWeight: 700,
              outline: 'none'
            }}
          >
            {['AAPL', 'MSFT', 'NVDA', 'RELIANCE', 'TCS', 'INFY'].map((s) => (
              <option key={s} value={s}>{s}</option>
            ))}
          </select>

          <button
            onClick={async () => {
              setLoading(true);
              const champData = await fetchModelRegistryChampions();
              if (champData) setChampions(champData);
              const evalData = await fetchModelEvaluation(selectedSymbol);
              if (evalData && evalData.evaluation_suite) setEvaluationSuite(evalData.evaluation_suite);
              setLoading(false);
            }}
            style={{
              background: 'var(--bg-canvas)',
              border: '1px solid var(--border-bright)',
              padding: '6px 12px',
              borderRadius: '4px',
              color: 'var(--text-primary)',
              fontSize: '12px',
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '6px'
            }}
          >
            <RefreshCw size={14} className={loading ? 'animate-spin' : ''} /> Refresh Suite
          </button>
        </div>
      </div>

      {/* 1. ROC Curve Comparison & Confusion Matrix Visualizer Grid */}
      <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: '20px' }}>
        {/* Multi-Model ROC Curve Comparison Chart */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <Activity size={16} color="var(--color-cyan)" />
              <span>Multi-Model Receiver Operating Characteristic (ROC) Comparison</span>
            </div>
            <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Class: Bullish vs Non-Bullish</span>
          </div>

          <div style={{ width: '100%', height: '320px', background: 'var(--bg-canvas)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '10px 10px 0 0' }}>
            {evaluationSuite?.roc_curves ? (
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={formatRocDataForRecharts()}>
                  <CartesianGrid stroke="#1e293b" strokeDasharray="3 3" />
                  <XAxis dataKey="fpr" stroke="#64748b" fontSize={10} label={{ value: 'False Positive Rate (FPR)', position: 'insideBottom', offset: -2, fill: '#64748b', fontSize: 10 }} />
                  <YAxis domain={[0, 1]} stroke="#94a3b8" fontSize={10} label={{ value: 'True Positive Rate (TPR)', angle: -90, position: 'insideLeft', fill: '#94a3b8', fontSize: 10 }} />
                  <Tooltip
                    contentStyle={{ background: '#0f172a', borderColor: '#334155', borderRadius: '6px', fontSize: '11px' }}
                    formatter={(val: any, name: string) => [val, name]}
                  />
                  
                  {/* Random Chance Benchmark */}
                  <Line type="monotone" dataKey="randomChance" name="Random Chance (AUC=0.50)" stroke="#475569" strokeDasharray="4 4" dot={false} />

                  {/* ROC Curves for Models */}
                  {evaluationSuite.roc_curves.map((roc: any) => (
                    <Line
                      key={roc.model_name}
                      type="monotone"
                      dataKey={roc.model_name}
                      name={`${roc.model_name} (AUC: ${roc.auc})`}
                      stroke={roc.color}
                      strokeWidth={roc.model_name === 'Stacked Ensemble' ? 3 : 1.5}
                      dot={false}
                    />
                  ))}
                </LineChart>
              </ResponsiveContainer>
            ) : (
              <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
                Loading ROC Curve comparison matrix...
              </div>
            )}
          </div>

          {/* AUC Legend Badges */}
          <div style={{ display: 'flex', gap: '8px', flexWrap: 'wrap', marginTop: '4px' }}>
            {evaluationSuite?.roc_curves?.map((roc: any) => (
              <div
                key={roc.model_name}
                onClick={() => setSelectedModel(roc.model_name)}
                style={{
                  background: selectedModel === roc.model_name ? 'rgba(6, 182, 212, 0.2)' : 'var(--bg-canvas)',
                  border: `1px solid ${roc.color}`,
                  padding: '4px 10px',
                  borderRadius: '4px',
                  fontSize: '11px',
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '6px'
                }}
              >
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: roc.color }} />
                <span style={{ fontWeight: 700, color: 'var(--text-primary)' }}>{roc.model_name}</span>
                <span style={{ fontFamily: 'var(--font-mono)', color: 'var(--color-emerald)', fontWeight: 800 }}>AUC {roc.auc}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Confusion Matrix Visualizer */}
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <Layers size={16} color="var(--color-purple)" />
              <span>Confusion Matrix Visualizer — {selectedModel}</span>
            </div>
          </div>

          {currentCM ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {/* 3x3 Heatmap Grid */}
              <div style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-color)', borderRadius: '6px', padding: '16px' }}>
                <div style={{ fontSize: '10px', color: 'var(--text-muted)', marginBottom: '8px', textAlign: 'center' }}>
                  PREDICTED CLASS →
                </div>

                <div style={{ display: 'grid', gridTemplateColumns: '80px repeat(3, 1fr)', gap: '6px', textAlign: 'center', fontSize: '11px' }}>
                  <div style={{ color: 'var(--text-muted)', fontSize: '10px', alignSelf: 'center' }}>ACTUAL ↓</div>
                  {currentCM.labels.map((lbl: string) => (
                    <div key={lbl} style={{ fontWeight: 700, color: 'var(--color-cyan)', fontSize: '10px' }}>{lbl}</div>
                  ))}

                  {currentCM.labels.map((rowLabel: string, rIdx: number) => (
                    <React.Fragment key={rowLabel}>
                      <div style={{ fontWeight: 700, color: 'var(--text-secondary)', alignSelf: 'center', fontSize: '10px', textAlign: 'left' }}>
                        {rowLabel}
                      </div>
                      {currentCM.matrix[rIdx].map((val: number, cIdx: number) => {
                        const isDiagonal = rIdx === cIdx;
                        return (
                          <div
                            key={`${rIdx}-${cIdx}`}
                            style={{
                              background: isDiagonal ? 'rgba(16, 185, 129, 0.2)' : 'rgba(244, 63, 94, 0.1)',
                              border: `1px solid ${isDiagonal ? 'rgba(16, 185, 129, 0.4)' : 'rgba(244, 63, 94, 0.2)'}`,
                              padding: '12px 6px',
                              borderRadius: '4px',
                              fontWeight: 800,
                              fontFamily: 'var(--font-mono)',
                              color: isDiagonal ? 'var(--color-emerald)' : 'var(--color-rose)',
                              fontSize: '14px'
                            }}
                          >
                            {val}
                          </div>
                        );
                      })}
                    </React.Fragment>
                  ))}
                </div>
              </div>

              {/* Classification Metrics Card */}
              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: '8px', fontSize: '11px' }}>
                <div style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-color)', padding: '8px', borderRadius: '4px', textAlign: 'center' }}>
                  <div style={{ color: 'var(--text-muted)', fontSize: '10px' }}>Accuracy</div>
                  <div style={{ fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-emerald)', fontSize: '14px' }}>
                    {currentCM.accuracy}%
                  </div>
                </div>
                <div style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-color)', padding: '8px', borderRadius: '4px', textAlign: 'center' }}>
                  <div style={{ color: 'var(--text-muted)', fontSize: '10px' }}>Precision</div>
                  <div style={{ fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-cyan)', fontSize: '14px' }}>
                    {currentCM.precision}%
                  </div>
                </div>
                <div style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-color)', padding: '8px', borderRadius: '4px', textAlign: 'center' }}>
                  <div style={{ color: 'var(--text-muted)', fontSize: '10px' }}>Recall</div>
                  <div style={{ fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-purple)', fontSize: '14px' }}>
                    {currentCM.recall}%
                  </div>
                </div>
                <div style={{ background: 'var(--bg-canvas)', border: '1px solid var(--border-color)', padding: '8px', borderRadius: '4px', textAlign: 'center' }}>
                  <div style={{ color: 'var(--text-muted)', fontSize: '10px' }}>F1-Score</div>
                  <div style={{ fontWeight: 800, fontFamily: 'var(--font-mono)', color: 'var(--color-amber)', fontSize: '14px' }}>
                    {currentCM.f1_score}%
                  </div>
                </div>
              </div>
            </div>
          ) : (
            <div style={{ padding: '40px', textAlign: 'center', color: 'var(--text-muted)' }}>
              Loading confusion matrix data...
            </div>
          )}
        </div>
      </div>

      {/* 2. Walk-Forward Performance Comparison Matrix */}
      <div className="panel">
        <div className="panel-header">
          <div className="panel-title">
            <FileSpreadsheet size={16} color="var(--color-emerald)" />
            <span>Walk-Forward Cross-Validation Performance Leaderboard — {selectedSymbol}</span>
          </div>
          <span style={{ fontSize: '11px', color: 'var(--text-muted)' }}>Evaluated on Out-Of-Fold Predictions</span>
        </div>

        <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '8px', fontSize: '12px' }}>
          <thead>
            <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '11px' }}>
              <th style={{ padding: '10px' }}>MODEL ALGORITHM</th>
              <th style={{ padding: '10px' }}>ROC-AUC SCORE</th>
              <th style={{ padding: '10px' }}>ACCURACY (OOS)</th>
              <th style={{ padding: '10px' }}>PRECISION</th>
              <th style={{ padding: '10px' }}>RECALL</th>
              <th style={{ padding: '10px' }}>F1-SCORE</th>
              <th style={{ padding: '10px' }}>LOG LOSS</th>
              <th style={{ padding: '10px' }}>PARLIAMENT STATUS</th>
            </tr>
          </thead>
          <tbody>
            {Object.entries(detailedMetrics).map(([mName, m]: [string, any]) => {
              const isChampion = mName === 'Stacked Ensemble';
              return (
                <tr
                  key={mName}
                  onClick={() => setSelectedModel(mName)}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    cursor: 'pointer',
                    background: selectedModel === mName ? 'var(--bg-panel-hover)' : 'transparent'
                  }}
                >
                  <td style={{ padding: '12px 10px', fontWeight: 800, color: isChampion ? 'var(--color-cyan)' : 'var(--text-primary)' }}>
                    {mName}
                  </td>
                  <td style={{ padding: '12px 10px', fontFamily: 'var(--font-mono)', fontWeight: 800, color: 'var(--color-emerald)' }}>
                    {m.roc_auc}
                  </td>
                  <td style={{ padding: '12px 10px', fontFamily: 'var(--font-mono)', fontWeight: 700 }}>
                    {m.accuracy}%
                  </td>
                  <td style={{ padding: '12px 10px', fontFamily: 'var(--font-mono)' }}>
                    {m.precision}%
                  </td>
                  <td style={{ padding: '12px 10px', fontFamily: 'var(--font-mono)' }}>
                    {m.recall}%
                  </td>
                  <td style={{ padding: '12px 10px', fontFamily: 'var(--font-mono)', fontWeight: 700, color: 'var(--color-amber)' }}>
                    {m.f1_score}%
                  </td>
                  <td style={{ padding: '12px 10px', fontFamily: 'var(--font-mono)', color: 'var(--text-secondary)' }}>
                    {m.log_loss}
                  </td>
                  <td style={{ padding: '12px 10px' }}>
                    <span className={`badge ${isChampion ? 'badge-live' : 'badge-closed'}`}>
                      {isChampion ? 'CHAMPION' : 'MEMBER'}
                    </span>
                  </td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      {/* 3. Active Champions & Model Lineage */}
      <div style={{ display: 'grid', gridTemplateColumns: '7fr 5fr', gap: '20px' }}>
        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <CheckCircle2 size={16} color="var(--color-emerald)" />
              <span>Active Champion Models across Instruments</span>
            </div>
          </div>
          <table style={{ width: '100%', borderCollapse: 'collapse', marginTop: '8px', fontSize: '12px' }}>
            <thead>
              <tr style={{ borderBottom: '1px solid var(--border-color)', textAlign: 'left', color: 'var(--text-muted)', fontSize: '11px' }}>
                <th style={{ padding: '8px' }}>INSTRUMENT</th>
                <th style={{ padding: '8px' }}>MODEL ID</th>
                <th style={{ padding: '8px' }}>ALGORITHM</th>
                <th style={{ padding: '8px' }}>VALIDATION</th>
                <th style={{ padding: '8px' }}>STATUS</th>
              </tr>
            </thead>
            <tbody>
              {championList.map(([sym, meta]) => (
                <tr
                  key={sym}
                  onClick={() => setSelectedSymbol(sym)}
                  style={{
                    borderBottom: '1px solid var(--border-color)',
                    cursor: 'pointer',
                    background: selectedSymbol === sym ? 'var(--bg-panel-hover)' : 'transparent'
                  }}
                >
                  <td style={{ padding: '10px 8px', fontWeight: 700, color: 'var(--color-cyan)', fontFamily: 'var(--font-mono)' }}>
                    {sym}
                  </td>
                  <td style={{ padding: '10px 8px', fontFamily: 'var(--font-mono)', fontSize: '10px' }}>
                    {meta.model_id}
                  </td>
                  <td style={{ padding: '10px 8px', color: 'var(--text-secondary)' }}>
                    {meta.algorithm}
                  </td>
                  <td style={{ padding: '10px 8px', fontSize: '10px', color: 'var(--text-muted)' }}>
                    {meta.validation_period}
                  </td>
                  <td style={{ padding: '10px 8px' }}>
                    <span className="badge badge-live">CHAMPION</span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="panel">
          <div className="panel-header">
            <div className="panel-title">
              <History size={16} color="var(--color-purple)" />
              <span>Model Lineage & Provenance — {selectedSymbol}</span>
            </div>
          </div>

          {history.length > 0 ? (
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              {history.map((m, idx) => (
                <div key={idx} style={{ background: 'var(--bg-canvas)', padding: '12px', borderRadius: '6px', border: '1px solid var(--border-color)', fontSize: '11px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', fontWeight: 700, marginBottom: '6px' }}>
                    <span style={{ color: 'var(--color-cyan)', fontFamily: 'var(--font-mono)' }}>{m.model_id}</span>
                    <span className={`badge ${m.status === 'CHAMPION' ? 'badge-live' : 'badge-closed'}`}>{m.status}</span>
                  </div>
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px', color: 'var(--text-secondary)', fontSize: '10px' }}>
                    <div>Model Version: {m.model_version}</div>
                    <div>Feature Version: {m.feature_version}</div>
                    <div>Calibration: {m.calibration_method}</div>
                    <div>Conformal: {m.conformal_method}</div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div style={{ padding: '30px', textAlign: 'center', color: 'var(--text-muted)', fontSize: '12px' }}>
              Select an instrument to inspect historical lineage and validation history.
            </div>
          )}
        </div>
      </div>
    </div>
  );
};
