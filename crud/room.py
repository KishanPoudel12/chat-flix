from fastapi import  status, HTTPException
from sqlalchemy.orm import Session
from models import  Room
from schemas.room import RoomCreate,RoomUpdate
from utils import pagination


def get_rooms(db:Session, skip:int=0, limit:int=0):
    query= db.query(Room)
    rooms= pagination(query, skip, limit)
    if not rooms:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Room Not Found")
    return rooms

def get_room_by_id(db:Session, room_id:int):
    room = db.query(Room).filter(Room.id==room_id).first()
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND , detail="Room Not Found")
    return room


# {
#   "room_name": "string",
#   "host_id": 1,   ->> i will set up from the jwt verification one
#   "room_description": "string",
#   "video_url": "string",
#   "video_provider": "string",
#   "is_live": true,    --> if current time > scheduled time , automatic islive =True
#   "is_private": true,
#   "max_members": 20,  --> will only keep
#   "scheduled_start": "2025-12-30T20:52:32.836000"
# }



def create_room(db:Session, data:RoomCreate):
    room_data= Room(**data.model_dump())
    db.add(room_data)
    db.commit()
    return room_data

def update_room(db:Session , room_id:int , data:RoomUpdate):
    get_updating_room= db.query(Room).filter(Room.id==room_id).first()
    if not get_updating_room:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No Room Found ")
    update_data= data.model_dump()
    for key , value in  update_data.items():
        setattr(get_updating_room, key, value)

    db.commit()
    db.refresh(get_updating_room)
    return get_updating_room


def delete_room(db:Session, room_id :int ):
    get_deleting_room= db.query(Room).filter(Room.id==room_id)
    if not get_deleting_room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Room Found to delete ")
    db.delete(get_deleting_room)
    db.commit()
    return get_deleting_room


