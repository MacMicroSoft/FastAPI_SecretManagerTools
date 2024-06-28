from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from app.database import get_db
from app.models.models import Note
from app.shemas import NoteCreate, UserOut, NoteList
from app.crud.crud_notes import get_notes_by_user, create_note, get_user_owner_notes, share_note_permission, \
    get_notes_by_permissions
from app.routes.routes_users import get_current_active_user, http_bearer

route_note = APIRouter(prefix="/note", tags=["Notes"], dependencies=[Depends(http_bearer)])


@route_note.post("/create/", response_model=NoteCreate)
async def create_note_route(note_data: NoteCreate, db: AsyncSession = Depends(get_db)):
    return await create_note(db, note_data.user_id, note_data.title, note_data.content)


@route_note.get("/list", response_model=List[NoteCreate])
async def get_notes_route(
        user_id: int,
        current_user: UserOut = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access these notes",
        )
    return await get_notes_by_user(db, user_id)


@route_note.post("/share/")
async def share_note(
        from_user_id: int,
        to_user_id: int,
        note_id: int,
        db: AsyncSession = Depends(get_db),
        current_user: UserOut = Depends(get_current_active_user)
):
    if current_user.id != from_user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to share these notes",
        )

    await share_note_permission(db, from_user_id, to_user_id, note_id)
    return {"detail": "Note shared successfully"}


@route_note.get("/permission/list", response_model=List[NoteCreate])
async def get_notes_route(
        user_id: int,
        current_user: UserOut = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access these notes",
        )
    return await get_notes_by_permissions(db, user_id)
