from sqlalchemy import select, func
from sqlalchemy.orm import Session
from app.models import UserSongConnection

import math

#Upper bound on number of users that get points from one connection
WINDOW = 20


def recompute_points_for_connection(db: Session, connection_id: int) -> None:
    total_supporters = db.scalar(
        select(func.count())
        .select_from(UserSongConnection)
        .where(UserSongConnection.connection_id == connection_id)
    )

    earliest_supporters = db.scalars(
        select(UserSongConnection)
        .where(UserSongConnection.connection_id == connection_id)
        .order_by(UserSongConnection.created_at.asc())
        .limit(WINDOW)
    ).all()

    for rank, supporter in enumerate(earliest_supporters, start=1):
        supporter.points = math.log(total_supporters / rank)