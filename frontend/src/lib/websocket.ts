import { ConnectionState } from '../types';

export class MarketWSClient {
  private ws: WebSocket | null = null;
  private url: string;
  private subscribedSymbols: Set<string> = new Set();
  private onMessageCallback: ((event: any) => void) | null = null;
  private onStateChangeCallback: ((state: ConnectionState) => void) | null = null;

  private connectionState: ConnectionState = 'DISCONNECTED';
  private heartbeatInterval: NodeJS.Timeout | null = null;
  private lastHeartbeat: number = 0;
  private missedHeartbeats: number = 0;

  constructor() {
    this.url = this.getWsUrl();
    this.setupVisibilityHandler();
  }

  private getWsUrl(): string {
    if (typeof window !== 'undefined') {
      const host = window.location.hostname || '127.0.0.1';
      return `ws://${host}:8000/api/v1/ws/market`;
    }
    return 'ws://127.0.0.1:8000/api/v1/ws/market';
  }

  private setupVisibilityHandler() {
    if (typeof document !== 'undefined') {
      document.addEventListener('visibilitychange', () => {
        if (document.visibilityState === 'visible') {
          if (this.connectionState === 'CONNECTED' || this.connectionState === 'DEGRADED') {
            this.requestSnapshot();
          } else {
            this.connect(this.onMessageCallback, this.onStateChangeCallback);
          }
        }
      });
    }
  }

  private setState(state: ConnectionState) {
    if (this.connectionState !== state) {
      this.connectionState = state;
      if (this.onStateChangeCallback) {
        this.onStateChangeCallback(state);
      }
    }
  }

  public connect(
    onMessage: ((event: any) => void) | null,
    onStateChange: ((state: ConnectionState) => void) | null = null
  ) {
    if (onMessage) this.onMessageCallback = onMessage;
    if (onStateChange) this.onStateChangeCallback = onStateChange;

    if (this.ws?.readyState === WebSocket.CONNECTING || this.ws?.readyState === WebSocket.OPEN) {
      return;
    }

    this.url = this.getWsUrl();
    this.setState('CONNECTING');

    try {
      this.ws = new WebSocket(this.url);

      this.ws.onopen = () => {
        this.setState('CONNECTED');
        this.lastHeartbeat = Date.now();
        this.missedHeartbeats = 0;

        this.requestSnapshot();
        if (this.subscribedSymbols.size > 0) {
          this.subscribe(Array.from(this.subscribedSymbols));
        }

        this.startHeartbeatMonitor();
      };

      this.ws.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);

          if (data.type === 'heartbeat' || data.type === 'pong') {
            this.lastHeartbeat = Date.now();
            this.missedHeartbeats = 0;
            if (this.connectionState === 'DEGRADED') {
              this.setState('CONNECTED');
            }
          }

          data.frontend_received_timestamp = Date.now() / 1000.0;
          if (this.onMessageCallback) {
            this.onMessageCallback(data);
          }
        } catch (e) {
          // ignore
        }
      };

      this.ws.onclose = () => {
        this.setState('DISCONNECTED');
        this.cleanup();
        setTimeout(() => {
          this.setState('RECONNECTING');
          this.connect(this.onMessageCallback, this.onStateChangeCallback);
        }, 3000);
      };

      this.ws.onerror = () => {
        this.ws?.close();
      };

    } catch (e) {
      this.setState('DISCONNECTED');
      setTimeout(() => {
        this.setState('RECONNECTING');
        this.connect(this.onMessageCallback, this.onStateChangeCallback);
      }, 3000);
    }
  }

  private startHeartbeatMonitor() {
    this.cleanup();
    this.heartbeatInterval = setInterval(() => {
      const now = Date.now();
      if (now - this.lastHeartbeat > 10000) {
        this.missedHeartbeats++;
        if (this.missedHeartbeats >= 2) {
          this.setState('DEGRADED');
        }
        if (this.missedHeartbeats > 4) {
          this.ws?.close();
        }
      }

      if (this.ws && this.ws.readyState === WebSocket.OPEN) {
        this.ws.send(JSON.stringify({ action: 'ping' }));
      }
    }, 5000);
  }

  private requestSnapshot() {
    if (this.ws && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'snapshot' }));
    }
  }

  public subscribe(symbols: string[]) {
    symbols.forEach(s => this.subscribedSymbols.add(s));
    if (this.ws && (this.connectionState === 'CONNECTED' || this.connectionState === 'DEGRADED') && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'subscribe', symbols }));
    }
  }

  public unsubscribe(symbols: string[]) {
    symbols.forEach(s => this.subscribedSymbols.delete(s));
    if (this.ws && (this.connectionState === 'CONNECTED' || this.connectionState === 'DEGRADED') && this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action: 'unsubscribe', symbols }));
    }
  }

  private cleanup() {
    if (this.heartbeatInterval) {
      clearInterval(this.heartbeatInterval);
      this.heartbeatInterval = null;
    }
  }

  public close() {
    this.cleanup();
    this.ws?.close();
  }
}

export const wsClient = new MarketWSClient();
