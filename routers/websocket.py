from fastapi import APIRouter,WebSocket,Depends,status, HTTPException
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from crud.message import get_messages
from crud.room import get_room_by_id
from database import get_db
from models.user import  User
from websocket.manager import RoomConnectionManager
from auth import  get_current_user

ws_router= APIRouter(
    prefix="/ws",
    tags=["Websocket"]
)
manager= RoomConnectionManager()


@ws_router.websocket("/rooms/{room_id}")
async def join(room_id:int , websocket:WebSocket, db:Session=Depends(get_db)):
    room= get_room_by_id(db, room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Unable to find the Room")

    if not room.is_live :
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="The Room is not live")

    #takign the token out from the cookies
    token = websocket.cookies.get("access_token")
    print(f"------------{token}-----------")
    if not token :
        await websocket.close(code=1008, reason="No token provided ")
        return
    token = token.replace("Bearer ", "")
    current_user =await  get_current_user(token, db)

    old_messages= get_messages(db, room_id,skip=0, limit=50)

    try :
        await manager.connect(room_id, current_user.id, websocket, room.max_members )

        for msg in old_messages:
            await manager.broadcast(room_id,f"User {msg.sender_username} : {msg.message} ")
        broadcast_message = f"User {current_user.username} Joined the Rooom"
        await manager.broadcast(room_id,broadcast_message )
    except Exception as e:
        print(f"Error :{e}")
        await websocket.close(code=1008)
        return

    try :
        while True :
            data = await websocket.receive_text()
            await manager.broadcast(room_id, f" User {current_user.username} :- {data}")
    except WebSocketDisconnect:
        manager.disconnect(room_id, user_id=current_user.id)
        await manager.broadcast(room_id,f"User {current_user.id} left the Room" )




