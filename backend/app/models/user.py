from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .connection import Connection
    from .user_song_connection import UserSongConnection

class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(unique=True, nullable=False)

    user_song_connections: Mapped[list["UserSongConnection"]] = relationship(
        "UserSongConnection",
        back_populates="user"
    )