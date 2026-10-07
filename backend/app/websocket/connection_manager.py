import json
from typing import Dict, Set, List, Any
from fastapi import WebSocket
from backend.app.websocket.event_types import WSEvent, EventType
from backend.app.core.logging import logger


class ConnectionManager:
    def __init__(self):
        # Map websocket -> set of subscribed symbols
        self.active_connections: Dict[WebSocket, Set[str]] = {}

    async def connect(self, websocket: WebSocket):
        try:
            await websocket.accept()
            self.active_connections[websocket] = set()
            logger.info(f"WebSocket client connected. Total clients: {len(self.active_connections)}")
        except Exception as e:
            logger.error(f"Failed to accept WebSocket connection: {e}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]
            logger.info(f"WebSocket client disconnected. Remaining clients: {len(self.active_connections)}")

    def subscribe(self, websocket: WebSocket, symbols: List[str]):
        if websocket in self.active_connections:
            for s in symbols:
                self.active_connections[websocket].add(s.upper().strip())

    def unsubscribe(self, websocket: WebSocket, symbols: List[str]):
        if websocket in self.active_connections:
            for s in symbols:
                self.active_connections[websocket].discard(s.upper().strip())

    async def send_personal_event(self, websocket: WebSocket, event: WSEvent):
        if websocket not in self.active_connections:
            return
        try:
            await websocket.send_text(event.model_dump_json())
        except Exception as e:
            logger.debug(f"Error sending WebSocket message: {e}")
            self.disconnect(websocket)

    async def broadcast_event(self, event: WSEvent):
        event_json = event.model_dump_json()
        target_symbol = event.symbol.upper() if event.symbol else None

        disconnected = []
        for ws, sub_symbols in list(self.active_connections.items()):
            if target_symbol is None or target_symbol in sub_symbols or len(sub_symbols) == 0:
                try:
                    await ws.send_text(event_json)
                except Exception:
                    disconnected.append(ws)

        for ws in disconnected:
            self.disconnect(ws)


ws_manager = ConnectionManager()
