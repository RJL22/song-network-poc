from typing import TYPE_CHECKING

from sqlalchemy.orm import Mapped, mapped_column

from .base import Base

class UserConnection(Base):
    __tablename__ = "user_connections"

    user_id: Mapped[int] = mapped_column(primary_key=True)
    connection_id: Mapped[int] = mapped_column(primary_key=True)