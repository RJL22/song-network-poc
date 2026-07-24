from fastapi import FastAPI, Depends, HTTPException, Response, status
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.orm import Session

from app.models import Song, Connection, UserConnection
from app.database import get_db
from app.schemas import SongCreate, SongResponse, SongUpdate
from app.schemas import ConnectionCreate, ConnectionResponse

app = FastAPI()

class Link(BaseModel):
    song1: str
    song2: str


@app.get("/")
def test():
    return {"message": "Hello World!"}


@app.get("/songs", response_model=list[SongResponse])
def get_songs(db: Session = Depends(get_db)):
    songs = db.scalars(sqlalchemy.select(Song)).all()
    return songs

@app.get("/songs/{song_id}", response_model=SongResponse)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(sqlalchemy.select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@app.get("/songs/{song_id}/connections", response_model=list[ConnectionResponse])
def get_song_connections(song_id: int, db: Session = Depends(get_db)):
    song = db.get(Song, song_id)
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    connections = db.scalars(
        sqlalchemy.select(Connection).where(
            (Connection.song_1_id == song_id) | (Connection.song_2_id == song_id)
        )
    ).all()
    return connections

@app.post("/songs", response_model=SongResponse)
def add_song(song: SongCreate, db: Session = Depends(get_db)):
    db_song = Song(title=song.title, artist=song.artist)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

@app.delete("/songs/{song_id}", response_model=None)
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(sqlalchemy.select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)
    db.commit()
    # return {"message": f"Successfully deleted song {song_id}"}
    return Response(status_code=status.HTTP_204_NO_CONTENT) 

@app.put("/songs/{song_id}", response_model=SongResponse)
def update_song(song_id: int, song_update: SongUpdate, db: Session = Depends(get_db)):
    song = db.scalar(sqlalchemy.select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    song.title = song_update.title
    song.artist = song_update.artist
    db.commit()
    db.refresh(song)
    return song


@app.get("/connections", response_model=list[ConnectionResponse])
def get_connections(db: Session = Depends(get_db)):
    connections = db.scalars(sqlalchemy.select(Connection)).all()
    return connections

@app.post("/connections", response_model=ConnectionResponse)
def add_connection(connection: ConnectionCreate, db: Session = Depends(get_db)):
    # Proper ordering of song IDs to avoid duplicates
    song_1_id = min(connection.song_1_id, connection.song_2_id)
    song_2_id = max(connection.song_1_id, connection.song_2_id)

    song1 = db.get(Song, song_1_id)
    song2 = db.get(Song, song_2_id)
    if not song1 or not song2:
        raise HTTPException(status_code=404, detail="One or both songs not found")

    if song_1_id == song_2_id:
        raise HTTPException(status_code=400, detail="Cannot create a connection between the same song")
    


    db_connection = Connection(song_1_id=song_1_id, song_2_id=song_2_id)
    db.add(db_connection)
    try:
        db.commit()
    except sqlalchemy.exc.IntegrityError:
        db.rollback()
        raise HTTPException(status_code=409, detail="Connection already exists")
    db.refresh(db_connection)

    return db_connection

