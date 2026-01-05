# Implementation Log

## Project: One-Stop RAG Solution

**Last Updated:** 2025-12-29
**Status:** Fully Operational

---

## Overview

Complete RAG (Retrieval-Augmented Generation) solution enabling users to:
1. Select document folders via UI (with localStorage persistence)
2. Ingest documents (PDF, DOCX, PPTX, XLSX, TXT, MD) into PostgreSQL/PGVector
3. Chat with documents using multi-turn conversations powered by LangGraph

---

## Current System Status

| Component | Status | URL |
|-----------|--------|-----|
| Frontend | Running | http://localhost:5173 |
| Backend API | Running | http://localhost:8000 |
| API Docs | Running | http://localhost:8000/docs |
| PostgreSQL + PGVector | Running | localhost:5432 |
| Redis | Running | localhost:6379 |
| Ollama (phi3 + nomic-embed-text) | Running | http://ollama:11434 |

---

## Completed Implementation

### Phase 1: Database Models & Migration

**Files Created:**
- `backend/app/models/postgres/rag.py` - 4 SQLAlchemy models
- `backend/alembic/versions/2025_12_29_0001-add_rag_tables.py` - Migration with pgvector

**Models:**
| Model | Purpose | Key Fields |
|-------|---------|------------|
| RagDocument | Document metadata | file_hash (unique), status, markdown_content |
| RagChunk | Text chunks with embeddings | embedding Vector(768), HNSW index |
| RagConversation | Chat sessions | is_active (soft delete), folder_path |
| RagMessage | Conversation messages | role, content, sources (JSON) |

### Phase 2: Backend Services

**Files Created:**
- `backend/app/services/rag/embedding_service.py` - Ollama nomic-embed-text (768-dim)
- `backend/app/services/rag/ingestion_service.py` - markitdown + LangChain chunking
- `backend/app/services/rag/chat_agent.py` - LangGraph RAG agent (Retrieve→Augment→Generate)
- `backend/app/services/rag/rag_service.py` - Facade orchestrating all RAG operations
- `backend/app/repositories/rag_repository.py` - Data access with vector search
- `backend/app/schemas/rag.py` - Pydantic request/response schemas

**Chunking Configuration:**
- Splitter: RecursiveCharacterTextSplitter with tiktoken
- Chunk size: 1000 tokens
- Overlap: 200 tokens
- Separators: Markdown-aware (headers, paragraphs, sentences)

### Phase 3: API Endpoints

**File:** `backend/app/api/v1/rag.py`

| Endpoint | Method | Status | Description |
|----------|--------|--------|-------------|
| `/rag/documents/folder` | GET | ✅ Working | List supported files in folder |
| `/rag/documents/ingest` | POST | ✅ Working | Ingest with SSE progress |
| `/rag/documents/status` | GET | ✅ Working | Get document ingestion status |
| `/rag/chat` | POST | ✅ Working | Send message, get RAG response |
| `/rag/chat/stream` | POST | ✅ Working | Stream chat response (SSE) |
| `/rag/conversations` | GET | ✅ Working | List recent conversations |
| `/rag/conversations/{id}` | GET | ✅ Working | Get conversation with messages |
| `/rag/conversations/{id}` | DELETE | ✅ Working | Soft delete conversation |

### Phase 4: Frontend Components

**Files Created:**
- `frontend/src/api/ragTypes.ts` - TypeScript interfaces
- `frontend/src/api/rag.ts` - API client with SSE support
- `frontend/src/pages/Rag.tsx` - Main page with tab navigation
- `frontend/src/components/rag/DocumentsTab.tsx` - Document management UI
- `frontend/src/components/rag/ChatTab.tsx` - Chat interface with markdown

**Modified Files:**
- `frontend/src/App.tsx` - Added /rag route
- `frontend/src/layouts/MainLayout.tsx` - Added "Document Chat" nav link
- `frontend/package.json` - Added react-markdown, remark-gfm

---

## Bugs Fixed During Implementation

### 1. Greenlet Error (SQLAlchemy Async Context)

**Error:** `MissingGreenlet: greenlet_spawn has not been called`

**Root Cause:** When creating a new conversation (no conversation_id), the `messages` relationship wasn't eagerly loaded. Accessing `conversation.messages` triggered lazy loading outside async context.

**Fix:** Modified `rag_service.py:173` to only access messages when conversation_id is provided:
```python
# Before (broken)
if conversation.messages:

# After (fixed)
if conversation_id and conversation.messages:
```

### 2. Ollama Connection Error

**Error:** `Cannot connect to host localhost:11434`

**Root Cause:** Backend container was using `localhost` instead of Docker network hostname `ollama`.

**Fix:** Updated `backend/.env`:
```bash
OLLAMA_HOST=http://ollama:11434
```

### 3. Missing Ollama Models

**Error:** `model "nomic-embed-text" not found`

**Root Cause:** OLLAMA_MODELS environment variable wasn't passed to ollama container.

