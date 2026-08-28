"""add subject dimension and passages tables

Revision ID: b58124cd38d2
Revises: 04f3dde95ee8
Create Date: 2026-08-22 12:50:39.530171

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b58124cd38d2'
down_revision: Union[str, Sequence[str], None] = '04f3dde95ee8'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column(
        "practice_sessions",
        sa.Column("subject", sa.String(), nullable=False, server_default="maths"),
    )

    op.add_column(
        "child_progress",
        sa.Column("subject", sa.String(), nullable=False, server_default="maths"),
    )
    op.drop_constraint("child_progress_pkey", "child_progress", type_="primary")
    op.create_primary_key(
        "child_progress_pkey", "child_progress", ["child_id", "subject", "topic", "track"]
    )

    op.create_table(
        "passages",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column("subject", sa.String(), nullable=False),
        sa.Column("title", sa.Text(), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=False),
        sa.Column("sentence_count", sa.Integer(), nullable=False),
        sa.Column("difficulty_rank", sa.Integer(), nullable=False),
        sa.Column("takeaway", sa.Text(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.CheckConstraint(
            "difficulty_rank >= 1 AND difficulty_rank <= 50",
            name="ck_passages_difficulty_rank_range",
        ),
    )
    op.create_index("ix_passages_difficulty_rank", "passages", ["difficulty_rank"])

    op.create_table(
        "comprehension_questions",
        sa.Column("id", sa.Uuid(), primary_key=True),
        sa.Column(
            "passage_id",
            sa.Uuid(),
            sa.ForeignKey("passages.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("question_type", sa.String(), nullable=False),
        sa.Column("question_text", sa.Text(), nullable=False),
        sa.Column("options", sa.JSON(), nullable=False),
        sa.Column("correct_answer", sa.Text(), nullable=False),
        sa.Column("explanation_hint", sa.Text(), nullable=False),
    )
    op.create_index(
        "ix_comprehension_questions_passage_id", "comprehension_questions", ["passage_id"]
    )


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(
        "ix_comprehension_questions_passage_id", table_name="comprehension_questions"
    )
    op.drop_table("comprehension_questions")
    op.drop_index("ix_passages_difficulty_rank", table_name="passages")
    op.drop_table("passages")

    op.drop_constraint("child_progress_pkey", "child_progress", type_="primary")
    op.drop_column("child_progress", "subject")
    op.create_primary_key(
        "child_progress_pkey", "child_progress", ["child_id", "topic", "track"]
    )

    op.drop_column("practice_sessions", "subject")
