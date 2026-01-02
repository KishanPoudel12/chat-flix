from fastapi import APIRouter,WebSocket,Depends,status, HTTPException
from sqlalchemy.orm import Session
from starlette.websockets import WebSocketDisconnect

from crud.message import get_messages
from crud.room import get_room_by_id
from database import get_db
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
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="The User is Inactive")

    old_messages= get_messages(db, room_id,skip=0, limit=50)

    try :
        await manager.connect(room_id, current_user.id, websocket, room.max_members ,db)
        for msg in old_messages:
            await websocket.send_json({
                "type":"chat",
                "message":f"User {msg.sender_username} : {msg.message}"
            })

        broadcast_message = {"type":"system","message":f"User {current_user.username} Joined the Room"}
        await manager.broadcast(room_id,broadcast_message)

    except Exception as e:
        print(f"Error :{e}")
        await websocket.close(code=1008)
        return
    try :
        while True :
            data = await websocket.receive_json()
            if data.get("type")=="video_action" and room.host_id==current_user.id:
                await manager.update_host_action(
                    room_id=room_id,
                    video_id=data["video_id"],
                    current_time=data["time"],
                    action_str=data["action"]
                )
            elif data.get("type")=="chat" :
                await manager.broadcast(room_id=room_id, message={"type":"chat", "message":f"{current_user.username}:{data["message"]}"})
    except WebSocketDisconnect:
        manager.disconnect(room_id, user_id=current_user.id,db=db)
        await manager.broadcast(room_id,message={"type":"chat", "message":f"User {current_user.id} left the Room"} )





