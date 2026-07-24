from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .connection import Connection


class Song(Base):
    __tablename__ = "songs"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(nullable=False)
    artist: Mapped[str] = mapped_column(nullable=False)

    connections_as_song_1: Mapped[list["Connection"]] = relationship(
        back_populates="song_1",
        foreign_keys="Connection.song_1_id",
    )

    connections_as_song_2: Mapped[list["Connection"]] = relationship(
        back_populates="song_2",
        foreign_keys="Connection.song_2_id",
    )