const getApiBaseUrl = () => {
  if (typeof window !== 'undefined') {
    const host = (window.location.hostname === 'localhost' || !window.location.hostname) ? '127.0.0.1' : window.location.hostname;
    return `http://${host}:8000/api/v1`;
  }
  return 'http://127.0.0.1:8000/api/v1';
};

export async function fetchMarketSession(mode: string = 'AUTO') {
  try {
    const res = await fetch(`${getApiBaseUrl()}/market-session?mode=${mode}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchQuote(symbol: string) {
  try {
    const res = await fetch(`${getApiBaseUrl()}/stocks/${symbol}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchPrediction(symbol: string) {
  try {
    const res = await fetch(`${getApiBaseUrl()}/prediction/${symbol}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchScannerData() {
  try {
    const res = await fetch(`${getApiBaseUrl()}/scanner`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchPortfolioIntelligence() {
  try {
    const res = await fetch(`${getApiBaseUrl()}/portfolio-intelligence`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchModelRegistryChampions() {
  try {
    const res = await fetch(`${getApiBaseUrl()}/registry/champions`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchModelHistory(symbol: string) {
  try {
    const res = await fetch(`${getApiBaseUrl()}/registry/history/${symbol}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchModelEvaluation(symbol: string = 'AAPL') {
  try {
    const res = await fetch(`${getApiBaseUrl()}/registry/evaluation/${symbol}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchBacktestRun(symbol: string = 'AAPL', strategy: string = 'ADAPTIVE HYBRID', period: string = '1y') {
  try {
    const res = await fetch(`${getApiBaseUrl()}/backtest/run?symbol=${symbol}&strategy=${encodeURIComponent(strategy)}&period=${period}`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function fetchSystemHealth() {
  try {
    const res = await fetch(`${getApiBaseUrl()}/health`);
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}

export async function askCopilot(query: string) {
  try {
    const res = await fetch(`${getApiBaseUrl()}/copilot`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ query })
    });
    if (!res.ok) return null;
    return await res.json();
  } catch (e) {
    return null;
  }
}
