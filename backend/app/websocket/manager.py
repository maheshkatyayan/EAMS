from fastapi import WebSocket
from collections import defaultdict


class ConnectionManager:
    def __init__(self):
        self.by_user: dict[int, list[WebSocket]] = defaultdict(list)
        self.role_of: dict[WebSocket, str] = {}

    async def connect(self, ws: WebSocket, user_id: int, role: str):
        await ws.accept()
        self.by_user[user_id].append(ws)
        self.role_of[ws] = role

    def disconnect(self, ws: WebSocket, user_id: int):
        if ws in self.by_user.get(user_id, []):
            self.by_user[user_id].remove(ws)
        self.role_of.pop(ws, None)

    async def send_to(self, user_id: int, data: dict):
        for ws in list(self.by_user.get(user_id, [])):
            try: await ws.send_json(data)
            except Exception: pass

    async def broadcast_role(self, min_role: str, data: dict):
        """Send to everyone at or above a role (manager -> also hr, super_admin)."""
        order = ["employee", "manager", "hr", "super_admin"]
        allowed = set(order[order.index(min_role):])
        for ws, role in list(self.role_of.items()):
            if role in allowed:
                try: await ws.send_json(data)
                except Exception: pass


manager = ConnectionManager()
