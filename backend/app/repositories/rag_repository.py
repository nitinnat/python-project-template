import logging
import math
from typing import Optional
from uuid import UUID

from sqlalchemy import func, select, text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.postgres.rag import (
    RagChunk,
    RagConversation,
    RagDocument,
    RagMessage,
)

logger = logging.getLogger(__name__)


class RagRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_document(
        self,
        file_name: str,
        file_path: str,
        file_type: str,
        file_size: int,
        file_hash: str,
        folder_path: str,
        markdown_content: Optional[str] = None,
        status: str = "pending",
        metadata: Optional[dict] = None,
    ) -> RagDocument:
        document = RagDocument(
            file_name=file_name,
            file_path=file_path,
            file_type=file_type,
            file_size=file_size,
            file_hash=file_hash,
            folder_path=folder_path,
            markdown_content=markdown_content,
            status=status,
            metadata_=metadata or {},
        )
        self.session.add(document)
        await self.session.flush()
        await self.session.refresh(document)
        return document

    async def get_document_by_id(self, doc_id: UUID) -> Optional[RagDocument]:
        result = await self.session.execute(
            select(RagDocument).where(RagDocument.id == doc_id)
        )
        return result.scalar_one_or_none()

    async def get_document_by_hash(self, file_hash: str) -> Optional[RagDocument]:
        result = await self.session.execute(
            select(RagDocument).where(RagDocument.file_hash == file_hash)
        )
        return result.scalar_one_or_none()

    async def get_document_by_name(self, file_name: str) -> Optional[RagDocument]:
        result = await self.session.execute(
            select(RagDocument).where(RagDocument.file_name == file_name)
        )
        return result.scalar_one_or_none()

    async def get_documents_by_folder(
        self, folder_path: str, status: Optional[str] = None
    ) -> list[RagDocument]:
        query = select(RagDocument).where(RagDocument.folder_path == folder_path)
        if status:
            query = query.where(RagDocument.status == status)
        query = query.order_by(RagDocument.file_name)
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_document_status(
        self,
        doc_id: UUID,
        status: str,
        error_message: Optional[str] = None,
    ) -> None:
        document = await self.get_document_by_id(doc_id)
        if document:
            document.status = status
            document.error_message = error_message
            await self.session.flush()

    async def update_document_content(
        self, doc_id: UUID, markdown_content: str
    ) -> None:
        document = await self.get_document_by_id(doc_id)
        if document:
            document.markdown_content = markdown_content
            await self.session.flush()

    async def delete_document(self, doc_id: UUID) -> bool:
        document = await self.get_document_by_id(doc_id)
        if document:
            await self.session.delete(document)
            await self.session.flush()
            return True
        return False

    async def create_chunk(
        self,
        document_id: UUID,
        chunk_index: int,
        content: str,
        token_count: int,
        embedding: Optional[list[float]] = None,
        metadata: Optional[dict] = None,
    ) -> RagChunk:
        chunk = RagChunk(
            document_id=document_id,
            chunk_index=chunk_index,
            content=content,
            token_count=token_count,
            embedding=embedding,
            metadata_=metadata or {},
        )
        self.session.add(chunk)
        await self.session.flush()
        return chunk

    async def create_chunks_batch(
        self,
        chunks_data: list[dict],
    ) -> list[RagChunk]:
        chunks = [
            RagChunk(
                document_id=data["document_id"],
                chunk_index=data["chunk_index"],
                content=data["content"],
                token_count=data["token_count"],
                embedding=data.get("embedding"),
                metadata_=data.get("metadata", {}),
            )
            for data in chunks_data
        ]
        self.session.add_all(chunks)
        await self.session.flush()
        return chunks

    async def get_chunks_by_document(self, document_id: UUID) -> list[RagChunk]:
        result = await self.session.execute(
            select(RagChunk)
            .where(RagChunk.document_id == document_id)
            .order_by(RagChunk.chunk_index)
        )
        return list(result.scalars().all())

    async def vector_search(
        self,
        embedding: list[float],
        folder_path: Optional[str] = None,
        limit: int = 5,
        similarity_threshold: float = 0.0,
    ) -> list[dict]:
        embedding_str = "[" + ",".join(str(x) for x in embedding) + "]"

        conn = await self.session.connection()
        raw_conn = await conn.get_raw_connection()
        driver_conn = raw_conn.driver_connection

        if folder_path:
            query_str = """
                SELECT
                    c.id,
                    c.content,
                    c.chunk_index,
                    c.token_count,
                    c.metadata,
                    d.id as document_id,
                    d.file_name,
                    d.file_path,
                    1 - (c.embedding <=> $1::vector) as similarity
                FROM rag_chunks c
                JOIN rag_documents d ON c.document_id = d.id
                WHERE d.status = 'completed'
                  AND c.embedding IS NOT NULL
                  AND d.folder_path = $2
                  AND (1 - (c.embedding <=> $1::vector)) >= $3
                ORDER BY c.embedding <=> $1::vector
                LIMIT $4
            """
            rows = await driver_conn.fetch(
                query_str,
                embedding_str, folder_path, similarity_threshold, limit
            )
        else:
            query_str = """
                SELECT
                    c.id,
                    c.content,
                    c.chunk_index,
                    c.token_count,
                    c.metadata,
                    d.id as document_id,
                    d.file_name,
                    d.file_path,
                    1 - (c.embedding <=> $1::vector) as similarity
                FROM rag_chunks c
                JOIN rag_documents d ON c.document_id = d.id
                WHERE d.status = 'completed'
                  AND c.embedding IS NOT NULL
                  AND (1 - (c.embedding <=> $1::vector)) >= $2
                ORDER BY c.embedding <=> $1::vector
                LIMIT $3
            """
            rows = await driver_conn.fetch(
                query_str,
                embedding_str, similarity_threshold, limit
            )

        results = []
        for row in rows:
            similarity = float(row["similarity"])
            if math.isnan(similarity):
                logger.warning(f"[VECTOR_SEARCH] Skipping chunk with NaN similarity")
                continue
            results.append({
                "id": str(row["id"]),
                "content": row["content"],
                "chunk_index": row["chunk_index"],
                "token_count": row["token_count"],
                "metadata": row["metadata"],
                "document_id": str(row["document_id"]),
                "file_name": row["file_name"],
                "file_path": row["file_path"],
                "similarity": similarity,
            })

        logger.info(f"[VECTOR_SEARCH] Found {len(results)} relevant chunks")
        return results

    # ========================================================================
    # Conversation Operations
    # ========================================================================

    async def create_conversation(
        self,
        title: Optional[str] = None,
        folder_path: Optional[str] = None,
    ) -> RagConversation:
        conversation = RagConversation(
            title=title,
            folder_path=folder_path,
        )
        self.session.add(conversation)
        await self.session.flush()
        await self.session.refresh(conversation)
        return conversation

    async def get_conversation_by_id(
        self, conv_id: UUID
    ) -> Optional[RagConversation]:
        result = await self.session.execute(
            select(RagConversation).where(RagConversation.id == conv_id)
        )
        return result.scalar_one_or_none()

    async def get_conversation_with_messages(
        self, conv_id: UUID
    ) -> Optional[RagConversation]:
        result = await self.session.execute(
            select(RagConversation)
            .options(selectinload(RagConversation.messages))
            .where(RagConversation.id == conv_id)
        )
        return result.scalar_one_or_none()

    async def list_conversations(
        self, limit: int = 20, offset: int = 0
    ) -> list[RagConversation]:
        result = await self.session.execute(
            select(RagConversation)
            .options(selectinload(RagConversation.messages))
            .where(RagConversation.is_active == True)  # noqa: E712
            .order_by(RagConversation.created_at.desc())
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update_conversation_title(
        self, conv_id: UUID, title: str
    ) -> None:
        conversation = await self.get_conversation_by_id(conv_id)
        if conversation:
            conversation.title = title
            await self.session.flush()

    async def delete_conversation(self, conv_id: UUID) -> bool:
        conversation = await self.get_conversation_by_id(conv_id)
        if conversation:
            conversation.is_active = False
            await self.session.flush()
            return True
        return False

    # ========================================================================
    # Message Operations
    # ========================================================================

    async def add_message(
        self,
        conversation_id: UUID,
        role: str,
        content: str,
        sources: Optional[list] = None,
        token_count: Optional[int] = None,
    ) -> RagMessage:
        result = await self.session.execute(
            select(func.coalesce(func.max(RagMessage.sequence), 0) + 1).where(
                RagMessage.conversation_id == conversation_id
            )
        )
        next_sequence = result.scalar_one()

        message = RagMessage(
            conversation_id=conversation_id,
            sequence=next_sequence,
            role=role,
            content=content,
            sources=sources or [],
            token_count=token_count,
        )
        self.session.add(message)
        await self.session.flush()
        await self.session.refresh(message)
        return message

    async def get_messages_by_conversation(
        self, conversation_id: UUID
    ) -> list[RagMessage]:
        result = await self.session.execute(
            select(RagMessage)
            .where(RagMessage.conversation_id == conversation_id)
            .order_by(RagMessage.sequence)
        )
        return list(result.scalars().all())

    # ========================================================================
    # Statistics
    # ========================================================================

    async def get_document_count_by_folder(self, folder_path: str) -> int:
        result = await self.session.execute(
            select(func.count(RagDocument.id)).where(
                RagDocument.folder_path == folder_path
            )
        )
        return result.scalar() or 0

    async def get_chunk_count_by_document(self, document_id: UUID) -> int:
        result = await self.session.execute(
            select(func.count(RagChunk.id)).where(
                RagChunk.document_id == document_id
            )
        )
        return result.scalar() or 0
