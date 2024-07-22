import uuid
from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine, JSON, TIMESTAMP, Boolean
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.sql import func
from sqlalchemy.ext.asyncio import AsyncSession

Base = declarative_base()

user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', PGUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE')),
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE'))
)

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id', ondelete='CASCADE')),
    Column('permission_id', Integer, ForeignKey('permissions.id', ondelete='CASCADE'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(PGUUID(as_uuid=True), primary_key=True, default=uuid.uuid4, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hash_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    roles = relationship('Role', secondary=user_roles, lazy="selectin", back_populates='users', cascade='all, delete')
    notes = relationship('Note', back_populates='user', cascade='all, delete-orphan')
    is_active = Column(Boolean, default=False)
    is_superuser = Column(Boolean, default=False)

    def principals(self):
        return [f"user:{self.username}"]


class Role(Base):
    __tablename__ = 'roles'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), unique=True, index=True, nullable=False)
    users = relationship('User', secondary=user_roles, back_populates='roles')
    permissions = relationship('Permission', secondary=role_permissions, back_populates='roles')


class Permission(Base):
    __tablename__ = 'permissions'
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    details = Column(JSON, nullable=False)
    roles = relationship('Role', secondary=role_permissions, back_populates='permissions')


class Note(Base):
    __tablename__ = 'notes'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(100), nullable=False)
    content = Column(String, nullable=False)
    created_at = Column(TIMESTAMP, server_default=func.now())
    user_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))

    user = relationship('User', back_populates='notes')
    shares = relationship('NoteShare', back_populates='note', cascade='all, delete-orphan')


class NoteShare(Base):
    __tablename__ = 'shared_notes'
    id = Column(Integer, primary_key=True, index=True)
    note_id = Column(Integer, ForeignKey('notes.id', ondelete='CASCADE'))
    from_user_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    to_user_id = Column(PGUUID(as_uuid=True), ForeignKey('users.id', ondelete='CASCADE'))
    role_receiver = Column(Integer, ForeignKey('roles.id'), nullable=False)

    note = relationship('Note', back_populates='shares')
    from_user = relationship('User', foreign_keys=[from_user_id])
    to_user = relationship('User', foreign_keys=[to_user_id])


Note.shares = relationship('NoteShare', back_populates='note', cascade='all, delete-orphan')
