from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List, Optional

from app.database import get_db
from app.models.models import Note, User
from app.shemas import NoteCreate, UserOut, NoteList, NoteShare, NoteResponse
from app.crud.crud_notes import get_user_owner_notes, share_note_permission, \
    delete_note_by_id_crud, create_note_crud, get_notes_by_user_crud, update_note_crud, \
    get_notes_by_permissions_from_crud, get_notes_by_permissions_to_crud, get_note_by_id_crud
from app.routes.routes_users import get_current_active_user, http_bearer, get_current_user

route_note = APIRouter(prefix="/note", tags=["Notes"], dependencies=[Depends(get_current_active_user)])


@route_note.post("/create/", response_model=NoteCreate)
async def create_note(
        note_data: NoteCreate,
        db: AsyncSession = Depends(get_db),
        current_user: User = Depends(get_current_user)
):
    user_id = current_user.id
    return await create_note_crud(db, user_id, note_data.title, note_data.content)


@route_note.get("/list/me/", response_model=List[NoteResponse])
async def list_notes(
        current_user: UserOut = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id

    if current_user.id != user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to access these notes",
        )

    return await get_notes_by_user_crud(db, user_id)


@route_note.post("/share/", response_model=dict, status_code=status.HTTP_200_OK)
async def share_note(
        share: NoteShare,
        db: AsyncSession = Depends(get_db),
        current_user: UserOut = Depends(get_current_active_user)
):
    from_user_id = current_user.id

    await share_note_permission(db, from_user_id, share.to_user_id, share.note_id)

    return Response(status_code=status.HTTP_200_OK)


@route_note.get("/shared/to/others/", response_model=List[NoteShare], status_code=status.HTTP_200_OK)
async def list_shareable_notes_to(
        current_user: UserOut = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    await get_notes_by_permissions_to_crud(db, user_id)

    return Response(status_code=status.HTTP_200_OK)


@route_note.get("/shared/from/others/", response_model=List[NoteShare], status_code=status.HTTP_200_OK)
async def list_shareable_notes_from(
        current_user: UserOut = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    user_id = current_user.id
    await get_notes_by_permissions_from_crud(db, user_id)

    return Response(status_code=status.HTTP_200_OK)


@route_note.delete("/{note_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_note_by_id(
        note_id: int,
        current_user: UserOut = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    note = await delete_note_by_id_crud(db, note_id=note_id, user_id=current_user.id)

    if note is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Note not found or does not belong to the user"
        )

    return Response(status_code=status.HTTP_204_NO_CONTENT)


@route_note.put("/{note_id}", response_model=NoteCreate, status_code=status.HTTP_200_OK)
async def update_note(
        note_id: int,
        title: Optional[str] = None,
        content: Optional[str] = None,
        current_user: UserOut = Depends(get_current_active_user),
        db: AsyncSession = Depends(get_db)
):
    current_note = await get_note_by_id_crud(db, note_id=note_id)
    if not current_note:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Note not found")

    updated_title = title if title is not None else current_note.title
    updated_content = content if content is not None else current_note.content

    updated_note = await update_note_crud(db, note_id, updated_title, updated_content, current_user.id)

    return updated_note
