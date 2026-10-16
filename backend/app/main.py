from fastapi import FastAPI
from fastapi.responses import JSONResponse

from app.routers import auth, songs, connections, song_search
from app.core.exceptions import SelfConnectionError
from app.services.musicbrainz.client import close_client

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
    allow_credentials=True,
)


@app.get("/")
def test():
    return {"message": "Hello World!"}

@app.exception_handler(SelfConnectionError)
async def handle_self_connection(request, exc):
    return JSONResponse(status_code=400, content={"detail": str(exc)})

# Adding the routers for songs and connections
app.include_router(auth.router)
app.include_router(song_search.router)
app.include_router(songs.router)
app.include_router(connections.router)

@app.on_event("shutdown")
async def shutdown_external_clients():
    await close_client()
