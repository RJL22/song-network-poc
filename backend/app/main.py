from fastapi import FastAPI, Depends, HTTPException, Response, status
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.orm import Session

from app.models import Song, Connection, UserConnection
from app.database import get_db
from app.schemas import SongCreate, SongResponse, SongUpdate
from app.schemas import ConnectionCreate, ConnectionResponse
from app.routers import songs, connections, song_search

app = FastAPI()


@app.get("/")
def test():
    return {"message": "Hello World!"}

# Adding the routers for songs and connections
app.include_router(song_search.router)
app.include_router(songs.router)
app.include_router(connections.router)
