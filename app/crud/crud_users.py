# app/crud_users.py
from datetime import datetime, timedelta, timezone
from typing import Optional

from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.database import get_db
from app.models import models
from app.shemas import UserCreate
from app.config import setting
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends

from app.password import oauth2_scheme
from app.shemas import TokenData

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


async def get_user_by_email_crud(db: AsyncSession, email: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.email == email))
    return result.scalars().first()


async def get_user_by_id_crud(db: AsyncSession, user_id: int) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    return result.scalars().first()


async def get_user_by_name_crud(db: AsyncSession, username: str) -> Optional[models.User]:
    result = await db.execute(select(models.User).where(models.User.username == username))
    return result.scalars().first()


async def delete_user_by_id_crud(db: AsyncSession, user_id: int) -> None:
    result = await db.execute(select(models.User).where(models.User.id == user_id))
    user = result.scalar_one_or_none()

    if not user:
        return None

    await db.delete(user)
    await db.commit()
    return user


# async def get_role_id_by_name(db: AsyncSession, name: str) -> Optional[int]:
#     result = await db.execute(select(models.Role).where(models.Role.name == name))
#     role_id = await result.scalar_one_or_none()
#     return role_id


async def create_user(db: AsyncSession, user: UserCreate) -> models.User:
    hashed_password = get_password_hash(user.hash_password)
    db_user = models.User(email=user.email, username=user.username, hash_password=hashed_password)

    db.add(db_user)
    await db.commit()
    await db.refresh(db_user)
    return db_user


def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt


def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta or timedelta(minutes=setting.REFRESH_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    return encoded_jwt


async def decodeJWT(jwtoken: str):
    try:
        payload = jwt.decode(jwtoken, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.JWTError:
        return None


async def verify_jwt(jwtoken: str) -> bool:
    payload = await decodeJWT(jwtoken)
    return payload is not None
