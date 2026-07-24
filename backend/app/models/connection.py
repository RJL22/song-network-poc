from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base import Base

if TYPE_CHECKING:
    from .song import Song


class Connection(Base):
    __tablename__ = "connections"

    id: Mapped[int] = mapped_column(primary_key=True)

    song_1_id: Mapped[int] = mapped_column(
        ForeignKey("songs.id"),
        nullable=False,
    )

    song_2_id: Mapped[int] = mapped_column(
        ForeignKey("songs.id"),
        nullable=False,
    )

    song_1: Mapped["Song"] = relationship(
        back_populates="connections_as_song_1",
        foreign_keys=[song_1_id],
    )

    song_2: Mapped["Song"] = relationship(
        back_populates="connections_as_song_2",
        foreign_keys=[song_2_id],
    )