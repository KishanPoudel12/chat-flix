from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from database import create_db
from websocket.demo import html
#routers import
from routers import user_router, ws_router,message_router,room_router
from auth import  auth_router
from fastapi.middleware.cors import  CORSMiddleware
app = FastAPI()



origins = [
    "http://localhost:3000",  # frontend URL
    "http://127.0.0.1:5173",  # frontend dev server
    "https://chat-flix-kishan.onrender.com",  # your hosted frontend
    "https://chat-flix-d92mas0cu-kishanpoudel563-8257s-projects.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] to allow all
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    return HTMLResponse(html)

@app.on_event("startup")
async def startup():
    import models
    # return create_db()
    print("The Db Migrations are now handled by albemic itself ")

#routers
app.include_router(user_router)
app.include_router(message_router)
app.include_router(ws_router)
app.include_router(room_router)
app.include_router(auth_router)