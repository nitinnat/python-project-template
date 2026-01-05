from datetime import datetime
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FileInfo(BaseModel):
    name: str = Field(..., description="File name")
    path: str = Field(..., description="Full file path")
    type: str = Field(..., description="File type (pdf, docx, pptx, xlsx, txt, md)")
    size: int = Field(..., description="File size in bytes")
    modified_at: datetime = Field(..., description="Last modification time")


class FolderContents(BaseModel):
    folder_path: str = Field(..., description="Path to the folder")
    files: list[FileInfo] = Field(default_factory=list, description="List of files")
    total_count: int = Field(..., description="Total number of files")


class DocumentIngestRequest(BaseModel):
    folder_path: str = Field(..., description="Path to folder containing documents")


class DocumentStatus(BaseModel):
    id: UUID = Field(..., description="Document ID")
    file_name: str = Field(..., description="File name")
    status: str = Field(
        ..., description="Ingestion status (pending, processing, completed, failed)"
    )
    chunk_count: int = Field(default=0, description="Number of chunks created")
    error_message: Optional[str] = Field(
        None, description="Error message if status is failed"
    )
    created_at: datetime = Field(..., description="When document was ingested")


class IngestProgress(BaseModel):
    type: str = Field(
        ..., description="Event type (progress, error, complete)"
    )
    total: int = Field(default=0, description="Total files to process")
    processed: int = Field(default=0, description="Files processed so far")
    current_file: Optional[str] = Field(None, description="Currently processing file")
    status: str = Field(
        default="running", description="Status (running, completed, failed)"
    )
    error: Optional[str] = Field(None, description="Error message if any")
    file: Optional[str] = Field(
        None, description="File that caused error (for error events)"
    )


class ChatMessage(BaseModel):
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")


class ChatSource(BaseModel):
    document_name: str = Field(..., description="Name of source document")
    chunk_content: str = Field(..., description="Content of the chunk used")
    relevance_score: float = Field(
        ..., ge=0, le=1, description="Relevance score (0-1)"
    )


class ChatRequest(BaseModel):
    message: str = Field(..., min_length=1, description="User's message")
    conversation_id: Optional[UUID] = Field(
        None, description="Existing conversation ID (creates new if not provided)"
    )
    folder_path: Optional[str] = Field(
        None, description="Folder to scope document search"
    )


class ChatResponse(BaseModel):
    conversation_id: UUID = Field(..., description="Conversation ID")
    message: str = Field(..., description="Assistant's response")
    sources: list[ChatSource] = Field(
        default_factory=list, description="Sources used for response"
    )


class ConversationSummary(BaseModel):
    id: UUID = Field(..., description="Conversation ID")
    title: Optional[str] = Field(None, description="Conversation title")
    folder_path: Optional[str] = Field(None, description="Folder context")
    created_at: datetime = Field(..., description="When conversation started")
    message_count: int = Field(..., description="Number of messages")


class ConversationDetail(BaseModel):
    id: UUID = Field(..., description="Conversation ID")
    title: Optional[str] = Field(None, description="Conversation title")
    folder_path: Optional[str] = Field(None, description="Folder context")
    messages: list[ChatMessage] = Field(
        default_factory=list, description="All messages"
    )
    created_at: datetime = Field(..., description="When conversation started")


class ConversationCreate(BaseModel):
    title: Optional[str] = Field(None, description="Conversation title")
    folder_path: Optional[str] = Field(None, description="Folder context")
