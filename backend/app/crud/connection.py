from sqlalchemy.orm import Session
from app.models import Song, Connection, UserSongConnection
from app.crud.points import recompute_points_for_connection

def create_connection_service(
    db: Session,
    user_id: int,
    song_1_id: int,
    song_2_id: int,
) -> Connection:
    if song_1_id == song_2_id:
        raise ValueError("Cannot connect a song to itself")

    s1, s2 = min(song_1_id, song_2_id), max(song_1_id, song_2_id)

    #Verifying that provided ids were legitimate
    song_1, song_2 = db.get(Song, s1), db.get(Song, s2)
    if song_1 is None or song_2 is None:
        raise ValueError("One or both songs do not exist")

    #Checking if the connection already exists
    connection = db.query(Connection).filter(
        Connection.song_1_id == s1, Connection.song_2_id == s2
    ).first()
    if connection is None:
        connection = Connection(song_1_id=s1, song_2_id=s2)
        db.add(connection)
        db.flush()

    #Checking if the user already made the connection
    already_supported = db.query(UserSongConnection).filter(
        UserSongConnection.user_id == user_id,
        UserSongConnection.connection_id == connection.id,
    ).first()

    if already_supported is None:
        support = UserSongConnection(user_id=user_id, connection_id=connection.id)
        db.add(support)
        db.flush()
        recompute_points_for_connection(db, connection.id)


    db.commit()
    db.refresh(connection)
    return connection
    
