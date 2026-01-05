"""Add RAG tables for document ingestion and chat

Revision ID: add_rag_tables
Revises: e33669fc7a6c
Create Date: 2025-12-29 00:01:00.000000

"""
from alembic import op
import sqlalchemy as sa
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_rag_tables'
down_revision = 'e33669fc7a6c'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Enable pgvector extension
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    # Create rag_documents table
    op.create_table(
        'rag_documents',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('file_name', sa.String(length=500), nullable=False),
        sa.Column('file_path', sa.String(length=2000), nullable=False),
        sa.Column('file_type', sa.String(length=50), nullable=False),
        sa.Column('file_size', sa.Integer(), nullable=False),
        sa.Column('file_hash', sa.String(length=64), nullable=False),
        sa.Column('folder_path', sa.String(length=2000), nullable=False),
        sa.Column('markdown_content', sa.Text(), nullable=True),
        sa.Column('status', sa.String(length=50), server_default='pending', nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_rag_documents'))
    )
    op.create_index(op.f('ix_rag_documents_file_hash'), 'rag_documents', ['file_hash'], unique=True)
    op.create_index(op.f('ix_rag_documents_folder_path'), 'rag_documents', ['folder_path'], unique=False)

    # Create rag_chunks table
    op.create_table(
        'rag_chunks',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('document_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('chunk_index', sa.Integer(), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=False),
        sa.Column('embedding', Vector(768), nullable=True),
        sa.Column('metadata', postgresql.JSONB(astext_type=sa.Text()), server_default='{}', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ['document_id'],
            ['rag_documents.id'],
            name=op.f('fk_rag_chunks_document_id_rag_documents'),
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_rag_chunks'))
    )
    op.create_index(op.f('ix_rag_chunks_document_id'), 'rag_chunks', ['document_id'], unique=False)

    # Create HNSW index for fast vector similarity search
    op.execute("""
        CREATE INDEX ix_rag_chunks_embedding_hnsw
        ON rag_chunks
        USING hnsw (embedding vector_cosine_ops)
    """)

    # Create rag_conversations table
    op.create_table(
        'rag_conversations',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('title', sa.String(length=500), nullable=True),
        sa.Column('folder_path', sa.String(length=2000), nullable=True),
        sa.Column('is_active', sa.Boolean(), server_default='true', nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_rag_conversations'))
    )

    # Create rag_messages table
    op.create_table(
        'rag_messages',
        sa.Column('id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('conversation_id', postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column('role', sa.String(length=20), nullable=False),
        sa.Column('content', sa.Text(), nullable=False),
        sa.Column('sources', postgresql.JSONB(astext_type=sa.Text()), server_default='[]', nullable=False),
        sa.Column('token_count', sa.Integer(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(
            ['conversation_id'],
            ['rag_conversations.id'],
            name=op.f('fk_rag_messages_conversation_id_rag_conversations'),
            ondelete='CASCADE'
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_rag_messages'))
    )
    op.create_index(op.f('ix_rag_messages_conversation_id'), 'rag_messages', ['conversation_id'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_rag_messages_conversation_id'), table_name='rag_messages')
    op.drop_table('rag_messages')

    op.drop_table('rag_conversations')

    op.execute("DROP INDEX IF EXISTS ix_rag_chunks_embedding_hnsw")
    op.drop_index(op.f('ix_rag_chunks_document_id'), table_name='rag_chunks')
    op.drop_table('rag_chunks')

    op.drop_index(op.f('ix_rag_documents_folder_path'), table_name='rag_documents')
    op.drop_index(op.f('ix_rag_documents_file_hash'), table_name='rag_documents')
    op.drop_table('rag_documents')

    # Note: We don't drop the vector extension as other tables might use it
