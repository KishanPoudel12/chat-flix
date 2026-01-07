import json

from fastapi import HTTPException, status, WebSocket,WebSocketDisconnect
from typing import Dict, List
from sqlalchemy.orm import Session
from crud.room import get_room_by_id
from crud.room_member import add_user_to_room, leave_room
import redis
from dotenv import load_dotenv
import os
load_dotenv()

# Read Redis config
REDIS_HOST = os.getenv("REDIS_HOST")
REDIS_PORT = int(os.getenv("REDIS_PORT"))
REDIS_USERNAME = os.getenv("REDIS_USERNAME")
REDIS_PASSWORD = os.getenv("REDIS_PASSWORD")

# Connect to Redis
redis_client = redis.Redis(
    host=REDIS_HOST,
    port=REDIS_PORT,
    username=REDIS_USERNAME,
    password=REDIS_PASSWORD,
    decode_responses=True
)

# redis_client= redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

try:
    pong = redis_client.ping()
    print("Connected to Redis:", pong)
except redis.ConnectionError as e:
    print("Redis connection failed:", e)

def set_room_state(room_id:int, video_id:str, current_time:float, action:str):
    key = f"room:{room_id}:state"
    state= {
        "video_id":video_id,
        "time":current_time,
        "action":action
    }
    print("-------------in set_room_state")

    print(state)
    redis_client.set(key, json.dumps(state))

def get_room_state(room_id:int):
    key=f"room:{room_id}:state"
    state_json=redis_client.get(key)
    return json.loads(state_json) if state_json else None



class RoomConnectionManager:
    def __init__(self):
        self.rooms: Dict[int, List[tuple[int, WebSocket]]] = {}
        print("[Manager Initialized]")

    async def connect(self, room_id: int, user_id: int, websocket: WebSocket, max_members: int, db: Session):
        print(f"[Connect Attempt] Room: {room_id}, User: {user_id}")

        if room_id not in self.rooms:
            self.rooms[room_id] = []
            print(f"[New Room Created] Room ID: {room_id}")

        if len(self.rooms[room_id]) >= max_members:
            await websocket.accept()
            await websocket.send_json({
                "type": "system",
                "message": "Room is full"
            })
            await websocket.close(code=4001)
            return False

        # Clean up dead connections
        alive = [(u_id, ws) for u_id, ws in self.rooms[room_id] if ws.client_state.name == "CONNECTED"]
        self.rooms[room_id] = alive

        if any(u_id == user_id for u_id, _ in self.rooms[room_id]):
            await websocket.accept()
            await websocket.send_json({
                "type": "system",
                "message": "You are already in the room"
            })
            await websocket.close(code=4002)
            return False

        await websocket.accept()
        self.rooms[room_id].append((user_id, websocket))
        try:
            add_user_to_room(db, room_id, user_id)
        except Exception as e:
            print(f"[DB Error] Failed to add user to room: {e}")

        # Send current room state from Redis
        state = get_room_state(room_id)
        if state:
            await websocket.send_json({
                "type": "video_action",
                "video_id": state["video_id"],
                "time": state["time"],
                "action": state["action"]
            })

        print(f"[User Connected] User: {user_id}, Room: {room_id}, Total Members: {len(self.rooms[room_id])}")
        return True

    def disconnect(self, room_id: int, user_id: int, db: Session):
        if room_id in self.rooms:
            self.rooms[room_id] = [(u_id, ws) for u_id, ws in self.rooms[room_id] if u_id != user_id]
            leave_room(db, room_id, user_id)
            print(f"[User Disconnected] User: {user_id}, Room: {room_id}")
            if not self.rooms[room_id]:
                redis_client.delete(f"room:{room_id}:state")
                del self.rooms[room_id]
                print(f"[Room Empty] Room {room_id} removed")

    async def broadcast(self, room_id: int, message: dict):
        if room_id not in self.rooms:
            print(f"[Broadcast Failed] Room {room_id} does not exist")
            return
        dead_connections = []
        for user_id, conn in self.rooms[room_id]:
            try:
                await conn.send_json(message)
            except Exception as e:
                print(f"[Broadcast Error] Failed sending to User {user_id}: {e}")
                dead_connections.append(user_id)
        self.rooms[room_id] = [(u_id, ws) for u_id, ws in self.rooms[room_id] if u_id not in dead_connections]
        if not self.rooms[room_id]:
            redis_client.delete(f"room:{room_id}:state")
            del self.rooms[room_id]
            print(f"[Room Empty After Broadcast] Room {room_id} removed")

    async def update_host_action(self, room_id:int , video_id:str, current_time:float, action_str:str):
        set_room_state(room_id , video_id, current_time, action_str)
        await self.broadcast(room_id, {
            "type": "video_action",
            "video_id": video_id,
            "time": current_time,
            "action": action_str
        })

    async def kick_user(self, room_id: int, user_to_kick: int, host_id: int, db: Session):
        if room_id not in self.rooms:
            # Send system message to host if the room is not active
            for u_id, ws in self.rooms.get(room_id, []):
                if u_id == host_id:
                    await ws.send_json({"type": "system", "message": "Room is not active"})
            return

        # Check host authorization
        room = get_room_by_id(db, room_id)
        if not room or room.host_id != host_id:
            for u_id, ws in self.rooms.get(room_id, []):
                if u_id == host_id:
                    await ws.send_json({"type": "system", "message": "You are not the room host"})
            return

        for u_id, ws in self.rooms[room_id]:
            if u_id == user_to_kick:
                await ws.send_json({"type": "kicked", "by": host_id})
                await ws.close(code=4000)
                self.disconnect(room_id, user_to_kick, db)
                break
