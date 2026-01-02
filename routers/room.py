from fastapi import APIRouter, Depends, HTTPException, status, Form,Request
from sqlalchemy.orm import Session
from typing import List, Optional
from auth import get_current_active_user
from schemas.room import RoomCreate, RoomUpdate, RoomResponse
from crud.room import get_rooms, get_room_by_id, create_room, update_room, delete_room
from database import get_db
from models import  User
from datetime import datetime
from jose import jwt,JWTError
import os
room_router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

def get_user_from_cookie(request:Request,db:Session =Depends(get_db) ):
    token = request.cookies.get("access_token")
    if not token :
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No Token Found on Users cookie")
    if token.startswith("Bearer "):
        token = token[7:]
    try:
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        user_id= payload.get("user_id")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token")
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user


@room_router.get("/{room_id}/role")
def get_room_role(room_id:int , current_user:User=Depends(get_user_from_cookie),db:Session=Depends(get_db)):
    room = get_room_by_id(db,room_id)
    if not room:
        raise HTTPException(status_code=404, detail="Room not found")
    is_admin= current_user.id==room.host_id
    return {"is_admin": is_admin}



@room_router.get("/", response_model=List[RoomResponse])
def read_all_rooms(skip: int = 0, limit: int = 10, db: Session = Depends(get_db),current_user:User=Depends(get_current_active_user)):
    rooms = get_rooms(db, skip=skip, limit=limit)
    return rooms

@room_router.get("/{room_id}", response_model=RoomResponse)
def read_room(room_id: int, db: Session = Depends(get_db)):
    room = get_room_by_id(db, room_id)
    return room


# POST create a new room
@room_router.post("/create", response_model=RoomResponse, status_code=status.HTTP_201_CREATED)
def create_new_room(
    room_name: str = Form(...),
    room_description: Optional[str] = Form(None),
    video_url: str = Form(...),
    video_provider: Optional[str] = Form(None),
    # is_live: bool = Form(False),
    is_private: bool = Form(False),
    max_members: int = Form(...),
    # scheduled_start: Optional[datetime] = Form(None),
    db: Session = Depends(get_db),
    current_user:User=Depends(get_current_active_user)
):
    room_data = RoomCreate(
        room_name=room_name,
        host_id=current_user.id,
        room_description=room_description,
        video_url=video_url,
        video_provider=video_provider,
        is_live=True,
        is_private=is_private,
        max_members=max_members,
        scheduled_start=datetime.utcnow()
    )
    room = create_room(db, room_data)
    return room

@room_router.put("/{room_id}", response_model=RoomResponse)
def update_existing_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db),current_user:User=Depends(get_current_active_user)):
    if not current_user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User Not Found ")
    updated_room = update_room(db, room_id,current_user.id,  data)
    return updated_room


@room_router.delete("/{room_id}", response_model=RoomResponse)
def delete_existing_room(room_id: int, db: Session = Depends(get_db),current_user:User=Depends(get_current_active_user)):
    deleted_room = delete_room(db, room_id, current_user.id)
    return deleted_room
