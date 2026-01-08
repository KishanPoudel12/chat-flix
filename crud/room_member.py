from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from crud.room import get_room_by_id
from crud.user import get_user_by_id
from models.room_members import RoomMember


def get_users_in_room(db:Session, room_id:int):
    members= db.query(RoomMember).filter(RoomMember.room_id==room_id,RoomMember.left_at.is_(None)).all()
    return members

def add_user_to_room(db:Session, room_id:int , user_id:int ):
    existing_member = db.query(RoomMember).filter_by(room_id=room_id, user_id=user_id).first()
    if existing_member:
        return existing_member

    members_in_the_given_room = get_users_in_room(db, room_id)
    role= "member"
    if members_in_the_given_room:
        if members_in_the_given_room[0].room.host_id == user_id:
            role = "admin"
    else:
        role="admin"
    user = get_user_by_id(db, user_id)
    user_to_add= RoomMember(
        room_id=room_id,
        user_id=user_id,
        username=user.username,
        role=role,
        joined_at=datetime.utcnow()
    )
    increment_current_members(db, room_id, +1)
    db.add(user_to_add)
    db.commit()
    db.refresh(user_to_add)
    return user_to_add

def remove_user_from_room(db:Session, room_id:int , target_user:int , host_id:int ):
    room= get_room_by_id(db,room_id)
    if not room:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Room Not Found")

    if room.host_id!= host_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Only Host can remove a user")

    member= db.query(RoomMember).filter(
    RoomMember.room_id==room_id,RoomMember.user_id==target_user,
        RoomMember.left_at.is_(None)
    )
    if not member:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Member Not Present in the Room")
    increment_current_members(db, room_id, -1)

    member.left_at=datetime.utcnow()
    db.commit()
    db.refresh(member)
    return member


def leave_room(db:Session , room_id:int , user_id:int):
    member= db.query(RoomMember).filter(
        RoomMember.room_id == room_id,
        RoomMember.user_id == user_id,
        RoomMember.left_at.is_(None)
    ).first()
    if not member:
        return None
    member.left_at= datetime.utcnow()
    increment_current_members(db, room_id, -1)
    db.commit()
    db.refresh(member)
    return member



def increment_current_members(db: Session, room_id: int, delta: int):
    room = get_room_by_id(db, room_id)
    if not room:
        return

    if room.current_members is None:
        room.current_members = 0

    room.current_members = max(0, room.current_members + delta)