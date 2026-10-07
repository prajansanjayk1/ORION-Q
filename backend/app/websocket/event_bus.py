import asyncio
import time
import random
from typing import Dict, Set, Optional
from backend.app.websocket.connection_manager import ws_manager
from backend.app.websocket.event_types import WSEvent, EventType
from backend.app.data.ingestion_engine import ingestion_engine
from backend.app.core.logging import logger


class MarketEventBus:
    """
    Central Event Bus managing second-by-second (1s) tick streaming to WebSocket clients.
    Polls active subscribed instruments from the data ingestion fabric
    and pushes live 1s market updates and server heartbeats.
    """
    def __init__(self):
        self._is_running: bool = False
        self._task: Optional[asyncio.Task] = None
        self._poll_interval: float = 1.0  # 1-second live tick interval
        self._last_prices: Dict[str, float] = {}

    def start(self):
        if not self._is_running:
            self._is_running = True
            self._task = asyncio.create_task(self._stream_loop())
            logger.info("MarketEventBus started 1s tick streaming loop.")

    def stop(self):
        if self._is_running:
            self._is_running = False
            if self._task:
                self._task.cancel()
            logger.info("MarketEventBus stopped.")

    async def _stream_loop(self):
        while self._is_running:
            try:
                # 1. Gather all unique subscribed symbols across active connections
                active_symbols: Set[str] = set()
                for sub_set in ws_manager.active_connections.values():
                    active_symbols.update(sub_set)

                # Default fallback set if clients haven't explicitly subscribed yet
                if not active_symbols:
                    active_symbols = {"AAPL", "RELIANCE", "NVDA", "SPY", "TCS", "MSFT", "INFY"}

                # 2. Fetch real quotes for each symbol and broadcast 1s price updates
                for symbol in active_symbols:
                    quote = ingestion_engine.get_quote(symbol)
                    if quote:
                        price = quote.price
                        # If market is closed or delayed, simulate 1s tick micro-fluctuation around last price (±0.02%)
                        if quote.data_state.value in ["CLOSED", "DELAYED"]:
                            last_p = self._last_prices.get(symbol, price)
                            delta = last_p * random.uniform(-0.0003, 0.0003)
                            price = round(max(0.01, last_p + delta), 2)
                            self._last_prices[symbol] = price
                            quote.price = price
                            quote.change = round(price - quote.previous_close, 2)
                            quote.percent_change = round((quote.change / quote.previous_close * 100.0) if quote.previous_close > 0 else 0.0, 2)

                        event = WSEvent(
                            event_type=EventType.PRICE_UPDATE,
                            symbol=quote.symbol,
                            data=quote.model_dump(),
                            websocket_timestamp=time.time()
                        )
                        await ws_manager.broadcast_event(event)

                # 3. Broadcast heartbeat telemetry with high-precision timestamp
                heartbeat = WSEvent(
                    event_type=EventType.HEARTBEAT,
                    data={"status": "active", "server_timestamp": time.time()},
                    websocket_timestamp=time.time()
                )
                await ws_manager.broadcast_event(heartbeat)

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in MarketEventBus loop: {e}")

            await asyncio.sleep(self._poll_interval)


market_event_bus = MarketEventBus()
