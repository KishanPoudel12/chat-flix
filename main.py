from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database import create_db
from websocket.demo import html
#routers import
from routers import user_router, ws_router,message_router,room_router
from auth import  auth_router

app = FastAPI()

@app.get("/")
async def root():
    return HTMLResponse(html)

@app.on_event("startup")
async def startup():
    import models
    return create_db()


#routers
app.include_router(user_router)
app.include_router(message_router)
app.include_router(ws_router)
app.include_router(room_router)
app.include_router(auth_router)