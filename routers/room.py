from fastapi import APIRouter, Depends, HTTPException, status, Form
from sqlalchemy.orm import Session
from typing import List, Optional
from schemas.room import RoomCreate, RoomUpdate, RoomResponse
from crud.room import get_rooms, get_room_by_id, create_room, update_room, delete_room
from database import get_db

room_router = APIRouter(
    prefix="/rooms",
    tags=["Rooms"]
)

@room_router.get("/", response_model=List[RoomResponse])
def read_rooms(skip: int = 0, limit: int = 10, db: Session = Depends(get_db)):
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
    host_id: int = Form(...),
    room_description: Optional[str] = Form(None),
    video_url: str = Form(...),
    video_provider: Optional[str] = Form(None),
    is_live: bool = Form(False),
    is_private: bool = Form(False),
    max_members: int = Form(...),
    scheduled_start: Optional[str] = Form(None),
    db: Session = Depends(get_db)
):
    room_data = RoomCreate(
        room_name=room_name,
        host_id=host_id,
        room_description=room_description,
        video_url=video_url,
        video_provider=video_provider,
        is_live=is_live,
        is_private=is_private,
        max_members=max_members,
        scheduled_start=scheduled_start
    )
    room = create_room(db, room_data)
    return room

@room_router.put("/{room_id}", response_model=RoomResponse)
def update_existing_room(room_id: int, data: RoomUpdate, db: Session = Depends(get_db)):
    updated_room = update_room(db, room_id, data)
    return updated_room


@room_router.delete("/{room_id}", response_model=RoomResponse)
def delete_existing_room(room_id: int, db: Session = Depends(get_db)):
    deleted_room = delete_room(db, room_id)
    return deleted_room
