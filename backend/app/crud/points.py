from sqlalchemy import select, func
from sqlalchemy.orm import Session, joinedload
from app.models import UserSongConnection

import math

#Upper bound on number of users that get points from one connection
WINDOW = 20

def get_ranked_supporters(db: Session, connection_id: int) -> list[UserSongConnection]:
    return db.scalars(
        select(UserSongConnection)
        .where(UserSongConnection.connection_id == connection_id)
        .order_by(UserSongConnection.created_at.asc())
        .limit(WINDOW)
        .options(joinedload(UserSongConnection.user))
    ).all()


def recompute_points_for_connection(db: Session, connection_id: int) -> None:
    total_supporters = db.scalar(
        select(func.count())
        .select_from(UserSongConnection)
        .where(UserSongConnection.connection_id == connection_id)
    )

    earliest_supporters = get_ranked_supporters(db, connection_id)

    for rank, supporter in enumerate(earliest_supporters, start=1):
        supporter.points = math.log(total_supporters / rank)