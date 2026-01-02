from sqlalchemy.orm import Mapped, relationship
from sqlalchemy.testing.schema import mapped_column
from database import Base
from sqlalchemy import Column, DateTime, Integer, String, ForeignKey,Text
from datetime import datetime
'''
in my opinion the message should include 
    id ,
    sender id ,
    receiver id ,
    room_it_belongs,
    mesage ,
    created_at ,
    updated_at ,
'''

class Message(Base):
    __tablename__ = "messages"
    id :Mapped[int]= mapped_column(Integer, primary_key=True)
    sender_id :Mapped[int]= mapped_column(ForeignKey("users.id",ondelete="SET NULL"))
    sender_username:Mapped[str]=mapped_column(String, nullable=True)
    room_id:Mapped[int|None]= mapped_column(ForeignKey("rooms.id", ondelete="CASCADE"),nullable=True)
    message:Mapped[str]= mapped_column(Text,nullable=True)
    created_at:Mapped[datetime]= mapped_column(DateTime,default=datetime.utcnow)
    updated_at:Mapped[datetime]= mapped_column(DateTime,default=datetime.utcnow, onupdate=datetime.utcnow)

    #Relationships
    room:Mapped["Room"]= relationship("Room", back_populates="messages")
    sender:Mapped["User"]=relationship("User", back_populates="messages",  passive_deletes=True
)

