from typing import List
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.models import Note, User, Role, Permission, notes_permissions, NoteShare, user_roles
from app.shemas import NoteResponse, NoteCreate


async def get_notes_by_user_crud(db: AsyncSession, user_id: UUID) -> List[NoteResponse]:
    result = await db.execute(
        select(Note)
        .join(User, Note.user)
        .where(User.id == user_id)
    )
    notes = result.scalars().all()

    note_responses = [
        NoteResponse(note_id=note.id, title=note.title, content=note.content)
        for note in notes
    ]

    return note_responses


async def update_note_crud(db: AsyncSession, note_id: int, title: str, content: str, user_id: int):
    result = await db.execute(select(Note).where(Note.id == note_id))
    note = result.scalar_one_or_none()

    if note is None:
        raise HTTPException(
            status_code=404,
            detail="Note not found"
        )

    if note.user_id != user_id:
        raise HTTPException(
            status_code=404,
            detail="You do not have permission to update this note"
        )

    note.title = title
    note.content = content

    db.add(note)
    await db.commit()
    await db.refresh(note)

    return note


async def create_note_crud(db: AsyncSession, user_id: int, title: str, content: str):
    result = await db.execute(
        select(Permission)
        .join(Role, Permission.roles)
        .join(User, Role.users)
        .where(User.id == user_id)
        .where(Permission.name == 'create_notes')
    )
    permission = result.scalars().first()

    if not permission:
        raise HTTPException(status_code=403, detail="User does not have permission to create notes.")

    note = Note(title=title, content=content, user_id=user_id)
    db.add(note)
    await db.commit()
    await db.refresh(note)
    return note


async def get_user_owner_notes(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Note)
        .where(Note.user_id == user_id)
    )
    return result.scalars().all()


async def has_share_permission(db: AsyncSession, user_id: int) -> bool:
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
        raise HTTPException(status_code=403, detail="User does not have permission to share notes.")

    result = await db.execute(
        select(Note)
        .where(Note.id == note_id)
        .where(Note.user_id == from_user_id)
    )
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or does not belong to the user.")

    role_result = await db.execute(
        select(Role.id)
        .join(user_roles, user_roles.c.role_id == Role.id)
        .where(user_roles.c.user_id == to_user_id)
    )
    role_receiver = role_result.scalars().first()
    if not role_receiver:
        raise HTTPException(status_code=404, detail="Role for the recipient user not found.")

    await db.execute(
        NoteShare.__table__.insert().values(note_id=note_id, from_user_id=from_user_id, to_user_id=to_user_id, role_receiver=role_receiver)
    )
    await db.commit()


async def get_notes_by_permissions_from_crud(db: AsyncSession, user_id: UUID) -> List[Note]:
    result = await db.execute(
        select(NoteShare)
        .join(Note, NoteShare.note_id == Note.id)
        .filter(NoteShare.to_user_id == user_id)
    )
    notes_shares = result.scalars().all()
    if not notes_shares:
        raise HTTPException(status_code=404, detail="No notes found that were shared with this user.")

    return [note_share.note for note_share in notes_shares]


async def get_notes_by_permissions_to_crud(db: AsyncSession, user_id: UUID) -> List[NoteShare]:
    result = await db.execute(
        select(NoteShare)
        .where(NoteShare.from_user_id == user_id)
    )
    notes_shares = result.scalars().all()
    if not notes_shares:
        raise HTTPException(status_code=404, detail="No notes found that this user has shared.")

    return notes_shares


# async def get_notes_by_permissions(db: AsyncSession, user_id: int) -> list:
#     result = await db.execute(
#         select(Note)
#         .join(notes_permissions, notes_permissions.c.note_id == Note.id)
#         .where(notes_permissions.c.user_id == user_id)
#     )
#     return list(set(result.scalars().all()))


async def delete_note_by_id_crud(db: AsyncSession, note_id: int, user_id: int) -> None:
    result = await db.execute(
        select(Note)
        .where(Note.id == note_id)
        .where(Note.user_id == user_id)
    )
    note = result.scalar_one_or_none()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found or does not belong to the user.")
    await db.delete(note)
    await db.commit()
    return note