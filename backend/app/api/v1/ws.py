from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query
from app.core.security import decode_token
from app.websocket.manager import manager

router = APIRouter(tags=["ws"])


@router.websocket("/ws")
async def ws_endpoint(ws: WebSocket, token: str = Query(...)):
    payload = decode_token(token)
    if not payload or payload.get("type") != "access":
        await ws.close(code=4401)
        return
    uid, role = int(payload["sub"]), payload["role"]
    await manager.connect(ws, uid, role)
    try:
        while True:
            await ws.receive_text()  # keepalive pings
    except WebSocketDisconnect:
        manager.disconnect(ws, uid)
