from pydantic import BaseModel, EmailStr, Field
from datetime import datetime
from typing import Optional


class UserCreate(BaseModel):
    email: EmailStr
    password: str
    name: str = Field(max_length=20)

class MessageCreate(BaseModel):
    text: str
    dialog_id: int


# schemas.py
class UserResponse(BaseModel):
    user_id: int
    email: EmailStr
    name: Optional[str] = None       
    created_at: datetime
    class Config:
        orm_mode = True

class DialogCreate(BaseModel):
    user_id: int
    name: str

class DialogResponse(BaseModel):
    dialog_id: int
    user_id: int
    name: str
    created_at: datetime
    class Config:
        orm_mode = True

class MessageResponse(BaseModel):
    message_id: int
    dialog_id: int
    type: str
    text: str
    created_at: datetime
    class Config:
        orm_mode = True