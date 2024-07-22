from datetime import timedelta, datetime
from fastapi import APIRouter, Depends, HTTPException, status, Response, BackgroundTasks
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from starlette.responses import RedirectResponse

from app import shemas
from app.config import setting
from app.crud.crud_users import (
    get_user_by_email_crud,
    create_user,
    create_access_token,
    get_user_by_name_crud,
    verify_password,
    get_user_by_id_crud,
    delete_user_by_id_crud,
    get_password_hash,
)
from app.database import get_db
from app.models import models
from app.models.models import User, Role
from app.shemas import UserCreate, UserOut, Token, TokenData, UserBase, EmailSchema
from fastapi_mail import MessageSchema, FastMail
from app.email_config import conf
from sqlalchemy.future import select
import aioredis

route_user = APIRouter(prefix="/auth", tags=["Authentication"])
redis_url = "redis://redis:6379"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")
http_bearer = HTTPBearer()


async def get_redis():
    return aioredis.from_url(redis_url)

@route_user.get("/")
async def read_root(redis: aioredis.Redis = Depends(get_redis)):
    try:
        await redis.set("key", "value")
        value = await redis.get("key")
        return {"message": f"Redis value: {value.decode('utf-8')}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Redis error: {e}")



@route_user.post("/login", response_model=shemas.Token)
async def login_user(
    response: Response,
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_name_crud(db, form_data.username)
    if not user or not verify_password(form_data.password, user.hash_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=setting.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)

    response.set_cookie(
        key="access_token",
        value=access_token,
        httponly=True,
        samesite='Strict'
    )

    return {"access_token": access_token, "token_type": "bearer"}


@route_user.get("/logout")
async def logout_user(response: Response):
    response.delete_cookie(key="access_token")
    return {"message": "Logged out successfully"}


async def get_current_user(
    request: Request, db: AsyncSession = Depends(get_db)
) -> User:
    token = request.cookies.get("access_token")
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if token.startswith("Bearer "):
        token = token[len("Bearer "):]

    try:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = await get_user_by_name_crud(db, username)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


async def get_current_active_user(current_user: models.User = Depends(get_current_user)):
    if not current_user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


@route_user.post("/register", response_model=UserOut)
async def register_user(payload: UserCreate, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    if not payload.email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Please provide an email address"
        )
    user = await get_user_by_email_crud(db, payload.email)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"User with email {payload.email} already exists"
        )

    if payload.hash_password != payload.check_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"You have two different passwords"
        )
    created_user = await create_user(db, payload)

    default_role = await db.execute(select(Role).filter_by(name="visitor"))
    default_role = default_role.scalars().first()

    if not default_role:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Default role not found"
        )

    created_user.roles.append(default_role)
    await db.commit()

    token_data = {
        "sub": payload.email,
        "exp": datetime.utcnow() + timedelta(minutes=5),
    }

    token = jwt.encode(token_data, setting.SECRET_KEY, algorithm=setting.ALGORITHM)

    confirm_token = f"http://{setting.SERVER}:8000/auth/confirm-email?token={token}"

    message = MessageSchema(
        subject="Email Confirmation",
        recipients=[payload.email],
        body=f"Please copy the token and paste into your form: {confirm_token}",
        subtype="html"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

    return created_user


@route_user.get("/confirm-email")
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Please provide a valid email address"
            )
        user = await get_user_by_email_crud(db, email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"User with email {email} does not exist"
            )
        user.is_active = True
        await db.commit()
        return {"message": "Email confirmed successfully"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )


@route_user.post("/forgot-password", status_code=status.HTTP_200_OK)
async def forgot_password(request: EmailSchema, background_tasks: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    user = await get_user_by_email_crud(db, request.email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User with this email does not exist"
        )
    token_data = {
        "sub": request.email,
        "exp": datetime.utcnow() + timedelta(hours=1),
    }

    token = jwt.encode(token_data, setting.SECRET_KEY, algorithm=setting.ALGORITHM)
    reset_token = f"Please copy the token and paste into the form: {token}"

    message = MessageSchema(
        subject="Password Reset Request",
        recipients=[request.email],
        body=f"{reset_token}",
        subtype="html"
    )

    fm = FastMail(conf)
    background_tasks.add_task(fm.send_message, message)

    return {"message": "Password reset email sent"}


@route_user.post("/reset-password", status_code=status.HTTP_200_OK)
async def reset_password(token: str, new_password: str, db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=[setting.ALGORITHM])
        email = payload.get("sub")
        if email is None:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid token"
            )
        user = await get_user_by_email_crud(db, email)
        if user is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )

        hashed_password = get_password_hash(new_password)
        user.hash_password = hashed_password
        await db.commit()

        return {"message": "Password reset successful"}
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token"
        )


@route_user.get("/users/me/", response_model=UserOut)
async def read_users_me(
        current_user: UserOut = Depends(get_current_active_user),
):
    return current_user


@route_user.get("/user/{user_id}", response_model=UserBase)
async def get_user_by_id(
        user_id: int,
        current_user: UserBase = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    user = await get_user_by_id_crud(db, user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User in not found")
    return user


@route_user.get("/user/name/{user_name}", response_model=UserBase)
async def get_user_by_name(user_name: str, current_user: UserBase = Depends(get_current_active_user, ),
                           db: AsyncSession = Depends(get_db)):
    user = await get_user_by_name_crud(db, user_name)
    if user is None:
        raise HTTPException(status_code=404, detail="User in not found")
    return user


@route_user.delete("/user/{user_id}")
async def delete_user_by_id(
        user_id: int,
        current_user: UserOut = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.is_superuser:
        user = await delete_user_by_id_crud(db, user_id)
        if user:
            return Response(
                status_code=204,
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="User not found"
            )
    else:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User don't have permission"
        )
