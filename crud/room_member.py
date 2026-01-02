from datetime import datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from crud.room import get_room_by_id
from models.room_members import RoomMember


def get_users_in_room(db:Session, room_id:int):
    members= db.query(RoomMember).filter(RoomMember.room_id==room_id,RoomMember.left_at.is_(None)).all()
    return members

def add_user_to_room(db:Session, room_id:int , user_id:int ):
    members_in_the_given_room= get_users_in_room(db, room_id )
    for member in members_in_the_given_room:
        if member.user_id == user_id:
            return member

    role= "member"
    if members_in_the_given_room:
        if members_in_the_given_room[0].room.host_id == user_id:
            role = "admin"
    else:
        role="admin"


    user_to_add= RoomMember(
        room_id=room_id,
        user_id=user_id,
        role=role,
        joined_at=datetime.utcnow()
    )

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
    db.commit()
    db.refresh(member)
    return member