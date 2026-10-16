"""enforce one undirected connection per song pair"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "8d1c2c6b7f10"
down_revision: Union[str, Sequence[str], None] = "6b9b1800fb23"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Existing application code normalizes pairs before insertion. This
    # constraint protects that invariant against races and direct writes.
    op.create_unique_constraint(
        "uq_connections_song_pair", "connections", ["song_1_id", "song_2_id"]
    )


def downgrade() -> None:
    op.drop_constraint("uq_connections_song_pair", "connections", type_="unique")
