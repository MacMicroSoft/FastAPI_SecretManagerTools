from datetime import datetime
from typing import Union, Optional
from uuid import UUID

from pydantic import BaseModel, EmailStr


class UserBase(BaseModel):
    id: UUID
    email: EmailStr
    username: str


class UserCreate(BaseModel):
    email: EmailStr
    username: str
    hash_password: str
    check_password: str


class UserOut(UserBase):
    id: UUID
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

    title: str
    content: str

    class Config:
        from_attributes = True

class NoteShare(BaseModel):
    to_user_id: UUID
    note_id: int

    class Config:
        from_attributes = True


class NoteSchema(BaseModel):
    id: Optional[UUID]
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
    id: Optional[UUID]
    user_id: Optional[UUID]


class UserResponse(BaseModel):
    id: UUID
    email: EmailStr
    created_at: datetime

    class Config:
        from_attributes = True


class EmailSchema(BaseModel):
    email: EmailStr


class NoteResponse(BaseModel):
    note_id: int
    title: str
    content: str

    class Config:
        from_attributes = True


class ResetToken(BaseModel):
    reset_token: str
