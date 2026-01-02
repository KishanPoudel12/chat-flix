from typing import Optional

from pydantic import  BaseModel
from datetime import datetime

from models import RoomMember

class RoomMemberResponse(BaseModel):
    id: int
    user_id: int
    joined_at: datetime

    class Config:
        orm_mode = True

class RoomBase(BaseModel):
    room_name:str
    host_id:int
    room_description:Optional[str]=None
    video_url:str
    video_provider:Optional[str]=None
    is_live:bool
    is_private:bool
    max_members:int
    scheduled_start:datetime

class RoomCreate(RoomBase):
    pass

class RoomUpdate(BaseModel):
    room_name: Optional[str] = None
    room_description: Optional[str] = None
    video_url: Optional[str] = None
    video_provider: Optional[str] = None
    is_live: Optional[bool] = None
    is_private: Optional[bool] = None
    max_members: Optional[int] = None
    scheduled_start: Optional[datetime] = None


class RoomResponse(RoomBase):
    id:int
    members:list[RoomMemberResponse]
    pass



