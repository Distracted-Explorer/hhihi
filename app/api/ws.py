from fastapi import APIRouter, WebSocket, WebSocketDisconnect

from app.websocket import ws_manager

router = APIRouter()


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket) -> None:
    await ws_manager.connect(ws)
    try:
        while True:
            # Keep the connection alive; ignore client payloads
            await ws.receive_text()
    except WebSocketDisconnect:
        await ws_manager.disconnect(ws)
