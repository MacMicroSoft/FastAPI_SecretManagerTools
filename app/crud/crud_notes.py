from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException
from app.models.models import Note, User, notes_permissions, Permission, Role


async def get_notes_by_user(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Note)
        .join(User, Note.user)
        .join(notes_permissions, (notes_permissions.c.note_id == Note.id) & (notes_permissions.c.user_id == user_id))
        .where(User.id == user_id)
    )
    return result.scalars().all()


async def create_note(db: AsyncSession, user_id: int, title: str, content: str):
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


async def share_note_permission(db: AsyncSession, from_user_id: int, to_user_id: int, note_id: int):
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

    await db.execute(
        notes_permissions.insert().values(note_id=note_id, user_id=to_user_id)
    )
    await db.commit()


async def get_notes_by_permissions(db: AsyncSession, user_id: int):
    result = await db.execute(
        select(Note)
        .join(notes_permissions, notes_permissions.c.note_id == Note.id)
        .where(notes_permissions.c.user_id == user_id)
    )
    return list(set(result.scalars().all()))
