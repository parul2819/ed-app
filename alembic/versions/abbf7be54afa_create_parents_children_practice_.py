"""create parents children practice_sessions question_attempts child_progress

Revision ID: abbf7be54afa
Revises:
Create Date: 2026-08-09 20:44:38.347386

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abbf7be54afa'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    op.create_table(
        "parents",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("email", sa.Text(), nullable=False),
        sa.Column("password_hash", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.UniqueConstraint("email", name="uq_parents_email"),
    )
    op.create_index("ix_parents_email", "parents", ["email"])

    op.create_table(
        "children",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "parent_id",
            sa.Uuid(),
            sa.ForeignKey("parents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("name", sa.Text(), nullable=False),
        sa.Column("pin_hash", sa.Text(), nullable=False),
        sa.Column("grade", sa.Integer(), nullable=False, server_default="3"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index("ix_children_parent_id", "children", ["parent_id"])

    op.create_table(
        "practice_sessions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "child_id",
            sa.Uuid(),
            sa.ForeignKey("children.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("topic", sa.String(), nullable=False),
        sa.Column("track", sa.String(), nullable=False),
        sa.Column("mode", sa.String(), nullable=False),
        sa.Column(
            "started_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        "ix_practice_sessions_child_id_topic", "practice_sessions", ["child_id", "topic"]
    )
    op.create_index(
        "ix_practice_sessions_child_id_started_at",
        "practice_sessions",
        ["child_id", "started_at"],
    )

    op.create_table(
        "question_attempts",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "session_id",
            sa.Uuid(),
            sa.ForeignKey("practice_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_id", sa.Text(), nullable=False),
        sa.Column("selected_answer", sa.Text(), nullable=False),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column(
            "answered_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )
    op.create_index(
        "ix_question_attempts_session_id", "question_attempts", ["session_id"]
    )

    op.create_table(
        "child_progress",
        sa.Column(
            "child_id",
            sa.Uuid(),
            sa.ForeignKey("children.id", ondelete="CASCADE"),
            primary_key=True,
        ),
        sa.Column("topic", sa.String(), primary_key=True),
        sa.Column("track", sa.String(), primary_key=True),
        sa.Column(
            "questions_attempted", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column(
            "questions_correct", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("stars_earned", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_table("child_progress")
    op.drop_index("ix_question_attempts_session_id", table_name="question_attempts")
    op.drop_table("question_attempts")
    op.drop_index(
        "ix_practice_sessions_child_id_started_at", table_name="practice_sessions"
    )
    op.drop_index(
        "ix_practice_sessions_child_id_topic", table_name="practice_sessions"
    )
    op.drop_table("practice_sessions")
    op.drop_index("ix_children_parent_id", table_name="children")
    op.drop_table("children")
    op.drop_index("ix_parents_email", table_name="parents")
    op.drop_table("parents")
    op.execute("DROP EXTENSION IF EXISTS vector")
