import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.models import Song, Connection, User
from app.database import get_db
from app.schemas import SongCreate, SongResponse, SongUpdate, SongRecommendationResponse
from app.dependencies.auth import get_current_user

router = APIRouter(prefix="/songs", tags=["songs"])

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

@router.get("/{song_id}/connections", response_model=list[SongRecommendationResponse])
def get_song_connections(song_id: int, db: Session = Depends(get_db)):
    song = db.get(Song, song_id)
    if song is None:
        raise HTTPException(status_code=404, detail="Song not found")
    adjacent_songs = []

    for connection in song.connections:
        adj_song_id = connection.song_1_id if connection.song_2_id == song_id else connection.song_2_id
        adjacent_songs.append((connection, db.get(Song, adj_song_id), len(connection.supporters)))

    adjacent_songs.sort(key=lambda item: (-item[2], item[1].title.lower(), item[0].id))
    
    return [
        SongRecommendationResponse(
            id=song.id, mb_id=song.mb_id, title=song.title, artist=song.artist,
            connection_id=connection.id, supporter_count=count,
        )
        for connection, song, count in adjacent_songs
    ]

@router.post("/", response_model=SongResponse)
def add_song(song: SongCreate, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    #Searching for song to see if it already exists (returns song if it does)
    existing = db.scalars(sqlalchemy.select(Song).where(Song.mb_id == song.mb_id)).first()
    if existing:
        return existing

    db_song = Song(mb_id=song.mb_id, title=song.title, artist=song.artist)
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
