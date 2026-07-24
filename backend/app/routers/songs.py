import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.models import Song, Connection
from app.database import get_db
from app.schemas import SongCreate, SongResponse, SongUpdate, ConnectionResponse

router = APIRouter()

@router.get("/", response_model=list[SongResponse])
def get_songs(db: Session = Depends(get_db)):
    songs = db.scalars(sqlalchemy.select(Song)).all()
    return songs

@router.get("/{song_id}", response_model=SongResponse)
def get_song(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(sqlalchemy.select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    return song

@router.get("/{song_id}/connections", response_model=list[ConnectionResponse])
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

@router.post("/", response_model=SongResponse)
def add_song(song: SongCreate, db: Session = Depends(get_db)):
    db_song = Song(title=song.title, artist=song.artist)
    db.add(db_song)
    db.commit()
    db.refresh(db_song)
    return db_song

@router.delete("/{song_id}", response_model=None)
def delete_song(song_id: int, db: Session = Depends(get_db)):
    song = db.scalar(sqlalchemy.select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    db.delete(song)
    db.commit()
    # return {"message": f"Successfully deleted song {song_id}"}
    return Response(status_code=status.HTTP_204_NO_CONTENT) 

@router.put("/{song_id}", response_model=SongResponse)
def update_song(song_id: int, song_update: SongUpdate, db: Session = Depends(get_db)):
    song = db.scalar(sqlalchemy.select(Song).where(Song.id == song_id))
    if not song:
        raise HTTPException(status_code=404, detail="Song not found")
    song.title = song_update.title
    song.artist = song_update.artist
    db.commit()
    db.refresh(song)
    return song