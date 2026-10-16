import sqlalchemy
from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy.orm import Session, joinedload

from app.models import Song, Connection, User, UserSongConnection
from app.database import get_db
from app.schemas import ConnectionCreate, ConnectionResponse, SupporterResponse, ConnectionHistoryResponse
from app.dependencies.auth import get_current_user
from app.crud.connection import create_connection_service
from app.crud.points import get_ranked_supporters

router = APIRouter(prefix="/connections", tags=["connections"])

@router.get("/", response_model=list[ConnectionResponse])
def get_connections(db: Session = Depends(get_db)):
    connections = db.scalars(sqlalchemy.select(Connection)).all()
    
    return [ConnectionResponse(id=c.id, song_1_id=c.song_1_id, song_2_id=c.song_2_id, supporter_count=len(c.supporters)) for c in connections]

@router.get("/{connection_id}/supporters", response_model=list[SupporterResponse])
def get_connection_supporters(connection_id: int, db: Session = Depends(get_db)):
    #Checking if connection is valid
    connection = db.scalar(sqlalchemy.select(Connection).where(Connection.id == connection_id))
    if not connection:
        raise HTTPException(status_code=404, detail="Connection not found")

    supporters = get_ranked_supporters(db, connection_id)

    return [
        {
            "user_id": s.user_id,
            "username": s.user.username,
            "rank": rank,
            "points": s.points,
        }
        for rank, s in enumerate(supporters, start=1)
    ]


@router.get("/mine", response_model=list[ConnectionHistoryResponse])
def get_my_connections(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    rows = db.scalars(
        sqlalchemy.select(UserSongConnection)
        .where(UserSongConnection.user_id == current_user.id)
        .order_by(UserSongConnection.created_at.desc())
        .options(joinedload(UserSongConnection.connection))
    ).all()
    return [
        ConnectionHistoryResponse(
            connection_id=row.connection.id,
            song_1_id=row.connection.song_1_id,
            song_2_id=row.connection.song_2_id,
            created_at=row.created_at.isoformat(),
            points=row.points,
            supporter_count=len(row.connection.supporters),
        ) for row in rows
    ]

@router.post("/", response_model=ConnectionResponse)
def add_connection(connection: ConnectionCreate, 
                   current_user: User = Depends(get_current_user),
                   db: Session = Depends(get_db)):
    try:
        created = create_connection_service(
            db,
            user_id=current_user.id,
            song_1_id=connection.song_1_id,
            song_2_id=connection.song_2_id,
        )
        return ConnectionResponse(
            id=created.id,
            song_1_id=created.song_1_id,
            song_2_id=created.song_2_id,
            supporter_count=len(created.supporters),
        )
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
