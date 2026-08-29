"""add difficulty to practice sessions

Revision ID: f4ae0d5007ea
Revises: b58124cd38d2
Create Date: 2026-08-29 12:53:35.708772

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f4ae0d5007ea'
down_revision: Union[str, Sequence[str], None] = 'b58124cd38d2'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "practice_sessions",
        sa.Column("difficulty", sa.String(), nullable=True),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column("practice_sessions", "difficulty")
