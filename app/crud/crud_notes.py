from typing import List, Optional
from uuid import UUID
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.models import Note, User, Role, Permission, NoteShare, user_roles
from app.shemas import NoteResponse, NoteCreate
from app.exeptions.exception_note import NotePermissionException, NoteFoundNoteException, NoteAlreadySharedException


async def get_note_by_id_crud(db: AsyncSession, note_id: int) -> Note:
    note = await db.get(Note, note_id)
    return note


async def get_notes_by_user_crud(db: AsyncSession, user_id: UUID) -> List[NoteResponse]:
    result = await db.execute(
        select(Note)
        .join(User, Note.user)
        .where(User.id == user_id)
    )
    notes = result.scalars().all()
    note_responses = [NoteResponse(note_id=note.id, title=note.title, content=note.content) for note in notes]
    return note_responses


async def update_note_crud(db: AsyncSession, note_id: int, title: str, content: str, user_id: UUID):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()
    if note is None:
        raise NoteFoundNoteException()
    if note.user_id != user_id:
        raise NotePermissionException()
    note.title = title
    note.content = content
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def create_note_crud(db: AsyncSession, user_id: UUID, title: str, content: str):
    result = await db.execute(
        select(Permission)
        .join(Role, Permission.roles)
        .join(User, Role.users)
        .where(User.id == user_id)
        .where(Permission.name == 'create_notes')
    )
    permission = result.scalars().first()
    if not permission:
        raise NotePermissionException()
    note = Note(title=title, content=content, user_id=user_id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_user_owner_notes(db: AsyncSession, user_id: UUID):
    result = await db.execute(
        select(Note)
        .where(Note.user_id == user_id)
    )
    return result.scalars().all()


async def has_share_permission(db: AsyncSession, user_id: UUID) -> bool:
    result = await db.execute(
        select(Permission)
        .join(Role, Permission.roles)
        .join(User, Role.users)
        .where(User.id == user_id)
        .where(Permission.name == 'share_notes')
    )
    permission = result.scalars().first()
    return permission is not None


async def share_note_permission(db: AsyncSession, from_user_id: UUID, to_user_id: UUID, note_id: int):
    if not await has_share_permission(db, from_user_id):
        raise NotePermissionException()
    check_exist = await db.execute(
        select(NoteShare).filter_by(note_id=note_id, from_user_id=from_user_id, to_user_id=to_user_id)
    )
    share = check_exist.scalars().first()
    if share:
        raise NoteAlreadySharedException()
    result = await db.execute(
        select(Note)
        .where(Note.id == note_id)
        .where(Note.user_id == from_user_id)
    )
    note = result.scalars().first()

    if not note:
        note_shared_result = await db.execute(
            select(NoteShare)
            .where(NoteShare.note_id == note_id)
            .where(NoteShare.to_user_id == from_user_id)
        )
        note = note_shared_result.scalars().first()
        if not note:
            raise NotePermissionException()

    role_result = await db.execute(
        select(Role.id)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(user_roles.c.user_id == to_user_id)
    )
    role_receiver = role_result.scalars().first()
    if not role_receiver:
        raise HTTPException(status_code=404, detail="Role for the recipient user not found.")
    await db.execute(
        NoteShare.__table__.insert().values(note_id=note_id, from_user_id=from_user_id, to_user_id=to_user_id,
                                            role_receiver=role_receiver)
    )
    await db.commit()


async def get_notes_by_permissions_from_crud(db: AsyncSession, user_id: UUID) -> List[NoteShare]:
    result = await db.execute(
        select(NoteShare)
        .where(NoteShare.to_user_id == user_id)
    )
    notes_shares = result.scalars().all()
    if not notes_shares:
        raise NoteFoundNoteException()
    return notes_shares


async def get_notes_by_permissions_to_crud(db: AsyncSession, user_id: UUID) -> List[NoteShare]:
    result = await db.execute(
        select(NoteShare)
        .where(NoteShare.from_user_id == user_id)
    )
    notes_shares = result.scalars().all()
    if not notes_shares:
        raise NoteFoundNoteException()
    return notes_shares


async def delete_note_by_id_crud(db: AsyncSession, note_id: int, user_id: UUID) -> None:
    result = await db.execute(
        select(Note)
        .where(Note.id == note_id)
        .where(Note.user_id == user_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise NotePermissionException()

    await db.delete(note)
    await db.commit()
    return note
