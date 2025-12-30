from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List


class RoomConnectionManager:
    def __init__(self):
        self.rooms: Dict[int, List[WebSocket]] = {}
        print("[Manager Initialized]")

    async def connect(self, room_id: int, websocket: WebSocket, max_members: int):
        print(f"[Connect Attempt] Room ID: {room_id}, Max Members: {max_members}")
        await websocket.accept()
        print("[WebSocket Accepted]")

        if room_id not in self.rooms:
            self.rooms[room_id] = []
            print(f"[New Room Created] Room ID: {room_id}")

        print(f"[Current Room Count] {len(self.rooms[room_id])} members")
        if len(self.rooms[room_id]) > max_members:
            print("[Room Full] Rejecting connection")
            await websocket.send_text("Room is Full")
            await websocket.close()
            return False

        self.rooms[room_id].append(websocket)
        print(f"[Connected] Total Members Now: {len(self.rooms[room_id])}")
        return True

    def disconnect(self, room_id: int, websocket: WebSocket):
        print(f"[Disconnect Attempt] Room ID: {room_id}")
        if room_id in self.rooms and websocket in self.rooms[room_id]:
            self.rooms[room_id].remove(websocket)
            print(f"[Disconnected] Remaining Members: {len(self.rooms[room_id])}")

    async def broadcast(self, room_id: int, message: str):
        print(f"[Broadcast] Room ID: {room_id}, Message: {message}")
        if room_id in self.rooms:
            for conn in self.rooms[room_id]:
                try:
                    await conn.send_text(message)
                    print("[Message Sent]")
                except Exception as e:
                    print(f"[Broadcast Error] {e}")
