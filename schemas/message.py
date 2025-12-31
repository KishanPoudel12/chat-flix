from pydantic import BaseModel
from datetime import datetime
from models import Message


class MessageBase(BaseModel):
    room_id :int
    message:str


class MessageCreate(MessageBase):
    pass


class MessageResponse(BaseModel):
    id: int
    sender_id: int
    sender_username: str
    room_id: int
    message: str
    created_at: datetime


    model_config = {
        "from_attributes": True
    }