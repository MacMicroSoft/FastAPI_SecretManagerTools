import os
import uvicorn
from fastapi import FastAPI, Request, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.middleware import Middleware
from starlette.middleware.sessions import SessionMiddleware
from starlette_admin.auth import BaseAuthProvider
from starlette_admin.contrib.sqla import Admin, ModelView
from app.models.models import Note, User, Role, NoteShare, Permission
from app.crud.crud_users import get_password_hash
from app.provider import MyAuthProvider
from app.routes.routers_notes import route_note
from app.routes.routes_users import route_user
from app.database import engine

app = FastAPI()

admin = Admin(
    engine,
    title="Example: Auth",
    base_url="/admin",
    login_logo_url="/admin/statics/logo.svg",
    auth_provider=MyAuthProvider(),
    middlewares=[Middleware(SessionMiddleware, secret_key="mykey")],
)


class UserModelView(ModelView):
    async def create(self, request: Request, data: dict) -> dict:
        if 'hash_password' in data:
            data['hash_password'] = get_password_hash(data['hash_password'])
        return await super().create(request, data)

    async def update(self, request: Request, pk: str, data: dict) -> dict:
        if 'hash_password' in data:
            data['hash_password'] = get_password_hash(data['hash_password'])
        return await super().update(request, pk, data)


admin.add_view(UserModelView(User))
admin.add_view(ModelView(Note))
admin.add_view(ModelView(Role))
admin.add_view(ModelView(Permission))
admin.add_view(ModelView(NoteShare))

app.include_router(route_user)
app.include_router(route_note)
admin.mount_to(app)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)





























# import os
# import uvicorn
# from fastapi import FastAPI, Request, Response
# from sqlalchemy import select
# from sqlalchemy.ext.asyncio import AsyncSession
# from starlette_admin.auth import BaseAuthProvider
# from starlette_admin.contrib.sqla import Admin, ModelView
# from app.models.models import Note, User, Role, NoteShare, Permission
# from app.crud.crud_users import get_password_hash
# from app.routes.routers_notes import route_note
# from app.routes.routes_users import route_user
# from app.database import engine
#
# app = FastAPI()
#
# admin = Admin(engine)
#
# admin.add_view(ModelView(User))
# admin.add_view(ModelView(Note))
# admin.add_view(ModelView(Role))
# admin.add_view(ModelView(Permission))
# admin.add_view(ModelView(NoteShare))
# admin.mount_to(app)
#
# app.include_router(route_user)
# app.include_router(route_note)
#
# if __name__ == "__main__":
#     uvicorn.run(app, host="0.0.0.0", port=8000)
