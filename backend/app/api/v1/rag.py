import json
import logging
from typing import Optional
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_db
from app.schemas.rag import (
    ChatRequest,
    ChatResponse,
    ConversationDetail,
    ConversationSummary,
    DocumentIngestRequest,
    DocumentStatus,
    FolderContents,
)
from app.services.rag.rag_service import RagService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/rag", tags=["rag"])


def get_rag_service(session: AsyncSession = Depends(get_db)) -> RagService:
    return RagService(session)


@router.get("/documents/folder", response_model=FolderContents)
async def list_folder_documents(
    folder_path: str = Query(..., description="Path to the folder"),
    rag_service: RagService = Depends(get_rag_service),
) -> FolderContents:
    try:
        return await rag_service.list_folder(folder_path)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/documents/ingest")
async def ingest_folder_documents(
    request: DocumentIngestRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> StreamingResponse:
    async def event_generator():
        try:
            async for progress in rag_service.ingest_folder(request.folder_path):
                yield f"data: {json.dumps(progress)}\n\n"
        except ValueError as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        except Exception as e:
            logger.error(f"Ingestion error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Internal error during ingestion'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.get("/documents/status", response_model=list[DocumentStatus])
async def get_document_status(
    folder_path: str = Query(..., description="Path to the folder"),
    rag_service: RagService = Depends(get_rag_service),
) -> list[DocumentStatus]:
    try:
        return await rag_service.get_document_status(folder_path)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/chat", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> ChatResponse:
    try:
        return await rag_service.chat(
            message=request.message,
            conversation_id=request.conversation_id,
            folder_path=request.folder_path,
        )
    except LookupError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.post("/chat/stream")
async def chat_stream(
    request: ChatRequest,
    rag_service: RagService = Depends(get_rag_service),
) -> StreamingResponse:
    async def event_generator():
        try:
            response = await rag_service.chat(
                message=request.message,
                conversation_id=request.conversation_id,
                folder_path=request.folder_path,
            )

            sources_data = [
                {
                    "document_name": s.document_name,
                    "chunk_content": s.chunk_content,
                    "relevance_score": s.relevance_score,
                }
                for s in response.sources
            ]
            yield f"data: {json.dumps({'type': 'sources', 'sources': sources_data})}\n\n"
            yield f"data: {json.dumps({'type': 'message', 'content': response.message})}\n\n"
            yield f"data: {json.dumps({'type': 'done', 'conversation_id': str(response.conversation_id)})}\n\n"

        except LookupError as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        except ValueError as e:
            yield f"data: {json.dumps({'type': 'error', 'error': str(e)})}\n\n"
        except Exception as e:
            logger.error(f"Chat stream error: {e}")
            yield f"data: {json.dumps({'type': 'error', 'error': 'Internal error during chat'})}\n\n"

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


# ============================================================================
# Conversations
# ============================================================================


@router.get("/conversations", response_model=list[ConversationSummary])
async def list_conversations(
    limit: int = Query(20, ge=1, le=100, description="Max conversations to return"),
    rag_service: RagService = Depends(get_rag_service),
) -> list[ConversationSummary]:
    """
    List recent conversations.

    Returns conversation summaries ordered by creation date (newest first).
    """
    return await rag_service.list_conversations(limit=limit)


@router.get("/conversations/{conversation_id}", response_model=ConversationDetail)
async def get_conversation(
    conversation_id: UUID,
    rag_service: RagService = Depends(get_rag_service),
) -> ConversationDetail:
    """
    Get a conversation with all its messages.
    """
    try:
        return await rag_service.get_conversation(conversation_id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )


@router.delete("/conversations/{conversation_id}")
async def delete_conversation(
    conversation_id: UUID,
    rag_service: RagService = Depends(get_rag_service),
) -> dict:
    """
    Delete a conversation (soft delete).

    Returns success status.
    """
    result = await rag_service.delete_conversation(conversation_id)
    if not result:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Conversation not found: {conversation_id}",
        )
    return {"success": True, "message": "Conversation deleted"}
