from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import ForeignKey

class Base(DeclarativeBase):
    pass

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
        foreign_keys=[song_1_id]
    )

    song_2: Mapped["Song"] = relationship(
        back_populates="connections_as_song_2",
        foreign_keys=[song_2_id]
    )

class UserConnection(Base):
    __tablename__ = "user_connections"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    connection_id: Mapped[int] = mapped_column(primary_key=True)

