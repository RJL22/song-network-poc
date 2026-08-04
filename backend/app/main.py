from fastapi import FastAPI, Depends, HTTPException, Response, status
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.orm import Session

from app.models import Song, Connection, UserSongConnection
from app.database import get_db
from app.schemas import SongCreate, SongResponse, SongUpdate
from app.schemas import ConnectionCreate, ConnectionResponse
from app.routers import auth, songs, connections, song_search

from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def test():
    return {"message": "Hello World!"}

# Adding the routers for songs and connections
app.include_router(auth.router)
app.include_router(song_search.router)
app.include_router(songs.router)
app.include_router(connections.router)
