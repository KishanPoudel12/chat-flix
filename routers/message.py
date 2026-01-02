from fastapi import APIRouter,Depends,HTTPException,status
from sqlalchemy.orm import Session

from crud.message import get_messages, get_message_by_room
from database import get_db
from schemas.message import MessageCreate
from models.user import    User
from auth import  get_current_active_user
from crud.message import  create_message
message_router= APIRouter(
    prefix="/message",
    tags=["Message"]
)

@message_router.get('/')
async def read_messages( room_id:int ,db:Session=Depends(get_db),skip:int=0, limit:int=10):
    return get_messages(db,room_id,skip, limit)

@message_router.get('/{message_id}')
async def read_message_by_id( message_id:int ,db:Session=Depends(get_db),skip:int=0, limit:int=10):
    return get_messages(db,message_id,skip, limit)

@message_router.get('/{room_id}')
async def read_messages_room_id(room_id:int,db:Session=Depends(get_db)):
    return get_message_by_room(db,room_id)


@message_router.post("/")
async def create_new_message( data:MessageCreate, db:Session=Depends(get_db),current_user:User=Depends(get_current_active_user)):
    message= create_message(db, data, current_user)
    if not message:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail="Message Creation Failed")
    return message
