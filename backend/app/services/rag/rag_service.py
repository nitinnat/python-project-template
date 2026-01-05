import logging
from typing import AsyncGenerator, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.rag_repository import RagRepository
from app.schemas.rag import (
    ChatResponse,
    ChatSource,
    ConversationDetail,
    ConversationSummary,
    DocumentStatus,
    FileInfo,
    FolderContents,
)
from app.services.rag.chat_agent import RagChatAgent
from app.services.rag.embedding_service import EmbeddingService
from app.services.rag.ingestion_service import IngestionService

logger = logging.getLogger(__name__)


class RagService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.repository = RagRepository(session)
        self.embedding_service = EmbeddingService()
        self.ingestion_service = IngestionService(
            repository=self.repository,
            embedding_service=self.embedding_service,
        )
        self.chat_agent = RagChatAgent(
            repository=self.repository,
            embedding_service=self.embedding_service,
        )

    async def list_folder(self, folder_path: str) -> FolderContents:
        normalized_path = self.ingestion_service.normalize_folder_path(folder_path)
        files = self.ingestion_service.list_folder_files(normalized_path)
        return FolderContents(
            folder_path=normalized_path,
            files=[
                FileInfo(
                    name=f["name"],
                    path=f["path"],
                    type=f["type"],
                    size=f["size"],
                    modified_at=f["modified_at"],
                )
                for f in files
            ],
            total_count=len(files),
        )

    async def ingest_folder(
        self, folder_path: str
    ) -> AsyncGenerator[dict, None]:
        normalized_path = self.ingestion_service.normalize_folder_path(folder_path)
        async for progress in self.ingestion_service.ingest_folder(normalized_path):
            yield progress
            if progress.get("type") in ("progress", "complete"):
                await self.session.commit()

    async def get_document_status(
        self, folder_path: str
    ) -> list[DocumentStatus]:
        normalized_path = self.ingestion_service.normalize_folder_path(folder_path)
        statuses = await self.ingestion_service.get_document_status(normalized_path)
        return [
            DocumentStatus(
                id=s["id"],
                file_name=s["file_name"],
                status=s["status"],
                chunk_count=s["chunk_count"],
                error_message=s["error_message"],
                created_at=s["created_at"],
            )
            for s in statuses
        ]

    async def chat(
        self,
        message: str,
        conversation_id: Optional[UUID] = None,
        folder_path: Optional[str] = None,
    ) -> ChatResponse:
        if conversation_id:
            conversation = await self.repository.get_conversation_with_messages(
                conversation_id
            )
            if not conversation:
                raise LookupError(f"Conversation not found: {conversation_id}")
        else:
            normalized_path = self.ingestion_service.normalize_folder_path(folder_path)
            conversation = await self.repository.create_conversation(
                folder_path=normalized_path
            )

        normalized_path = self.ingestion_service.normalize_folder_path(
            folder_path or conversation.folder_path
        )
        if conversation.folder_path and conversation.folder_path != normalized_path:
            raise ValueError(
                "Conversation folder does not match the configured documents root"
            )
        if not conversation.folder_path:
            conversation.folder_path = normalized_path
            await self.session.flush()

        history = []
        if conversation_id and conversation.messages:
            for msg in conversation.messages:
                history.append({
                    "role": msg.role,
                    "content": msg.content,
                })

        result = await self.chat_agent.chat(
            query=message,
            conversation_history=history,
            folder_path=normalized_path,
        )

        await self.repository.add_message(
            conversation_id=conversation.id,
            role="user",
            content=message,
        )

        source_ids = [s["chunk_id"] for s in result["sources"]]
        await self.repository.add_message(
            conversation_id=conversation.id,
            role="assistant",
            content=result["message"],
            sources=source_ids,
        )

        await self.session.commit()

        if not conversation.title and len(history) == 0:
            title = message[:50] + ("..." if len(message) > 50 else "")
            await self.repository.update_conversation_title(
                conversation.id, title
            )
            await self.session.commit()

        return ChatResponse(
            conversation_id=conversation.id,
            message=result["message"],
            sources=[
                ChatSource(
                    document_name=s["document_name"],
                    chunk_content=s["chunk_content"],
                    relevance_score=s["relevance_score"],
                )
                for s in result["sources"]
            ],
        )

    async def list_conversations(
        self, limit: int = 20
    ) -> list[ConversationSummary]:
        conversations = await self.repository.list_conversations(limit=limit)
        return [
            ConversationSummary(
                id=c.id,
                title=c.title,
                folder_path=c.folder_path,
                created_at=c.created_at,
                message_count=len(c.messages),
            )
            for c in conversations
        ]

    async def get_conversation(
        self, conversation_id: UUID
    ) -> ConversationDetail:
        conversation = await self.repository.get_conversation_with_messages(
            conversation_id
        )
        if not conversation:
            raise ValueError(f"Conversation not found: {conversation_id}")

        return ConversationDetail(
            id=conversation.id,
            title=conversation.title,
            folder_path=conversation.folder_path,
            messages=[
                {"role": m.role, "content": m.content}
                for m in conversation.messages
            ],
            created_at=conversation.created_at,
        )

    async def delete_conversation(self, conversation_id: UUID) -> bool:
        result = await self.repository.delete_conversation(conversation_id)
        await self.session.commit()
        return result
