"""create password_reset_tokens

Revision ID: 04f3dde95ee8
Revises: abbf7be54afa
Create Date: 2026-08-14 18:21:24.949091

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '04f3dde95ee8'
down_revision: Union[str, Sequence[str], None] = 'abbf7be54afa'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "password_reset_tokens",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "parent_id",
            sa.Uuid(),
            sa.ForeignKey("parents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("token_hash", sa.Text(), nullable=False),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used", sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("token_hash", name="uq_password_reset_tokens_token_hash"),
    )
    op.create_index(
        "ix_password_reset_tokens_parent_id", "password_reset_tokens", ["parent_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_password_reset_tokens_parent_id", table_name="password_reset_tokens"
    )
    op.drop_table("password_reset_tokens")
