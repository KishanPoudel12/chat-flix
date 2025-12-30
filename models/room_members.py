from sqlalchemy import ForeignKey, DateTime, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from datetime import datetime
from database import Base

class RoomMember(Base):
    __tablename__ = "room_members"

    id: Mapped[int] = mapped_column(
        primary_key=True,
        index=True
    )

    room_id: Mapped[int] = mapped_column(
        ForeignKey("rooms.id"),
        index=True
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        index=True
    )

    role: Mapped[str] = mapped_column(
        String(50),
        default="member"
    )

    joined_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow
    )

    left_at: Mapped[datetime | None] = mapped_column(
        DateTime,
        nullable=True
    )

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
    room: Mapped["Room"] = relationship(
        "Room",
        back_populates="members"
    )

    # user: Mapped["User"] = relationship(
    #     "User",
    #     back_populates="rooms"
    # )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="joined_rooms"
    )
