from fastapi import APIRouter,WebSocket,Depends,status, HTTPException
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from crud.room import get_room_by_id
from database import get_db
from websocket.manager import RoomConnectionManager

manager= RoomConnectionManager()
ws_router= APIRouter(
    prefix="/ws",
    tags=["Websocket"]
)

@ws_router.websocket("/rooms/{room_id}")
async def join_room(room_id:int, websocket:WebSocket,db:Session=Depends(get_db)):
    try:
        room = get_room_by_id(db, room_id)
        if not room:
            print(f"[WS ERROR] Room {room_id} not found")
            raise HTTPException(status_code= status.HTTP_404_NOT_FOUND, detail= "Room Not Found")
        if not room.is_live:
            print(f"[WS ERROR] Room {room_id} not live")
            await websocket.close(code=1008)
            return

        success = await manager.connect(room_id, websocket, max_members=room.max_members)
        if not success:
            print(f"[WS ERROR] Room {room_id} is full")
            return
        try :
            while True:
                data = await  websocket.receive_text()
                print(f"[WS MESSAGE] Room {room_id}: {data}")
                await manager.broadcast(room_id, data)
        except WebSocketDisconnect :
            print(f"[WS DISCONNECT] User left room {room_id}")

            manager.disconnect(room_id, websocket)

    except Exception as e:
        print(f"[WS FATAL ERROR] Room {room_id}: {e}")
        await websocket.close(code=1011, reason="Internal server error")