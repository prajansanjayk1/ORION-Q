'use client';

import React, { useState } from 'react';
import { askCopilot } from '../lib/api';
import { MessageSquareCode, Send, ShieldCheck, AlertTriangle, Info, BrainCircuit, Activity } from 'lucide-react';

export const CopilotView: React.FC = () => {
  const [query, setQuery] = useState('');
  const [loading, setLoading] = useState(false);
  const [messages, setMessages] = useState<Array<{ sender: 'user' | 'copilot'; text: string; data?: any }>>([
    {
      sender: 'copilot',
      text: 'Hello. I am the **ORION-Q Quantitative Copilot**. Ask me any quantitative question about supported US or Indian equities (e.g. *"Why is RELIANCE bullish?"*, *"What is the 95% conformal bound for AAPL?"*). I retrieve structured live evidence before answering and will strictly refuse to hallucinate missing data.'
    }
  ]);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim() || loading) return;

    const userMsg = query.trim();
    setQuery('');
    setMessages(prev => [...prev, { sender: 'user', text: userMsg }]);
    setLoading(true);

    try {
      const res = await askCopilot(userMsg);
      setLoading(false);

      if (res && res.confidence !== 'INSUFFICIENT_DATA') {
        setMessages(prev => [...prev, { sender: 'copilot', text: res.response_text, data: res }]);
      } else {
        setMessages(prev => [...prev, { sender: 'copilot', text: '⚠ INSUFFICIENT EVIDENCE\nI cannot produce a reliable quantitative explanation because the required live market / model evidence is unavailable.', data: res }]);
      }
    } catch (error) {
      setLoading(false);
      setMessages(prev => [...prev, { sender: 'copilot', text: '⚠ INSUFFICIENT EVIDENCE\nI cannot produce a reliable quantitative explanation because the required live market / model evidence is unavailable.' }]);
    }
  };

  const renderConfidence = (conf: string) => {
    let color = 'var(--text-muted)';
    if (conf === 'HIGH') color = 'var(--color-emerald)';
    if (conf === 'MEDIUM') color = 'var(--color-yellow)';
    if (conf === 'LOW') color = 'var(--color-orange)';
    if (conf === 'INSUFFICIENT_DATA') color = 'var(--color-red)';
    return <span style={{ color, fontWeight: 'bold' }}>{conf}</span>;
  };

  return (
    <div className="panel" style={{ margin: '20px', height: 'calc(100vh - 160px)', display: 'flex', flexDirection: 'column' }}>
      <div className="panel-header">
        <div className="panel-title">
          <MessageSquareCode size={18} color="var(--color-cyan)" />
          <span>ORION-Q Quantitative AI Copilot — Evidence-Driven Engine</span>
        </div>
        <span style={{ fontSize: '11px', color: 'var(--color-emerald)', fontWeight: 600 }}>Zero Hallucination Guarantee</span>
      </div>

      <div style={{ flex: 1, overflowY: 'auto', display: 'flex', flexDirection: 'column', gap: '16px', padding: '10px' }}>
        {messages.map((m, i) => (
          <div
            key={i}
            style={{
              alignSelf: m.sender === 'user' ? 'flex-end' : 'flex-start',
              maxWidth: '85%',
              background: m.sender === 'user' ? 'rgba(6, 182, 212, 0.15)' : 'var(--bg-canvas)',
              border: `1px solid ${m.sender === 'user' ? 'rgba(6, 182, 212, 0.4)' : 'var(--border-color)'}`,
              borderRadius: '8px',
              padding: '14px 18px',
              color: 'var(--text-primary)',
              fontSize: '13px',
              whiteSpace: 'pre-line'
            }}
          >
            <div style={{ fontSize: '11px', color: m.sender === 'user' ? 'var(--color-cyan)' : 'var(--color-purple)', fontWeight: 700, marginBottom: '6px' }}>
              {m.sender === 'user' ? 'INSTITUTIONAL INVESTOR' : 'ORION-Q QUANT COPILOT'}
            </div>
            <div>{m.text}</div>

            {m.data && m.data.confidence && (
              <div style={{ marginTop: '10px', fontSize: '11px', color: 'var(--text-secondary)' }}>
                Confidence: {renderConfidence(m.data.confidence)}
              </div>
            )}

            {m.data && m.data.evidence_sections && m.data.evidence_sections.length > 0 && (
              <div style={{ marginTop: '12px', display: 'flex', flexDirection: 'column', gap: '10px' }}>
                {m.data.evidence_sections.map((section: any, idx: number) => {
                  if (section.type === 'FACTUAL_DATA') {
                    return (
                      <div key={idx} style={{ background: 'var(--bg-panel)', padding: '10px', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                        <div style={{ fontWeight: 700, color: 'var(--color-cyan)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px' }}>
                          <Activity size={14} /> 📊 FACTUAL MARKET DATA
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '4px', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                          <div>Price: {section.content.price}</div>
                          <div>Status: {section.content.market_status}</div>
                          <div>Feed: {section.content.feed}</div>
                        </div>
                      </div>
                    );
                  } else if (section.type === 'MODEL_OUTPUT') {
                    return (
                      <div key={idx} style={{ background: 'var(--bg-panel)', padding: '10px', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                        <div style={{ fontWeight: 700, color: 'var(--color-purple)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px' }}>
                          <BrainCircuit size={14} /> 🤖 MODEL OUTPUT
                        </div>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '4px', fontSize: '11px', fontFamily: 'var(--font-mono)' }}>
                          <div>Signal: {section.content.signal}</div>
                          <div>Prob: {section.content.probability}</div>
                          <div>Regime: {section.content.regime}</div>
                          <div>Expected: {section.content.expected_return}</div>
                        </div>
                      </div>
                    );
                  } else if (section.type === 'GENERAL_EXPLANATION') {
                    return (
                      <div key={idx} style={{ background: 'var(--bg-panel)', padding: '10px', borderRadius: '4px', border: '1px solid var(--border-color)' }}>
                        <div style={{ fontWeight: 700, color: 'var(--color-emerald)', marginBottom: '4px', display: 'flex', alignItems: 'center', gap: '6px', fontSize: '11px' }}>
                          <Info size={14} /> 📝 GENERAL EXPLANATION
                        </div>
                        <div style={{ fontSize: '11px', color: 'var(--text-secondary)' }}>
                          {section.content.context}
                        </div>
                      </div>
                    );
                  }
                  return null;
                })}
              </div>
            )}

            {m.data && m.data.disclaimers && m.data.disclaimers.length > 0 && (
              <div style={{ marginTop: '12px', paddingTop: '10px', borderTop: '1px solid var(--border-color)', fontSize: '10px', color: 'var(--text-muted)' }}>
                {m.data.disclaimers.map((d: string, i: number) => <div key={i}>• {d}</div>)}
              </div>
            )}
          </div>
        ))}

        {loading && (
          <div style={{ alignSelf: 'flex-start', color: 'var(--text-muted)', fontSize: '12px', fontStyle: 'italic' }}>
            Retrieving live market state, regime, SHAP drivers, and conformal bounds...
          </div>
        )}
      </div>

      <form onSubmit={handleSubmit} style={{ display: 'flex', gap: '10px', marginTop: '10px' }}>
        <input
          type="text"
          placeholder="Ask Quantitative Copilot (e.g., Why is RELIANCE bullish? Should I buy AAPL?)..."
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          style={{
            flex: 1,
            background: 'var(--bg-canvas)',
            border: '1px solid var(--border-bright)',
            borderRadius: '6px',
            padding: '12px 16px',
            color: 'var(--text-primary)',
            fontSize: '13px',
            outline: 'none'
          }}
        />
        <button
          type="submit"
          disabled={loading}
          style={{
            background: 'var(--color-cyan)',
            color: '#000000',
            fontWeight: 700,
            padding: '0 20px',
            borderRadius: '6px',
            display: 'flex',
            alignItems: 'center',
            gap: '8px'
          }}
        >
          <Send size={16} />
          <span>ASK COPILOT</span>
        </button>
      </form>
    </div>
  );
};
