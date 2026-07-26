from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey, UniqueConstraint

from .base import Base

class UserSongConnection(Base):
    __tablename__ = "user_song_connections"

    id: Mapped[int] = mapped_column(primary_key=True)

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id")
        )
    
    connection_id: Mapped[int] = mapped_column(
        ForeignKey("connections.id")
        )

    user = relationship(
        "User",
        back_populates="user_song_connections"
    )

    connection = relationship(
        "Connection",
        back_populates="supporters"
    )

    __table_args__ = (
        UniqueConstraint("user_id", "connection_id"),
    )