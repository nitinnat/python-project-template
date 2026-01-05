import hashlib
import logging
from datetime import datetime
from pathlib import Path
from typing import AsyncGenerator, Optional
from uuid import UUID

import tiktoken

from app.config.settings import settings
from app.repositories.rag_repository import RagRepository
from app.services.rag.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)

SUPPORTED_EXTENSIONS = {".pdf", ".docx", ".pptx", ".xlsx", ".txt", ".md"}


class IngestionService:
    def __init__(
        self,
        repository: RagRepository,
        embedding_service: EmbeddingService,
        chunk_size: int = 5000,
        chunk_overlap: int = 500,
    ):
        self.repository = repository
        self.embedding_service = embedding_service
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        self.documents_root = Path(settings.documents_root).expanduser().resolve()

    def normalize_folder_path(self, folder_path: Optional[str]) -> str:
        requested = (
            Path(folder_path).expanduser().resolve()
            if folder_path
            else self.documents_root
        )
        root = self.documents_root

        if requested != root:
            raise ValueError(f"Folder path must be the documents root: {root}")

        if not root.exists():
            raise ValueError(f"Documents folder does not exist: {root}")

        if not root.is_dir():
            raise ValueError(f"Documents path is not a directory: {root}")

        return str(root)

    def list_folder_files(self, folder_path: str) -> list[dict]:
        normalized_path = self.normalize_folder_path(folder_path)
        folder = Path(normalized_path)

        if not folder.exists():
            raise ValueError(f"Folder does not exist: {folder_path}")

        if not folder.is_dir():
            raise ValueError(f"Path is not a directory: {folder_path}")

        files = []
        for file_path in folder.iterdir():
            if file_path.is_file() and file_path.suffix.lower() in SUPPORTED_EXTENSIONS:
                stat = file_path.stat()
                files.append({
                    "name": file_path.name,
                    "path": str(file_path),
                    "type": file_path.suffix.lower()[1:],  # Remove leading dot
                    "size": stat.st_size,
                    "modified_at": datetime.fromtimestamp(stat.st_mtime),
                })

        return sorted(files, key=lambda x: x["name"])

    async def ingest_folder(
        self, folder_path: str
    ) -> AsyncGenerator[dict, None]:
        normalized_path = self.normalize_folder_path(folder_path)
        files = self.list_folder_files(normalized_path)
        total = len(files)

        if total == 0:
            yield {
                "type": "complete",
                "total": 0,
                "processed": 0,
                "status": "completed",
            }
            return

        for idx, file_info in enumerate(files):
            yield {
                "type": "progress",
                "total": total,
                "processed": idx,
                "current_file": file_info["name"],
                "status": "running",
            }

            try:
                await self._ingest_single_file(file_info, normalized_path)
                logger.info(f"Ingested: {file_info['name']}")
            except Exception as e:
                logger.error(f"Failed to ingest {file_info['name']}: {e}")
                yield {
                    "type": "error",
                    "file": file_info["name"],
                    "error": str(e),
                    "total": total,
                    "processed": idx,
                    "status": "running",
                }

        yield {
            "type": "complete",
            "total": total,
            "processed": total,
            "current_file": None,
            "status": "completed",
        }

    async def _ingest_single_file(
        self, file_info: dict, folder_path: str
    ) -> None:
        file_hash = self._compute_file_hash(file_info["path"])
        existing = await self.repository.get_document_by_name(file_info["name"])

        if existing:
            await self.repository.delete_document(existing.id)

        document = await self.repository.create_document(
            file_name=file_info["name"],
            file_path=file_info["path"],
            file_type=file_info["type"],
            file_size=file_info["size"],
            file_hash=file_hash,
            folder_path=folder_path,
            status="processing",
        )

        try:
            markdown_content = self._convert_to_markdown(file_info["path"])
            await self.repository.update_document_content(
                document.id, markdown_content
            )

            chunks = self._chunk_markdown(markdown_content, document.id)
            if not chunks:
                raise ValueError("No chunks generated from document")

            chunk_texts = [c["content"] for c in chunks]
            embeddings = await self.embedding_service.embed_batch(chunk_texts)

            for chunk, embedding in zip(chunks, embeddings):
                chunk["embedding"] = embedding

            await self.repository.create_chunks_batch(chunks)
            await self.repository.update_document_status(
                document.id, "completed"
            )

        except Exception as e:
            logger.error(f"Error processing {file_info['name']}: {e}")
            await self.repository.update_document_status(
                document.id, "failed", str(e)
            )
            raise

    def _convert_to_markdown(self, file_path: str) -> str:
        from markitdown import MarkItDown

        md = MarkItDown()
        result = md.convert(file_path)
        return result.text_content

    def _chunk_markdown(
        self, content: str, document_id: UUID
    ) -> list[dict]:
        from langchain_text_splitters import RecursiveCharacterTextSplitter

        splitter = RecursiveCharacterTextSplitter.from_tiktoken_encoder(
            encoding_name="cl100k_base",
            chunk_size=self.chunk_size,
            chunk_overlap=self.chunk_overlap,
            separators=[
                "\n## ",
                "\n### ",
                "\n#### ",
                "\n\n",
                "\n",
                ". ",
                " ",
                "",
            ],
        )

        texts = splitter.split_text(content)

        chunks = []
        for idx, text in enumerate(texts):
            token_count = len(self.tokenizer.encode(text))
            chunks.append({
                "document_id": document_id,
                "chunk_index": idx,
                "content": text,
                "token_count": token_count,
                "metadata": {"chunk_type": "markdown"},
            })

        return chunks

    def _compute_file_hash(self, file_path: str) -> str:
        sha256 = hashlib.sha256()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)
        return sha256.hexdigest()

    async def get_document_status(
        self, folder_path: str
    ) -> list[dict]:
        normalized_path = self.normalize_folder_path(folder_path)
        documents = await self.repository.get_documents_by_folder(normalized_path)
        result = []

        for doc in documents:
            chunk_count = await self.repository.get_chunk_count_by_document(doc.id)
            result.append({
                "id": doc.id,
                "file_name": doc.file_name,
                "status": doc.status,
                "chunk_count": chunk_count,
                "error_message": doc.error_message,
                "created_at": doc.created_at,
            })

        return result
