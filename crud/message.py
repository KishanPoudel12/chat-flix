from fastapi import  status, HTTPException
from sqlalchemy.orm import Session
from models import  Message
from utils import pagination
from models import  User
from schemas.message import  MessageCreate

def get_messages(db:Session,room_id:int, skip:int=0, limit:int =10):
    query= db.query(Message).filter(Message.room_id==room_id)
    return pagination(query, skip , limit)

def get_message_by_id(db:Session, message_id:int=0):
    message= db.query(Message).filter(Message.id == message_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message Not Found")
    return message
def get_message_by_room(db:Session, room_id:int=0):
    message= db.query(Message).filter(Message.room_id == room_id).first()
    if not message:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Message Not Found")
    return message
def create_message(db,data:MessageCreate, current_user:User):
    message= Message(
        sender_id=current_user.id,
        sender_username=current_user.username,
        room_id=data.room_id,
        message=data.message
    )
    db.add(message)
    db.commit()
    db.refresh(message)
    return message



