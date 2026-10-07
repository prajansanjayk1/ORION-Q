import json
import asyncio
from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from backend.app.websocket.connection_manager import ws_manager
from backend.app.websocket.event_types import WSEvent, EventType
from backend.app.data.ingestion_engine import ingestion_engine
from backend.app.services.market_session_engine import global_market_router
from backend.app.core.logging import logger

router = APIRouter()


@router.websocket("/ws/market")
async def websocket_market_endpoint(websocket: WebSocket):
    await ws_manager.connect(websocket)
    if websocket not in ws_manager.active_connections:
        return
    try:
        # Send initial market status
        status = global_market_router.get_global_status()
        await ws_manager.send_personal_event(
            websocket,
            WSEvent(
                event_type=EventType.MARKET_STATUS,
                data=status.model_dump()
            )
        )

        while True:
            data_text = await websocket.receive_text()
            try:
                msg = json.loads(data_text)
                action = msg.get("action")
                symbols = msg.get("symbols", [])

                if action == "subscribe":
                    ws_manager.subscribe(websocket, symbols)
                    # Push immediate quotes for newly subscribed symbols
                    for s in symbols:
                        quote = ingestion_engine.get_quote(s)
                        if quote:
                            await ws_manager.send_personal_event(
                                websocket,
                                WSEvent(
                                    event_type=EventType.PRICE_UPDATE,
                                    symbol=s.upper(),
                                    data=quote.model_dump()
                                )
                            )

                elif action == "unsubscribe":
                    ws_manager.unsubscribe(websocket, symbols)

                elif action == "ping":
                    await ws_manager.send_personal_event(
                        websocket,
                        WSEvent(
                            event_type=EventType.HEARTBEAT,
                            data={"status": "pong"}
                        )
                    )

            except json.JSONDecodeError:
                logger.warning("Received malformed JSON on WebSocket endpoint")

    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
