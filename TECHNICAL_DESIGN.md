# One-Stop RAG Solution - Technical Design Document

**Version:** 1.1
**Date:** 2025-12-29

---

## Table of Contents

1. [Project Setup](#1-project-setup)
2. [Executive Summary](#2-executive-summary)
3. [System Architecture](#3-system-architecture)
4. [Technology Stack](#4-technology-stack)
5. [Database Schema](#5-database-schema)
6. [Backend Services](#6-backend-services)
7. [API Endpoints](#7-api-endpoints)
8. [Frontend Components](#8-frontend-components)
9. [LangGraph Agent Architecture](#9-langgraph-agent-architecture)
10. [Configuration](#10-configuration)
11. [Development Setup](#11-development-setup)
12. [Implementation Notes & Lessons Learned](#12-implementation-notes--lessons-learned)
13. [Testing Strategy](#13-testing-strategy)

---

## 1. Project Setup

### Initial Project Creation

This project was bootstrapped from a reusable Python project template that provides a production-ready foundation with common services and infrastructure.

#### Template Repository

**Source:** Python Project Template (internal)
**Features Provided:**
- FastAPI backend with async PostgreSQL (SQLAlchemy 2.0)
- React + TypeScript + Vite frontend with TailwindCSS
- Docker Compose orchestration for all services
- Optional services: MongoDB, Neo4j, Redis, RabbitMQ/Celery
- Alembic for database migrations
- Health check endpoints
- Feature flag system
- Poetry for Python dependency management
- Pre-configured ESLint, Prettier, and type checking

#### Setup Steps

```bash
# 1. Clone the template repository
git clone https://github.com/nitinnat/python-project-template.git one-stop-rag
cd one-stop-rag

# 2. Remove template git history and reinitialize
rm -rf .git
git init
git add .
git commit -m "Initial commit from template"

# 3. Update project-specific files
# - Update README.md with project description
# - Update package names in frontend/package.json
# - Update project name in backend/pyproject.toml
# - Clear TECHNICAL_DESIGN.md and IMPLEMENTATION_LOG.md
```

### Template Structure Inherited

```
one-stop-rag/
├── backend/
│   ├── app/
│   │   ├── api/v1/          # API endpoints (health, admin, documents, graph)
│   │   ├── models/          # SQLAlchemy models (postgres, mongodb, neo4j)
│   │   ├── repositories/    # Data access layer
│   │   ├── services/        # Business logic
│   │   ├── schemas/         # Pydantic models
│   │   ├── helpers/         # Utilities (postgres, redis, celery, llm clients)
│   │   ├── config/          # Settings and feature flags
│   │   └── main.py          # FastAPI app entry point
│   ├── alembic/             # Database migrations
│   ├── Dockerfile
│   └── pyproject.toml       # Poetry dependencies
├── frontend/
│   ├── src/
│   │   ├── api/             # API client functions
│   │   ├── components/      # React components
│   │   ├── pages/           # Page components
│   │   ├── layouts/         # Layout components
│   │   ├── context/         # React context providers
│   │   └── hooks/           # Custom React hooks
│   ├── Dockerfile
│   └── package.json
├── docker-compose.yml       # Service orchestration
├── Makefile                 # Common commands
└── .env                     # Environment variables
```

### Services Configured in Template

| Service | Purpose | Default Port |
|---------|---------|--------------|
| backend | FastAPI application | 8000 |
| frontend | React application | 5173 |
| postgres | Primary database | 5432 |
| redis | Caching & sessions | 6379 |
| mongodb | Document database (optional) | 27017 |
| neo4j | Graph database (optional) | 7474, 7687 |
| rabbitmq | Message queue (optional) | 5672, 15672 |
| ollama | LLM inference (optional) | 11434 |

### Template Modifications for RAG

The following changes were made to adapt the template for the RAG use case:

1. **PostgreSQL Image:** Changed from `postgres:16-alpine` to `pgvector/pgvector:pg16` for vector support
2. **Ollama Service:** Added to docker-compose.yml with model auto-pull configuration
3. **Dependencies:** Added RAG-specific packages:
   - Backend: markitdown, langgraph, tiktoken, pgvector, langchain-text-splitters
   - Frontend: react-markdown, remark-gfm
4. **New Feature Flags:** Added `ENABLE_PGVECTOR=true` and `ENABLE_LLM_OLLAMA=true`
5. **Environment Variables:** Configured `OLLAMA_HOST` and `OLLAMA_MODELS`

### Benefits of Using the Template

- **Rapid Development:** Pre-configured infrastructure saved ~2 days of setup time
- **Best Practices:** Built-in patterns for services, repositories, and API structure
- **Production-Ready:** Health checks, migrations, error handling already implemented
- **Flexibility:** Feature flags allow enabling only needed services
- **Consistency:** Established code organization and styling conventions

---

## 2. Executive Summary

One-Stop RAG is a production-ready Retrieval-Augmented Generation solution that allows users to:

1. **Select a document folder** via UI with persistence
2. **Ingest documents** (PDF, DOCX, PPTX, XLSX, TXT, MD) into a vector database
3. **Chat with documents** using multi-turn conversations powered by LangGraph

### Key Features

| Feature | Implementation |
|---------|----------------|
| Document Conversion | Microsoft's `markitdown` library |
| Chunking | LangChain RecursiveCharacterTextSplitter (1000 tokens, 200 overlap) |
| Embeddings | Ollama `nomic-embed-text` (768 dimensions) |
| LLM | Ollama `phi3` model |
| Vector Storage | PostgreSQL + PGVector with HNSW indexing |
| Conversation Memory | PostgreSQL (persisted) |
| Agent Framework | LangGraph for multi-turn conversations |

---

## 2. System Architecture

### High-Level Overview

```
┌─────────────────────────────────────────────────────────────────────────┐
│                              Frontend (React)                            │
│  ┌─────────────────────────────────────────────────────────────────┐   │
│  │                    /rag Page with Tabs                           │   │
│  │  ┌─────────────────────┐    ┌─────────────────────────────────┐ │   │
│  │  │   Documents Tab      │    │         Chat Tab                 │ │   │
│  │  │  - Folder selector   │    │  - Message history               │ │   │
│  │  │  - File list         │    │  - Source citations              │ │   │
│  │  │  - Ingest button     │    │  - Input field                   │ │   │
│  │  └─────────────────────┘    └─────────────────────────────────┘ │   │
│  └─────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Backend (FastAPI)                               │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      RAG API Endpoints                            │  │
│  │  /rag/documents/folder  /rag/documents/ingest  /rag/chat         │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                       Service Layer                               │  │
│  │  ┌────────────────┐  ┌────────────────┐  ┌────────────────────┐ │  │
│  │  │ Ingestion      │  │ Embedding      │  │ LangGraph          │ │  │
│  │  │ Service        │  │ Service        │  │ Chat Agent         │ │  │
│  │  │ (markitdown)   │  │ (Ollama)       │  │ (Retrieve→Generate)│ │  │
│  │  └────────────────┘  └────────────────┘  └────────────────────┘ │  │
│  └──────────────────────────────────────────────────────────────────┘  │
│                                    │                                     │
│  ┌──────────────────────────────────────────────────────────────────┐  │
│  │                      Repository Layer                             │  │
│  │               RAG Repository (Vector Search + CRUD)               │  │
│  └──────────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────────┘
                                    │
                                    ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                          Data Layer                                      │
│  ┌───────────────────────────────┐  ┌────────────────────────────────┐ │
│  │     PostgreSQL + PGVector     │  │          Ollama                 │ │
│  │  - rag_documents              │  │  - nomic-embed-text (embed)    │ │
│  │  - rag_chunks (embeddings)    │  │  - phi3 (chat)                 │ │
│  │  - rag_conversations          │  │                                 │ │
│  │  - rag_messages               │  │                                 │ │
│  └───────────────────────────────┘  └────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────────────┘
```

### Request Flow

```
User Query → Embed Query → Vector Search → Retrieve Top-K Chunks →
Build Context → Generate Response (phi3) → Return with Sources
```

---

## 3. Technology Stack

### Backend

| Component | Technology | Version |
|-----------|------------|---------|
| Web Framework | FastAPI | 0.109+ |
| ORM | SQLAlchemy 2.0 | async |
| Vector DB | PostgreSQL + PGVector | 16 / 0.7+ |
| Document Conversion | markitdown | 0.0.1a3 |
| Text Splitting | LangChain | 0.1+ |
| Agent Framework | LangGraph | 0.2+ |
| Token Counting | tiktoken | 0.5+ |
| LLM/Embeddings | Ollama | phi3 / nomic-embed-text |

### Frontend

| Component | Technology | Version |
|-----------|------------|---------|
| UI Framework | React | 18 |
| Language | TypeScript | 5.3+ |
| Build Tool | Vite | 5 |
| Styling | TailwindCSS | 3.4+ |
| State Management | TanStack Query | v5 |
| Markdown Rendering | react-markdown | 9+ |
| HTTP Client | Axios | 1.6+ |

---

## 4. Database Schema

### Entity Relationship Diagram

```
┌─────────────────────┐
│    rag_documents    │
├─────────────────────┤
│ id (UUID, PK)       │
│ file_name           │
│ file_path           │
│ file_type           │
│ file_size           │
│ file_hash (unique)  │───────┐
│ folder_path         │       │
│ markdown_content    │       │
│ status              │       │
│ error_message       │       │
│ metadata (JSON)     │       │
│ created_at          │       │
│ updated_at          │       │
└─────────────────────┘       │
         │                    │
         │ 1:N                │
         ▼                    │
┌─────────────────────┐       │
│     rag_chunks      │       │
├─────────────────────┤       │
│ id (UUID, PK)       │       │
│ document_id (FK)    │───────┘
│ chunk_index         │
│ content             │
│ token_count         │
│ embedding (Vector)  │ ◄── HNSW Index
│ metadata (JSON)     │
│ created_at          │
│ updated_at          │
└─────────────────────┘

┌─────────────────────┐
│  rag_conversations  │
├─────────────────────┤
│ id (UUID, PK)       │
│ title               │
│ folder_path         │
│ is_active           │
│ created_at          │
│ updated_at          │
└─────────────────────┘
         │
         │ 1:N
         ▼
┌─────────────────────┐
│    rag_messages     │
├─────────────────────┤
│ id (UUID, PK)       │
│ conversation_id(FK) │
│ role                │
│ content             │
│ sources (JSON)      │
│ token_count         │
│ created_at          │
│ updated_at          │
└─────────────────────┘
```

### Table Definitions

#### rag_documents
```sql
CREATE TABLE rag_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    file_name VARCHAR(500) NOT NULL,
    file_path VARCHAR(2000) NOT NULL,
    file_type VARCHAR(50) NOT NULL,
    file_size INTEGER NOT NULL,
    file_hash VARCHAR(64) NOT NULL UNIQUE,
    folder_path VARCHAR(2000) NOT NULL,
    markdown_content TEXT,
    status VARCHAR(50) DEFAULT 'pending',
    error_message TEXT,
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_rag_documents_folder ON rag_documents(folder_path);
CREATE INDEX idx_rag_documents_hash ON rag_documents(file_hash);
```

#### rag_chunks
```sql
CREATE TABLE rag_chunks (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    document_id UUID NOT NULL REFERENCES rag_documents(id) ON DELETE CASCADE,
    chunk_index INTEGER NOT NULL,
    content TEXT NOT NULL,
    token_count INTEGER NOT NULL,
    embedding VECTOR(768),
    metadata JSONB DEFAULT '{}',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

-- HNSW index for fast cosine similarity search
CREATE INDEX idx_rag_chunks_embedding ON rag_chunks
    USING hnsw (embedding vector_cosine_ops);
```

#### rag_conversations
```sql
CREATE TABLE rag_conversations (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    title VARCHAR(500),
    folder_path VARCHAR(2000),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);
```

#### rag_messages
```sql
CREATE TABLE rag_messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    conversation_id UUID NOT NULL REFERENCES rag_conversations(id) ON DELETE CASCADE,
    role VARCHAR(20) NOT NULL,
    content TEXT NOT NULL,
    sources JSONB DEFAULT '[]',
    token_count INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ
);

CREATE INDEX idx_rag_messages_conversation ON rag_messages(conversation_id);
```

---

## 5. Backend Services

### Service Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      RagService (Facade)                     │
│  Orchestrates all RAG operations                            │
└─────────────────────────────────────────────────────────────┘
         │                    │                    │
         ▼                    ▼                    ▼
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ IngestionService│  │EmbeddingService │  │  RagChatAgent   │
│                 │  │                 │  │   (LangGraph)   │
│ - list_folder() │  │ - embed_text()  │  │                 │
│ - ingest_folder│  │ - embed_batch() │  │ - Retrieve node │
│ - convert_to_md│  │                 │  │ - Augment node  │
│ - chunk_text() │  │                 │  │ - Generate node │
└─────────────────┘  └─────────────────┘  └─────────────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              ▼
                 ┌─────────────────────────┐
                 │     RagRepository       │
                 │  - create_document()    │
                 │  - create_chunks()      │
                 │  - vector_search()      │
                 │  - conversation CRUD    │
                 └─────────────────────────┘
```

### 5.1 Embedding Service

**File:** `backend/app/services/rag/embedding_service.py`

```python
class EmbeddingService:
    """Generate embeddings using Ollama nomic-embed-text model."""

    model: str = "nomic-embed-text"

    async def embed_text(self, text: str) -> List[float]:
        """Generate embedding for single text (768 dimensions)."""

    async def embed_batch(self, texts: List[str], batch_size: int = 10) -> List[List[float]]:
        """Generate embeddings for multiple texts."""
```

### 5.2 Ingestion Service

**File:** `backend/app/services/rag/ingestion_service.py`

```python
class IngestionService:
    """Process documents: convert → chunk → embed → store."""

    SUPPORTED_EXTENSIONS = {'.pdf', '.docx', '.pptx', '.xlsx', '.txt', '.md'}

    async def list_folder_files(self, folder_path: str) -> List[FileInfo]:
        """List all supported files in a folder."""

    async def ingest_folder(self, folder_path: str) -> AsyncGenerator[IngestProgress, None]:
        """Ingest all documents with progress updates (SSE)."""

    async def _convert_to_markdown(self, file_path: str) -> str:
        """Convert document to markdown using markitdown."""

    async def _chunk_markdown(self, content: str, document_id: UUID) -> List[ChunkData]:
        """Chunk markdown using LangChain splitter (1000 tokens, 200 overlap)."""
```

### 5.3 LangGraph Chat Agent

**File:** `backend/app/services/rag/chat_agent.py`

See [Section 8](#8-langgraph-agent-architecture) for detailed architecture.

---

## 6. API Endpoints

### RAG Router: `/api/v1/rag`

| Endpoint | Method | Description | Request | Response |
|----------|--------|-------------|---------|----------|
| `/documents/folder` | GET | List folder files | `?path=/path/to/folder` | `FolderContents` |
| `/documents/ingest` | POST | Ingest folder | `{folder_path: str}` | SSE stream |
| `/documents/status` | GET | Get ingestion status | `?folder_path=...` | `List[DocumentStatus]` |
| `/chat` | POST | Send chat message | `ChatRequest` | `ChatResponse` |
| `/chat/stream` | POST | Stream chat response | `ChatRequest` | SSE stream |
| `/conversations` | GET | List conversations | - | `List[ConversationSummary]` |
| `/conversations/{id}` | GET | Get conversation detail | - | `ConversationDetail` |

### Request/Response Schemas

```python
class FolderContents(BaseModel):
    folder_path: str
    files: List[FileInfo]
    total_count: int

class FileInfo(BaseModel):
    name: str
    path: str
    type: str  # pdf, docx, pptx, xlsx, txt, md
    size: int
    modified_at: datetime

class ChatRequest(BaseModel):
    message: str
    conversation_id: Optional[UUID] = None
    folder_path: Optional[str] = None

class ChatResponse(BaseModel):
    conversation_id: UUID
    message: str
    sources: List[ChatSource]

class ChatSource(BaseModel):
    document_name: str
    chunk_content: str
    relevance_score: float
```

---

## 7. Frontend Components

### Component Tree

```
App.tsx
└── MainLayout
    └── /rag route
        └── RagPage
            ├── Tab Navigation (Documents | Chat)
            ├── DocumentsTab
            │   ├── FolderInput (with localStorage persistence)
            │   ├── FileList
            │   │   └── FileCard (name, type, size, status)
            │   └── IngestButton (with progress bar)
            └── ChatTab
                ├── FolderContext (shows current folder)
                ├── MessageList
                │   ├── UserMessage
                │   └── AssistantMessage
                │       └── SourcesAccordion
                └── ChatInput
```

### State Management

```typescript
// RagPage state
const [activeTab, setActiveTab] = useState<'documents' | 'chat'>('documents');
const [selectedFolder, setSelectedFolder] = useState<string>(() =>
    localStorage.getItem('rag_selected_folder') || ''
);

// ChatTab state
const [messages, setMessages] = useState<ChatMessage[]>([]);
const [conversationId, setConversationId] = useState<string | undefined>();
```

### API Client

```typescript
// frontend/src/api/rag.ts
export const ragApi = {
    listFolder(path: string): Promise<FolderContents>,
    ingestFolder(path: string, onProgress: (event) => void): EventSource,
    chat(request: ChatRequest): Promise<ChatResponse>,
    chatStream(request: ChatRequest, onMessage: (event) => void): EventSource,
    listConversations(): Promise<ConversationSummary[]>,
};
```

---

## 8. LangGraph Agent Architecture

### Graph Structure

```
┌─────────┐     ┌──────────┐     ┌─────────┐     ┌──────────┐
│  Entry  │ ──► │ Retrieve │ ──► │ Augment │ ──► │ Generate │ ──► End
└─────────┘     └──────────┘     └─────────┘     └──────────┘
```

### Agent State

```python
class AgentState(TypedDict):
    messages: List[Dict[str, str]]  # Conversation history
    query: str                       # Current user query
    context: str                     # Retrieved and formatted chunks
    sources: List[Dict[str, Any]]   # Source metadata
    folder_path: Optional[str]       # Folder scope for search
    final_response: Optional[str]    # Generated response
```

### Node Implementations

#### Retrieve Node
```python
async def retrieve_node(state: AgentState) -> Dict[str, Any]:
    """
    1. Generate embedding for user query
    2. Perform vector search in PGVector
    3. Return top-5 most similar chunks
    """
    query_embedding = await embedding_service.embed_text(state["query"])
    results = await repository.vector_search(
        embedding=query_embedding,
        folder_path=state.get("folder_path"),
        limit=5
    )
    return {"sources": format_sources(results)}
```

#### Augment Node
```python
async def augment_node(state: AgentState) -> Dict[str, Any]:
    """
    Format retrieved chunks into context string.
    """
    context_parts = []
    for i, source in enumerate(state["sources"], 1):
        context_parts.append(
            f"[Document {i}: {source['document_name']}]\n{source['chunk_content']}"
        )
    return {"context": "\n\n---\n\n".join(context_parts)}
```

#### Generate Node
```python
async def generate_node(state: AgentState) -> Dict[str, Any]:
    """
    Generate response using Ollama phi3 with:
    - System prompt with RAG context
    - Full conversation history
    - Current query
    """
    system_prompt = f"""You are a helpful AI assistant that answers questions
    based on the provided documents.

    CONTEXT:
    {state["context"]}

    Answer based on the context. If unsure, acknowledge uncertainty."""

    response = await ollama_client.chat(
        model="phi3",
        messages=[
            {"role": "system", "content": system_prompt},
            *state["messages"],
            {"role": "user", "content": state["query"]}
        ]
    )
    return {"final_response": response["content"]}
```

### Vector Search Query

```sql
SELECT
    c.id,
    c.content,
    c.chunk_index,
    d.file_name,
    1 - (c.embedding <=> :query_embedding::vector) as similarity
FROM rag_chunks c
JOIN rag_documents d ON c.document_id = d.id
WHERE d.status = 'completed'
  AND (:folder_path IS NULL OR d.folder_path = :folder_path)
ORDER BY c.embedding <=> :query_embedding::vector
LIMIT 5;
```

---

## 9. Configuration

### Environment Variables

```bash
# .env

# Feature Flags
ENABLE_PGVECTOR=true
ENABLE_LLM_OLLAMA=true

# Ollama Configuration
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODELS=phi3,nomic-embed-text

# RAG Configuration (optional overrides)
RAG_CHUNK_SIZE=1000
RAG_CHUNK_OVERLAP=200
RAG_TOP_K=5
RAG_EMBEDDING_MODEL=nomic-embed-text
RAG_CHAT_MODEL=phi3
```

### Feature Flag Integration

RAG routes are automatically enabled when `ENABLE_PGVECTOR=true` in the environment.

---

## 10. Development Setup

### Prerequisites

- Docker Desktop 24+
- Docker Compose 2.0+

### Quick Start

```bash
# 1. Clone repository
git clone <repo-url>
cd one-stop-rag

# 2. Start services
make dev

# 3. Access application
# Frontend: http://localhost:5173/rag
# Backend API: http://localhost:8000/docs
```

### Running Migrations

```bash
# Apply RAG tables migration
make migrate
```

### Testing the RAG Pipeline

```bash
# 1. List folder files
curl "http://localhost:8000/api/v1/rag/documents/folder?path=/path/to/docs"

# 2. Ingest documents (SSE)
curl -X POST "http://localhost:8000/api/v1/rag/documents/ingest" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/path/to/docs"}'

# 3. Chat with documents
curl -X POST "http://localhost:8000/api/v1/rag/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is this document about?"}'
```

---

## File Structure Summary

### New Backend Files

```
backend/app/
├── models/postgres/
│   └── rag.py                    # Database models
├── schemas/
│   └── rag.py                    # Pydantic schemas
├── repositories/
│   └── rag_repository.py         # Data access layer
├── services/rag/
│   ├── __init__.py
│   ├── embedding_service.py      # Ollama embeddings
│   ├── ingestion_service.py      # Document processing
│   ├── chat_agent.py             # LangGraph agent
│   └── rag_service.py            # Facade service
└── api/v1/
    └── rag.py                    # REST endpoints

backend/alembic/versions/
└── YYYYMMDD_rag_tables.py        # Migration
```

### New Frontend Files

```
frontend/src/
├── api/
│   ├── ragTypes.ts               # TypeScript types
│   └── rag.ts                    # API client
├── pages/
│   └── Rag.tsx                   # Main page
└── components/rag/
    ├── DocumentsTab.tsx          # Document management
    └── ChatTab.tsx               # Chat interface
```

---

## 11. Implementation Notes & Lessons Learned

### Critical Fixes Applied

#### 1. SQLAlchemy Async Greenlet Issue
**Problem:** `MissingGreenlet` error when accessing lazy-loaded relationships in async context.

**Solution:** Check if `conversation_id` exists before accessing `conversation.messages`:
```python
# rag_service.py:173
if conversation_id and conversation.messages:  # Not just: if conversation.messages
```

#### 2. Docker Network Hostname
**Problem:** Backend couldn't connect to Ollama using `localhost`.

**Solution:** Use Docker service name `ollama` instead:
```bash
OLLAMA_HOST=http://ollama:11434  # Not localhost:11434
```

#### 3. PostgreSQL Parameter Binding
**Problem:** Named parameters (`:param`) don't work with asyncpg.

**Solution:** Use positional parameters (`$1, $2, $3`):
```python
# Instead of: WHERE d.folder_path = :folder_path
# Use: WHERE d.folder_path = $1
```

#### 4. PGVector Extension
**Problem:** Standard PostgreSQL image doesn't include pgvector.

**Solution:** Use `pgvector/pgvector:pg16` image in docker-compose.yml.

### Key Architecture Decisions

1. **Manual Node Execution:** LangGraph's `ainvoke()` caused issues with SQLAlchemy async context, so nodes are executed manually in sequence.

2. **Positional SQL Parameters:** All raw SQL in repositories uses positional parameters for asyncpg compatibility.

3. **Eager Loading:** Conversations with messages use `selectinload()` to avoid lazy loading issues.

4. **SSE for Progress:** Document ingestion uses Server-Sent Events for real-time progress updates.

---

## 12. Testing Strategy (Planned)

### Backend Tests (pytest)
- **Unit Tests:** Services with mocked dependencies
- **Integration Tests:** Full API with test database
- **Vector Search Tests:** Pre-computed embeddings for deterministic results

### Frontend Tests (Playwright)
- **E2E Flows:** Document ingestion → Chat → Conversation management
- **Component Tests:** DocumentsTab, ChatTab with mocked API

### Coverage Targets
- Backend: 90%+ on RAG services and repositories
- Frontend: Critical user flows with Playwright

---

**Document Status:** Final v1.1 (Updated after implementation)
**Implementation Status:** Complete and Operational
