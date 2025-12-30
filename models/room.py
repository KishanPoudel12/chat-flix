from datetime import datetime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text, DateTime
from database import Base


class Room(Base):
    __tablename__ = "rooms"

    id: Mapped[int] = mapped_column(primary_key=True, index=True, nullable=False)
    room_name: Mapped[str] = mapped_column(String(100), nullable=False)
    host_id: Mapped[int] = mapped_column(ForeignKey('users.id'), nullable=False)
    room_description: Mapped[str] = mapped_column(String(255), nullable=False)
    video_url: Mapped[str] = mapped_column(Text, nullable=False)
    video_provider: Mapped[str] = mapped_column(String(50), nullable=False, default='youtube')
    is_live: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    is_private: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    max_members: Mapped[int] = mapped_column(Integer, nullable=False, default=5)
    scheduled_start: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now)
    created_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now)
    updated_at: Mapped[datetime] = mapped_column(DateTime, nullable=True, default=datetime.now, onupdate=datetime.now)

    # Relationships
    members: Mapped[list["RoomMember"]] = relationship("RoomMember", back_populates="room")
    host: Mapped["User"] = relationship("User", back_populates="rooms")
    messages:Mapped[list["Message"]] = relationship("Message", back_populates="room")
