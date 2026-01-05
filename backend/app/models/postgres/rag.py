from typing import Optional
from uuid import uuid4

from pgvector.sqlalchemy import Vector
from sqlalchemy import Boolean, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.postgres.base import Base, TimestampMixin


class RagDocument(Base, TimestampMixin):
    __tablename__ = "rag_documents"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    file_name: Mapped[str] = mapped_column(
        String(500), nullable=False, unique=True
    )
    file_path: Mapped[str] = mapped_column(String(2000), nullable=False)
    file_type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # pdf, docx, pptx, xlsx, txt, md
    file_size: Mapped[int] = mapped_column(Integer, nullable=False)
    file_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, index=True
    )  # SHA-256
    folder_path: Mapped[str] = mapped_column(
        String(2000), nullable=False, index=True
    )
    markdown_content: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[str] = mapped_column(
        String(50), default="pending", nullable=False
    )  # pending, processing, completed, failed
    error_message: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    # Relationships
    chunks: Mapped[list["RagChunk"]] = relationship(
        "RagChunk", back_populates="document", cascade="all, delete-orphan"
    )


class RagChunk(Base, TimestampMixin):
    __tablename__ = "rag_chunks"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    document_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_documents.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    token_count: Mapped[int] = mapped_column(Integer, nullable=False)
    embedding: Mapped[Optional[list[float]]] = mapped_column(
        Vector(768), nullable=True
    )  # nomic-embed-text dimension
    metadata_: Mapped[dict] = mapped_column(
        "metadata", JSONB, default=dict, nullable=False
    )

    # Relationships
    document: Mapped["RagDocument"] = relationship(
        "RagDocument", back_populates="chunks"
    )


class RagConversation(Base, TimestampMixin):
    __tablename__ = "rag_conversations"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    title: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    folder_path: Mapped[Optional[str]] = mapped_column(
        String(2000), nullable=True
    )  # Context folder for document retrieval
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # Relationships
    messages: Mapped[list["RagMessage"]] = relationship(
        "RagMessage",
        back_populates="conversation",
        cascade="all, delete-orphan",
        order_by="RagMessage.sequence",
    )


class RagMessage(Base, TimestampMixin):
    __tablename__ = "rag_messages"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True), primary_key=True, default=uuid4
    )
    conversation_id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("rag_conversations.id", ondelete="CASCADE"),
        nullable=False,
        index=True,
    )
    sequence: Mapped[int] = mapped_column(Integer, nullable=False)
    role: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # user, assistant, system
    content: Mapped[str] = mapped_column(Text, nullable=False)
    sources: Mapped[list] = mapped_column(
        JSONB, default=list, nullable=False
    )  # List of chunk IDs used
    token_count: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)

    # Relationships
    conversation: Mapped["RagConversation"] = relationship(
        "RagConversation", back_populates="messages"
    )
