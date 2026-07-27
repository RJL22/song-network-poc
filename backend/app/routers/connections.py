import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session

from app.models import Song, Connection, User
from app.database import get_db
from app.schemas import ConnectionCreate, ConnectionResponse
from app.dependencies.auth import get_current_user
from app.crud.connection import create_connection_service

router = APIRouter(prefix="/connections", tags=["connections"])

@router.get("/", response_model=list[ConnectionResponse])
def get_connections(db: Session = Depends(get_db)):
    connections = db.scalars(sqlalchemy.select(Connection)).all()
    return connections

@router.post("/", response_model=ConnectionResponse)
def add_connection(connection: ConnectionCreate, 
                   current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    try:
        return create_connection_service(
            db,
            user_id=current_user.id,
            song_1_id=connection.song_1_id,
            song_2_id=connection.song_2_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))