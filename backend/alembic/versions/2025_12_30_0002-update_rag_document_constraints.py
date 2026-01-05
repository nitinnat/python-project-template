"""Update RAG document uniqueness constraints

Revision ID: update_rag_document_constraints
Revises: add_rag_tables
Create Date: 2025-12-30 00:02:00.000000

"""
from alembic import op


# revision identifiers, used by Alembic.
revision = "update_rag_document_constraints"
down_revision = "add_rag_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_index(op.f("ix_rag_documents_file_hash"), table_name="rag_documents")
    op.create_index(
        op.f("ix_rag_documents_file_hash"),
        "rag_documents",
        ["file_hash"],
        unique=False,
    )
    op.create_unique_constraint(
        op.f("uq_rag_documents_file_name"),
        "rag_documents",
        ["file_name"],
    )


def downgrade() -> None:
    op.drop_constraint(
        op.f("uq_rag_documents_file_name"),
        "rag_documents",
        type_="unique",
    )
    op.drop_index(op.f("ix_rag_documents_file_hash"), table_name="rag_documents")
    op.create_index(
        op.f("ix_rag_documents_file_hash"),
        "rag_documents",
        ["file_hash"],
        unique=True,
    )
