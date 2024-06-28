from datetime import datetime
from typing import Union, Optional

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    email: EmailStr
    username: str


class UserCreate(UserBase):
    hash_password: str


class UserOut(UserBase):
    id: int
    is_active: bool
    is_superuser: bool

    class Config:
        from_attributes = True


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class Role(BaseModel):
    name: str


class NoteCreate(BaseModel):
    user_id: int
    title: str
    content: str


class NoteSchema(BaseModel):
    id: Optional[int]
    title: str
    content: str
    created_at: Optional[datetime]
    user_id: Optional[int]

    class Config:
        from_attributes = True


class UserLogin(BaseModel):
    username: str
    hash_password: str


class NoteList(BaseModel):
    id: Optional[int]
    user_id: Optional[int]