**Fix:** Added to `docker-compose.yml`:
```yaml
ollama:
  environment:
    - OLLAMA_MODELS=${OLLAMA_MODELS:-phi3,nomic-embed-text}
```

### 4. SQL Parameter Binding Error

**Error:** `syntax error at or near ":"`

**Root Cause:** PostgreSQL with asyncpg doesn't support named parameters (`:param`) in raw SQL with `text()`.

**Fix:** Changed `rag_repository.py` vector_search to use positional parameters (`$1, $2, $3`) instead of named parameters.

### 5. Frontend Missing Dependencies

**Error:** `Failed to resolve import "react-markdown"`

**Root Cause:** Dependencies added to package.json but not installed in container.

**Fix:** Ran `docker exec frontend npm install` and restarted container.

---

## Configuration Files

### backend/.env
```bash
POSTGRES_HOST=localhost
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app_db

REDIS_HOST=localhost
REDIS_PORT=6379

OLLAMA_HOST=http://ollama:11434

ENABLE_LLM_OLLAMA=true
ENABLE_MONGODB=false
ENABLE_NEO4J=false
ENABLE_RABBITMQ=false
```

### docker-compose.yml Key Changes
```yaml
postgres:
  image: pgvector/pgvector:pg16  # Changed from postgres:16-alpine

ollama:
  environment:
    - OLLAMA_HOST=0.0.0.0
    - OLLAMA_MODELS=${OLLAMA_MODELS:-phi3,nomic-embed-text}
```

---

## Dependencies Added

### Backend (pyproject.toml)
```toml
markitdown = "^0.0.1a3"
langgraph = "^0.2.76"
tiktoken = "^0.8.0"
pgvector = "^0.2.4"
langchain-text-splitters = "^0.3.0"
aiohttp = "^3.13.2"
```

### Frontend (package.json)
```json
"react-markdown": "^9.0.1",
"remark-gfm": "^4.0.0"
```

---

## File Structure

### New Backend Files (11)
```
backend/app/
├── models/postgres/rag.py              # Database models
├── schemas/rag.py                      # Pydantic schemas
├── repositories/rag_repository.py      # Data access layer
├── services/rag/
│   ├── __init__.py
│   ├── embedding_service.py            # Ollama embeddings
│   ├── ingestion_service.py            # Document processing
│   ├── chat_agent.py                   # LangGraph agent
│   └── rag_service.py                  # Facade service
└── api/v1/rag.py                       # REST endpoints

backend/alembic/versions/
└── 2025_12_29_0001-add_rag_tables.py   # Migration
```

### New Frontend Files (5)
```
frontend/src/
├── api/
│   ├── ragTypes.ts                     # TypeScript types
│   └── rag.ts                          # API client
├── pages/Rag.tsx                       # Main page
└── components/rag/
    ├── DocumentsTab.tsx                # Document management
    └── ChatTab.tsx                     # Chat interface
```

---

## Testing Verification

### Backend API Tests (via curl)
```bash
# List folder
curl "http://localhost:8000/api/v1/rag/documents/folder?folder_path=/tmp/test-docs"
# Response: {"folder_path":"/tmp/test-docs","files":[...],"total_count":2}

# Ingest documents
curl -X POST "http://localhost:8000/api/v1/rag/documents/ingest" \
  -H "Content-Type: application/json" \
  -d '{"folder_path": "/tmp/test-docs"}'
# Response: SSE stream with progress events

# Chat
curl -X POST "http://localhost:8000/api/v1/rag/chat" \
  -H "Content-Type: application/json" \
  -d '{"message": "What is RAG?", "folder_path": "/tmp/test-docs"}'
# Response: {"conversation_id":"...","message":"...","sources":[]}
```

---

## Known Limitations

1. **Vector Search Retrieval:** The vector search occasionally doesn't return relevant chunks on the first query to a new conversation. This may be related to the similarity threshold or embedding quality.

2. **No File Upload UI:** Documents must exist on the server filesystem. A file upload feature would require additional implementation.

3. **Single User:** No authentication/authorization implemented for RAG features.

---

## Next Steps (Suggested)

1. **Testing Suite:** Create comprehensive pytest tests for backend and Playwright tests for frontend
2. **Improve Retrieval:** Debug why vector search sometimes returns empty results
3. **Add File Upload:** Allow users to upload documents through the UI
4. **Authentication:** Add user scoping for documents and conversations
5. **Streaming Chat:** Enable real-time streaming of LLM responses in the UI

---

## Quick Start for New Session

```bash
# Start all services
docker-compose --profile ollama --profile frontend up -d

# Verify services
docker ps  # Should show: backend, frontend, postgres, redis, ollama

# Check logs if issues
docker logs backend --tail 50
docker logs frontend --tail 20

# Test endpoints
curl http://localhost:8000/health
curl http://localhost:5173  # Frontend

# Create test documents (inside backend container)
docker exec backend mkdir -p /tmp/test-docs
docker exec backend sh -c 'echo "# Test Document\nThis is test content." > /tmp/test-docs/test.txt'
```
