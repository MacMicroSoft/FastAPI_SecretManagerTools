from sqlalchemy import Column, Integer, String, ForeignKey, Table, create_engine, JSON, TIMESTAMP, Boolean
from sqlalchemy.orm import relationship, declarative_base, sessionmaker
from sqlalchemy.sql import func

Base = declarative_base()

# Association tables for many-to-many relationships
user_roles = Table(
    'user_roles', Base.metadata,
    Column('user_id', Integer, ForeignKey('users.id')),
    Column('role_id', Integer, ForeignKey('roles.id'))
)

role_permissions = Table(
    'role_permissions', Base.metadata,
    Column('role_id', Integer, ForeignKey('roles.id')),
    Column('permission_id', Integer, ForeignKey('permissions.id'))
)

notes_permissions = Table(
    'notes_permissions', Base.metadata,
    Column('note_id', Integer, ForeignKey('notes.id')),
    Column('user_id', Integer, ForeignKey('users.id'))
)


class User(Base):
    __tablename__ = 'users'
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True, nullable=False)
    hash_password = Column(String(255), nullable=False)
    email = Column(String(100), unique=True, index=True, nullable=False)
    roles = relationship('Role', secondary=user_roles, back_populates='users')
    notes = relationship('Note', back_populates='user')
    is_active = Column(Boolean, default=True)
    is_superuser = Column(Boolean, default=False)

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
    user_id = Column(Integer, ForeignKey('users.id'))
    user = relationship('User', back_populates='notes')
