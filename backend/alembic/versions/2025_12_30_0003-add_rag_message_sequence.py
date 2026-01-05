"""Add sequence column for ordered RAG messages

Revision ID: add_rag_message_sequence
Revises: update_rag_document_constraints
Create Date: 2025-12-30 00:03:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "add_rag_message_sequence"
down_revision = "update_rag_document_constraints"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "rag_messages",
        sa.Column("sequence", sa.Integer(), nullable=True),
    )
    op.execute(
        """
        WITH ranked AS (
            SELECT
                id,
                ROW_NUMBER() OVER (
                    PARTITION BY conversation_id
                    ORDER BY created_at, id
                ) AS seq
            FROM rag_messages
        )
        UPDATE rag_messages
        SET sequence = ranked.seq
        FROM ranked
        WHERE rag_messages.id = ranked.id
        """
    )
    op.alter_column("rag_messages", "sequence", nullable=False)
    op.create_unique_constraint(
        op.f("uq_rag_messages_conversation_id_sequence"),
        "rag_messages",
        ["conversation_id", "sequence"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("uq_rag_messages_conversation_id_sequence"),
        "rag_messages",
        type_="unique",
    )
    op.drop_column("rag_messages", "sequence")
