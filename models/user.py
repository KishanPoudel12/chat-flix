
from sqlalchemy.orm import relationship, Mapped, mapped_column
from database import Base
from sqlalchemy import Column, Integer, String, DateTime,Boolean
from datetime import datetime

'''
what a user should have in my idea:
    id ,
    username ,
    user_profile ,
    email,
    password,
    is_active,
    created_at,
    updated_at,
'''


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True
    )

    username: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True
    )

    user_profile: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    email: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        unique=True,
        index=True
    )

    hashed_password: Mapped[str] = mapped_column(
        String(100),
        nullable=False
    )

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
    is_verified: Mapped[bool] = mapped_column(
        Boolean,
        default=True
    )
    is_guest: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # Relationships
    rooms: Mapped[list["Room"]] = relationship(
        "Room",
        cascade="all, delete-orphan",
        back_populates="host"
    )

    joined_rooms: Mapped[list["RoomMember"]] = relationship("RoomMember", back_populates="user")


    messages: Mapped[list["Message"]] = relationship("Message",
    cascade="all, delete-orphan",
    back_populates="sender"
    )





