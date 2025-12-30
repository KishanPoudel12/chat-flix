from datetime import datetime

from pydantic import BaseModel
from typing import Optional

class UserBase(BaseModel):
    username: str
    email: str


class UserCreate(UserBase):
    password: str

class UserUpdate(UserBase):
    username: Optional[str] = None
    email : Optional[str]=None
    password: Optional[str]=None

class UserResponse(UserBase):
    is_active: bool
    is_verified: bool
    user_profile:Optional[str]=None
    created_at: datetime
    updated_at: datetime
    model_config = {
        "from_attributes": True
    }