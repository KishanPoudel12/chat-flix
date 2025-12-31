from fastapi import  HTTPException,status
from fastapi import WebSocket, WebSocketDisconnect
from typing import Dict, List
from sqlalchemy.orm import Session
from crud.room import get_room_by_id

class RoomConnectionManager:
    def __init__(self):
        self.rooms:Dict[int, List[tuple[int, WebSocket]]]={}

    async def connect(self, room_id:int , user_id:int , websocket:WebSocket , max_members:int):
        if room_id not in self.rooms:
            self.rooms[room_id]=[]
        if len(self.rooms[room_id])>=max_members:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room Full")

        user_exist=any(u_id==user_id for u_id ,_ in self.rooms[room_id])

        if user_exist:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Already in the Room")
        await  websocket.accept()
        self.rooms[room_id].append((user_id,websocket))
        return True

    def disconnect(self, room_id :int , user_id:int ):
        if room_id in self.rooms :
            user_exist = any(u_id == user_id for u_id, _ in self.rooms[room_id])
            if user_exist:
                self.rooms[room_id]=[(u_id, ws) for u_id, ws in self.rooms[room_id] if user_id!=u_id]

                if not self.rooms[room_id]:
                    del self.rooms[room_id]
            else :
                print(f"User {user_id} Not in the room ")
        else :
            print(f"Room {room_id} does not Exist")
        return True

    async def broadcast(self, room_id:int , message:str):
        if not room_id in self.rooms:
            return False
        dead_connections=[]
        for user_id,conn in self.rooms[room_id]:
            try:
                await conn.send_text(message)
            except Exception as e:
                print(f"Failed sending to user {user_id} ,Error:{e}")
                dead_connections.append(user_id)
        self.rooms[room_id]=[(u_id , ws ) for u_id, ws in self.rooms[room_id] if u_id not in dead_connections]
        if not self.rooms[room_id]:
            del self.rooms[room_id]
        return True

    async def kick_user(self, room_id:int , user_to_kick:int , host_id:int , db:Session):
        room= get_room_by_id(db,room_id)
        if not room:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room Not Found")
        if room_id not in self.rooms:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Room not in active rooms")

        if host_id != room.host_id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not the room host")

        for u_id ,ws in self.rooms[room_id]:
            if u_id == user_to_kick:
                print(f"User to kick is {u_id}")
                await ws.send_text(f"{host_id} kicked you :)")
                await ws.close(code=4000)
                break

        self.rooms[room_id]= [(u_id, ws) for u_id, ws in self.rooms[room_id] if u_id != user_to_kick]
        if not self.rooms[room_id]:
            del self.rooms[room_id]
        return True