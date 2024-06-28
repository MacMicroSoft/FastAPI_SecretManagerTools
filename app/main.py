import os
import uvicorn
from fastapi import FastAPI, Request, Response

from app.routes.routers_notes import route_note
from app.routes.routes_users import route_user


app = FastAPI()

app.include_router(route_user)
app.include_router(route_note)
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)