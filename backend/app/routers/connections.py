import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session
from app.models import Song, Connection
from app.database import get_db
from app.schemas import ConnectionCreate, ConnectionResponse

router = APIRouter()

@router.get("/connections", response_model=list[ConnectionResponse])
def get_connections(db: Session = Depends(get_db)):
    connections = db.scalars(sqlalchemy.select(Connection)).all()
    return connections

@router.post("/connections", response_model=ConnectionResponse)
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