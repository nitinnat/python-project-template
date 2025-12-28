# Python Full-Stack Project Template - Technical Design Document

**Version:** 2.1
**Date:** 2025-12-29
**Author:** Claude (Anthropic)

**Changelog:**
- v2.1: Aligned document with current codebase (auth/admin removed, limited APIs, missing tests)
- v2.0: Added comprehensive feature flag system (build-time + runtime) and Admin UI
- v1.0: Initial design

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Project Goals](#project-goals)
3. [Technology Stack](#technology-stack)
4. [Architecture Overview](#architecture-overview)
5. [Project Structure](#project-structure)
6. [Component Specifications](#component-specifications)
7. [Feature Flag System](#feature-flag-system)
8. [Admin UI](#admin-ui)
9. [Docker Configuration](#docker-configuration)
10. [Service Helper Libraries](#service-helper-libraries)
11. [Example Implementations](#example-implementations)
12. [Configuration Management](#configuration-management)
13. [Development Workflow](#development-workflow)
14. [CI/CD Pipeline](#cicd-pipeline)
15. [Security Considerations](#security-considerations)
16. [Testing Strategy](#testing-strategy)
17. [Deployment Guide](#deployment-guide)
18. [Future Extensibility](#future-extensibility)

---

## 1. Executive Summary

This document outlines the technical design for a comprehensive Python full-stack project template that provides a production-ready foundation for building modern web applications. The template integrates industry-standard technologies including FastAPI, React, multiple database systems (PostgreSQL, MongoDB, Neo4j), message queuing (RabbitMQ + Celery), and LLM integrations.

**Key Features:**
- One-command startup via `docker compose up`
- **Feature flag system** for selective service activation (build-time; runtime CRUD wiring still pending)
- **Admin UI** (frontend scaffolding exists, backend endpoints removed)
- Complete service abstraction layers for all external dependencies
- Full-stack monorepo with backend (Python/FastAPI) and frontend (React/TypeScript)
- Production-ready logging and monitoring hooks (authentication removed)
- Code quality tooling configured; automated tests still to be written
- Multi-platform CI/CD pipelines (GitHub Actions + GitLab CI)

---

### Current Implementation Snapshot (reality check)

| Area | Status | Notes |
| --- | --- | --- |
| Auth/users/JWT | Removed | No auth modules, user models, or `/auth` endpoints. Frontend AuthContext/login routes currently have no backend to talk to. |
| Admin API/UI | Partial (frontend only) | Admin pages exist in React, but backend admin routes are absent. Feature flag UI cannot persist changes. |
| Runtime feature flags | Partial | Alembic migration and service exist; API routers exposing CRUD were removed. |
| APIs exposed | Limited | Live routes: `/health`, `/api/v1/documents/*` (requires MongoDB profile) and `/api/v1/graph/*` (requires Neo4j profile). |
| Background tasks & LLM | Stubbed | Celery workers, RabbitMQ, and LLM clients exist but are not exercised by current API surface. |
| Data stores | Mixed | Postgres + Redis always provisioned; MongoDB/Neo4j require compose profiles; PGVector enabled flag exists but no vectors written today. |
| LLMs | Partial | Gemini client available (needs valid Google/Gemini API key); Ollama container with configurable models (default: `qwen2.5:7b`, `nomic-embed-text`); backend uses `OLLAMA_HOST` default. |
| Tests | Missing | `backend/tests` folders are empty. TESTING docs still describe removed auth flows. |

Use this table as the source of truth for what currently runs out-of-the-box.

---

## 2. Project Goals

### Primary Goals
1. **Zero-Config Startup**: New developers can clone and run `docker compose up` to get a fully functional application
2. **Modularity**: Enable/disable services via feature flags to suit specific project needs
3. **Reusability**: Serve as a foundation for ANY Python-based project without rewriting boilerplate code
4. **Best Practices**: Embody industry-standard patterns for code organization, testing, and deployment
5. **Comprehensive Integration**: Pre-configured connections to all major service categories (DBs, queues, LLMs)
6. **Developer Experience**: Excellent DX with hot-reload, type safety, linting, and automated testing
7. **Admin Control**: Runtime management of features through an intuitive Admin UI

### Non-Goals
- This is NOT a framework or library to be installed via pip
- This is NOT opinionated about business logic or domain models
- This does NOT include deployment to cloud providers (AWS/GCP/Azure) - only local Docker

---

## 3. Technology Stack

### Backend
- **Python 3.11**: Core language
- **FastAPI 0.109+**: Web framework
- **Poetry**: Dependency management
- **Pydantic v2**: Data validation and settings management
- **SQLAlchemy 2.0**: ORM for PostgreSQL
- **Motor**: Async MongoDB driver
- **Neomodel**: OGM for Neo4j
- **Celery 5.3+**: Distributed task queue
- **Kombu**: RabbitMQ integration

### Frontend
- **React 18**: UI framework
- **TypeScript 5.3+**: Type safety
- **Vite**: Build tool and dev server
- **TailwindCSS 3.4+**: Utility-first CSS
- **TanStack Query v5**: Server state management
- **Axios**: HTTP client
- **React Router v6**: Client-side routing
- **Zod**: Runtime validation

### Databases
- **PostgreSQL 16**: Primary relational database
- **PGVector**: Vector similarity search extension
- **MongoDB 7**: Document database
- **Neo4j 5.15**: Graph database
- **Redis 7**: Cache and Celery broker

### Infrastructure
- **Docker 24+**: Containerization
- **Docker Compose**: Multi-container orchestration
- **Nginx**: Reverse proxy and static file serving
- **RabbitMQ 3.12**: Message broker

### LLM Integration
- **LiteLLM**: Unified API for all LLM providers
- **LangChain**: LLM orchestration framework
- **OpenAI SDK**: ChatGPT integration
- **Anthropic SDK**: Claude integration
- **Google GenAI SDK**: Gemini integration (requires valid GOOGLE_API_KEY or GEMINI_API_KEY)
- **Ollama**: Local LLM integration (Dockerized; configurable models via `OLLAMA_MODELS` env var, defaults: `qwen2.5:7b`, `nomic-embed-text`)

### DevOps & Quality
- **Ruff**: Fast Python linter
- **Black**: Code formatter
- **mypy**: Static type checker
- **pytest**: Testing framework
- **pytest-cov**: Code coverage
- **pre-commit**: Git hooks
- **Alembic**: Database migrations
- **OpenTelemetry**: Observability

---

## 4. Architecture Overview

### System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                         Docker Host                          │
│                                                              │
│  ┌────────────────┐         ┌──────────────────┐           │
│  │  Nginx (80)    │────────▶│  React (Vite)    │           │
│  │  Reverse Proxy │         │  Frontend        │           │
│  └────────┬───────┘         └──────────────────┘           │
│           │                                                  │
│           ▼                                                  │
│  ┌─────────────────────────────────────────┐               │
│  │     FastAPI Backend (8000)              │               │
│  │  ┌────────────────────────────────────┐ │               │
│  │  │  API Layer (Routes)                │ │               │
│  │  ├────────────────────────────────────┤ │               │
│  │  │  Service Layer (Business Logic)    │ │               │
│  │  ├────────────────────────────────────┤ │               │
│  │  │  Repository Layer (Data Access)    │ │               │
│  │  ├────────────────────────────────────┤ │               │
│  │  │  Helper Clients (DB, Queue, LLM)   │ │               │
│  │  └────────────────────────────────────┘ │               │
│  └───────────────┬─────────────────────────┘               │
│                  │                                           │
│                  ├──────────┬──────────┬──────────┬────────┤
│                  ▼          ▼          ▼          ▼        ▼
│         ┌──────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌────────┐
│         │PostgreSQL│ │ MongoDB  │ │ Neo4j  │ │RabbitMQ│ │ Redis  │
│         │  +PGVec  │ │          │ │        │ │        │ │        │
│         └──────────┘ └──────────┘ └────────┘ └────────┘ └────────┘
│                  │                                           │
│                  └───────────────┬───────────────────────────┘
│                                  ▼                            │
│                         ┌─────────────────┐                  │
│                         │ Celery Workers  │                  │
│                         │  (Background)   │                  │
│                         └─────────────────┘                  │
│                                                              │
│  External Services (via API):                               │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐   │
│  │ OpenAI   │  │ Anthropic│  │  Google  │  │  Ollama  │   │
│  │ ChatGPT  │  │  Claude  │  │  Gemini  │  │  (Local) │   │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘   │
└─────────────────────────────────────────────────────────────┘
```

### Application Layers

1. **Presentation Layer**: React frontend with routing, state management, and UI components
2. **API Gateway**: Nginx reverse proxy handling routing and SSL termination
3. **Application Layer**: FastAPI routes with request/response handling
4. **Service Layer**: Business logic and orchestration
5. **Repository Layer**: Data access patterns and abstractions
6. **Integration Layer**: Helper clients for external services
7. **Data Layer**: Multiple database systems
8. **Background Processing**: Celery workers for async tasks

---

## 5. Project Structure

```
python-project-template/
├── backend/
│   ├── alembic/
│   │   ├── env.py
│   │   └── versions/2025_12_28_0116-e33669fc7a6c_initial_migration.py
│   ├── app/
│   │   ├── main.py                    # FastAPI app entry point
│   │   ├── config/settings.py         # Pydantic settings + feature flags
│   │   ├── core/{decorators.py,logging.py,telemetry.py}
│   │   ├── helpers/
│   │   │   ├── postgres.py            # PostgreSQL helper
│   │   │   ├── redis_helper.py        # Redis helper
│   │   │   ├── mongodb.py             # MongoDB helper
│   │   │   ├── neo4j_helper.py        # Neo4j helper
│   │   │   ├── rabbitmq.py            # RabbitMQ helper
│   │   │   ├── celery_app.py          # Celery configuration
│   │   │   └── llm/                   # LLM client stubs (OpenAI, Anthropic, Gemini, LangChain, Ollama, LiteLLM)
│   │   ├── models/
│   │   │   ├── postgres/{base.py,feature_flag.py}
│   │   │   ├── mongodb/document.py
│   │   │   └── neo4j/graph_node.py
│   │   ├── repositories/{document_repository.py,graph_repository.py}
│   │   ├── schemas/{document.py,feature_flag.py,graph.py,health.py}
│   │   ├── services/{document_service.py,feature_flag_service.py,graph_service.py}
│   │   ├── api/v1/{documents.py,graph.py,router.py}
│   │   └── tasks/{example_tasks.py,llm_tasks.py}
│   ├── Dockerfile, Dockerfile.celery, pyproject.toml, poetry.lock, alembic.ini, .env
├── frontend/
│   ├── src/ (AuthContext/login/admin pages remain but require backend auth endpoints that were removed)
│   ├── Dockerfile, package.json, package-lock.json, vite/tailwind configs
├── nginx/                            # Reverse proxy container
├── docker-compose.yml (+ dev/prod/minimal overrides)
├── features.env (+ minimal/fullstack/microservices presets)
├── scripts/{generate-profiles.sh,init-project.sh}
├── Makefile
├── README.md, TESTING.md, TESTING_GUIDE.md, TECHNICAL_DESIGN.md
└── LICENSE
```

---

## 6. Component Specifications

### 6.1 Backend (FastAPI)

#### 6.1.1 FastAPI Application (`backend/app/main.py`)

```python
"""
Main FastAPI application entry point.

Features:
- CORS middleware for frontend integration
- Exception handlers for standardized error responses
- Health check endpoints
- OpenTelemetry instrumentation
- API versioning (v1)
- Automatic OpenAPI documentation
"""

Key responsibilities:
- Initialize FastAPI app with metadata
- Configure middleware (CORS, logging, compression)
- Register API routers
- Setup startup/shutdown events for DB connections
- Configure OpenTelemetry tracing
```

#### 6.1.2 Configuration (`backend/app/config/settings.py`)

```python
"""
Pydantic Settings for type-safe configuration.

Features:
- Environment variable loading from .env
- Validation of required settings
- Separate configs for dev/test/prod
- Database connection strings
- API keys for external services
- Feature flags
"""

Settings classes:
- DatabaseSettings: All DB connection strings
- RedisSettings: Redis configuration
- CelerySettings: Task queue configuration
- LLMSettings: API keys for LLM providers
- AuthSettings: JWT secrets, token expiry
- AppSettings: Main settings aggregator
```

#### 6.1.3 Authentication (removed)

Authentication and user management were intentionally removed from the backend. There is no `auth.py`, JWT handling, or `/auth` routes in the current codebase, and the Postgres schema only contains `feature_flags`. Frontend `AuthContext`, login, and admin guard components remain in the UI but will not function until a replacement auth layer is implemented.

### 6.2 Database Helpers

#### 6.2.1 PostgreSQL Helper (`backend/app/helpers/postgres.py`)

```python
"""
PostgreSQL + PGVector helper with async SQLAlchemy.

Features:
- Async session factory
- Connection pooling
- Context manager for sessions
- Vector similarity search using PGVector
- Raw SQL execution support
- Transaction management

Usage:
    async with get_postgres_session() as session:
        result = await session.execute(query)

    # Vector search
    similar = await vector_search(
        embedding=[0.1, 0.2, ...],
        limit=10,
        table="documents"
    )
"""
```

#### 6.2.2 MongoDB Helper (`backend/app/helpers/mongodb.py`)

```python
"""
Async MongoDB helper using Motor.

Features:
- Connection pool management
- Database and collection getters
- CRUD operations wrapper
- Aggregation pipeline helpers
- Full-text search support
- GridFS for file storage

Usage:
    db = get_mongodb()
    collection = db.get_collection("users")
    await collection.insert_one({"name": "John"})
"""
```

#### 6.2.3 Neo4j Helper (`backend/app/helpers/neo4j_helper.py`)

```python
"""
Neo4j graph database helper using Neomodel.

Features:
- Async driver support
- Cypher query execution
- Relationship traversal helpers
- Graph algorithm wrappers (shortest path, etc.)
- Batch operations

Usage:
    from app.models.neo4j import Person, Follows

    person = await Person.nodes.get(name="Alice")
    followers = await person.followers.all()
"""
```

#### 6.2.4 Redis Helper (`backend/app/helpers/redis_helper.py`)

```python
"""
Redis helper for caching and session storage.

Features:
- Async redis client (aioredis)
- Key-value operations
- Pub/sub support
- TTL management
- Cache decorators

Usage:
    @cache(ttl=300)
    async def expensive_operation():
        return result

    await redis_set("key", "value", ttl=60)
    value = await redis_get("key")
"""
```

### 6.3 Message Queue & Background Tasks

#### 6.3.1 Celery Configuration (`backend/app/helpers/celery_app.py`)

```python
"""
Celery app configuration with RabbitMQ broker.

Features:
- Task routing by queue
- Result backend (Redis)
- Task retries and error handling
- Scheduled periodic tasks (Celery Beat)
- Task monitoring

Queues:
- default: General purpose tasks
- llm: LLM-related tasks (rate limited)
- heavy: CPU/memory intensive tasks
"""
```

#### 6.3.2 RabbitMQ Helper (`backend/app/helpers/rabbitmq.py`)

```python
"""
Direct RabbitMQ interaction (for non-Celery use cases).

Features:
- Async producer/consumer
- Exchange and queue management
- Message acknowledgment
- Dead letter queue setup
- Priority queues

Usage:
    await publish_message(
        exchange="events",
        routing_key="user.created",
        message={"user_id": 123}
    )
"""
```

### 6.4 LLM Integration Helpers

#### 6.4.1 LiteLLM Client (`backend/app/helpers/llm/litellm_client.py`)

```python
"""
Unified LLM client using LiteLLM.

Features:
- Single interface for all providers
- Automatic retries and fallbacks
- Cost tracking
- Streaming support
- Function calling

Supported providers:
- OpenAI (gpt-4, gpt-3.5-turbo)
- Anthropic (claude-3-opus, claude-3-sonnet)
- Google (gemini-flash-latest)
- Ollama (local models)

Usage:
    response = await llm_client.complete(
        model="gpt-4",
        messages=[{"role": "user", "content": "Hello"}]
    )
"""
```

#### 6.4.2 LangChain Client (`backend/app/helpers/llm/langchain_client.py`)

```python
"""
LangChain integration for complex LLM workflows.

Features:
- Chain composition
- Vector store integration (PGVector)
- Document loaders
- Agents and tools
- Memory management
- RAG (Retrieval Augmented Generation) pipeline

Usage:
    from langchain import VectorStoreRetriever

    retriever = get_pgvector_retriever()
    chain = get_rag_chain(retriever)
    answer = await chain.arun("What is...?")
"""
```

#### 6.4.3 Provider-Specific Clients

```python
"""
Direct client implementations for each provider.

Use cases:
- Provider-specific features not in LiteLLM
- Beta API access
- Fine-tuned models
- Advanced streaming

Files:
- openai_client.py: OpenAI SDK wrapper
- anthropic_client.py: Anthropic SDK wrapper
- gemini_client.py: Google GenAI wrapper
- ollama_client.py: Ollama local models
"""
```

### 6.5 Frontend (React + TypeScript)

#### 6.5.1 API Client (`frontend/src/api/client.ts`)

```typescript
/**
 * Axios client with interceptors for auth and error handling.
 *
 * Features:
 * - Automatic token attachment
 * - Token refresh on 401
 * - Request/response logging
 * - Error normalization
 * - Retry logic
 */

export const apiClient = axios.create({
  baseURL: import.meta.env.VITE_API_URL,
  timeout: 10000,
});
```

#### 6.5.2 React Query Setup

```typescript
/**
 * TanStack Query configuration for server state.
 *
 * Features:
 * - Automatic refetching
 * - Optimistic updates
 * - Cache management
 * - Mutations with rollback
 *
 * Custom hooks:
 * - useUsers()
 * - useDocuments()
 * - useAuth()
 * - useLLMChat()
 */
```

#### 6.5.3 Authentication Context

```typescript
/**
 * Auth context provider with JWT token management.
 *
 * Features:
 * - Login/logout
 * - Token persistence (localStorage)
 * - Protected route component
 * - User profile state
 */
```

---

## 7. Feature Flag System

The template implements a comprehensive **two-tier feature flag system** that allows you to configure which services and features are enabled both at **build-time** (Docker Compose) and **runtime** (application-level).

### 7.1 Design Philosophy

**Build-time vs Runtime:**
- **Build-time flags**: Control which Docker containers are started (saves resources)
- **Runtime flags**: Control which features are active in the application code (dynamic toggling)

**Why two tiers?**
1. **Resource efficiency**: Don't spin up MongoDB if your project doesn't need it
2. **Development flexibility**: Quickly prototype by disabling unused services
3. **Production control**: Enable/disable features without redeploying
4. **Cost optimization**: Pay only for services you use in cloud deployments

### 7.2 Build-Time Feature Flags

#### 7.2.1 Configuration File: `features.env`

```bash
# features.env - Build-time service configuration
# Set to "true" to enable, "false" to disable
# Changes require: docker compose down && docker compose up

# Core Services (recommended to keep enabled)
ENABLE_BACKEND=true
ENABLE_REDIS=true          # Required for Celery

# Frontend
ENABLE_FRONTEND=true
ENABLE_NGINX=true          # Set false if frontend disabled

# Databases
ENABLE_POSTGRES=true
ENABLE_PGVECTOR=true       # Requires ENABLE_POSTGRES=true
ENABLE_MONGODB=false
ENABLE_NEO4J=false

# Message Queue & Background Tasks
ENABLE_RABBITMQ=false
ENABLE_CELERY_WORKER=false # Requires ENABLE_RABBITMQ=true
ENABLE_CELERY_BEAT=false   # Requires ENABLE_CELERY_WORKER=true

# LLM Providers (doesn't affect containers, just dependencies)
ENABLE_LLM_OPENAI=true
ENABLE_LLM_ANTHROPIC=true
ENABLE_LLM_GOOGLE=false
ENABLE_LLM_OLLAMA=false
ENABLE_LLM_LITELLM=true
ENABLE_LLM_LANGCHAIN=false
```

#### 7.2.2 Pre-Configured Profiles

The template provides ready-to-use configuration profiles in the `/profiles` directory for common use cases:

| Profile | Use Case | Containers | Dependencies | Size |
|---------|----------|------------|--------------|------|
| `minimal.env` | Simple REST APIs | 3 (Backend, PostgreSQL, Redis) | Base only | ~500MB |
| `fullstack.env` | Web applications | 5 (+ Frontend, Nginx) | Base only | ~1GB |
| `ai-local.env` | Local AI/ML | 4 (+ Ollama w/ models) | Base only | ~5GB |
| `ai-cloud.env` | Cloud AI APIs | 3 | Base + LLM SDKs | ~800MB |
| `data-platform.env` | Multi-database | 5 (+ MongoDB, Neo4j) | Base + DB drivers | ~2GB |
| `async-tasks.env` | Background jobs | 6 (+ RabbitMQ, Celery) | Base + Celery | ~1GB |
| `everything.env` | Full exploration | 11 (all services) | All packages | ~15GB |

**Usage:**
```bash
# Copy desired profile
cp profiles/ai-local.env features.env

# Start services
make dev
```

**Customization:**
Users can copy a profile and modify it to fit their exact needs, combining features from multiple profiles.

#### 7.2.3 Docker Compose Profile System

The `docker-compose.yml` uses Docker Compose **profiles** to conditionally start services:

```yaml
# docker-compose.yml (excerpt)
services:
  postgres:
    image: postgres:16-alpine
    profiles:
      - postgres
    # ... configuration

  mongodb:
    image: mongo:7
    profiles:
      - mongodb
    # ... configuration

  neo4j:
    image: neo4j:5.15
    profiles:
      - neo4j
    # ... configuration

  rabbitmq:
    image: rabbitmq:3.12-management
    profiles:
      - rabbitmq
    # ... configuration

  celery-worker:
    build:
      context: ./backend
      dockerfile: Dockerfile.celery
    profiles:
      - celery
    depends_on:
      - rabbitmq
      - redis
    # ... configuration

  frontend:
    build: ./frontend
    profiles:
      - frontend
    # ... configuration

  nginx:
    build: ./nginx
    profiles:
      - nginx
    depends_on:
      - frontend
      - backend
    # ... configuration
```

#### 7.2.3 Profile Activation Script: `scripts/generate-profiles.sh`

```bash
#!/bin/bash
# scripts/generate-profiles.sh
# Reads features.env and generates docker compose command with appropriate profiles

set -a
source features.env
set +a

PROFILES=""

[[ "$ENABLE_POSTGRES" == "true" ]] && PROFILES="$PROFILES --profile postgres"
[[ "$ENABLE_MONGODB" == "true" ]] && PROFILES="$PROFILES --profile mongodb"
[[ "$ENABLE_NEO4J" == "true" ]] && PROFILES="$PROFILES --profile neo4j"
[[ "$ENABLE_RABBITMQ" == "true" ]] && PROFILES="$PROFILES --profile rabbitmq"
[[ "$ENABLE_CELERY_WORKER" == "true" ]] && PROFILES="$PROFILES --profile celery"
[[ "$ENABLE_FRONTEND" == "true" ]] && PROFILES="$PROFILES --profile frontend"
[[ "$ENABLE_NGINX" == "true" ]] && PROFILES="$PROFILES --profile nginx"

# Core services always enabled (no profile needed)
# - backend
# - redis

echo "$PROFILES"
```

#### 7.2.4 Updated Makefile

```makefile
# Makefile
.PHONY: dev prod configure

configure:
	@echo "Generating Docker Compose profiles from features.env..."
	@chmod +x scripts/generate-profiles.sh

dev: configure
	@PROFILES=$$(./scripts/generate-profiles.sh); \
	docker compose -f docker-compose.yml -f docker-compose.dev.yml $$PROFILES up

prod: configure
	@PROFILES=$$(./scripts/generate-profiles.sh); \
	docker compose -f docker-compose.yml -f docker-compose.prod.yml $$PROFILES up -d

down:
	docker compose --profile '*' down

clean:
	docker compose --profile '*' down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```

**Usage:**
```bash
# 1. Edit features.env to enable/disable services
# 2. Run make dev or make prod
make dev

# Only enabled services will start!
```

### 7.3 Runtime Feature Flags

Runtime flags control **application behavior** without restarting Docker containers. These are stored in the database and managed via the Admin UI.

#### 7.3.1 Feature Flag Model

```python
# backend/app/models/postgres/feature_flag.py
from sqlalchemy import Column, String, Boolean, DateTime, JSON
from sqlalchemy.sql import func
from app.models.postgres.base import Base

class FeatureFlag(Base):
    """Runtime feature flags stored in database."""

    __tablename__ = "feature_flags"

    key = Column(String(100), primary_key=True)
    enabled = Column(Boolean, default=False, nullable=False)
    description = Column(String(500))
    category = Column(String(50))  # 'database', 'llm', 'feature', 'integration'
    metadata = Column(JSON)  # Additional config (API keys, limits, etc.)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

#### 7.3.2 Feature Flag Service

```python
# backend/app/services/feature_flag_service.py
from typing import Any, Dict, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.postgres.feature_flag import FeatureFlag
from functools import lru_cache
import asyncio

class FeatureFlagService:
    """Service for managing runtime feature flags."""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._cache: Dict[str, bool] = {}
        self._cache_ttl = 60  # seconds

    async def is_enabled(self, key: str) -> bool:
        """Check if a feature is enabled."""
        # Check cache first
        if key in self._cache:
            return self._cache[key]

        # Query database
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        flag = result.scalar_one_or_none()

        enabled = flag.enabled if flag else False
        self._cache[key] = enabled

        # Auto-expire cache after TTL
        asyncio.create_task(self._expire_cache(key))

        return enabled

    async def _expire_cache(self, key: str):
        """Expire cache entry after TTL."""
        await asyncio.sleep(self._cache_ttl)
        self._cache.pop(key, None)

    async def set_flag(self, key: str, enabled: bool, metadata: Optional[Dict[str, Any]] = None):
        """Set or update a feature flag."""
        result = await self.session.execute(
            select(FeatureFlag).where(FeatureFlag.key == key)
        )
        flag = result.scalar_one_or_none()

        if flag:
            flag.enabled = enabled
            if metadata:
                flag.metadata = metadata
        else:
            flag = FeatureFlag(key=key, enabled=enabled, metadata=metadata)
            self.session.add(flag)

        await self.session.commit()

        # Invalidate cache
        self._cache.pop(key, None)

    async def get_all_flags(self) -> list[FeatureFlag]:
        """Get all feature flags."""
        result = await self.session.execute(select(FeatureFlag))
        return result.scalars().all()
```

#### 7.3.3 Feature Flag Decorator

```python
# backend/app/core/decorators.py
from functools import wraps
from fastapi import HTTPException, Depends
from app.services.feature_flag_service import FeatureFlagService
from app.api.deps import get_feature_flag_service

def require_feature(feature_key: str):
    """Decorator to protect endpoints behind feature flags."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Extract feature flag service from kwargs or use dependency
            flag_service = kwargs.get('flag_service')
            if not flag_service:
                # If not in kwargs, this should be used with Depends
                raise ValueError("Feature flag service not provided")

            if not await flag_service.is_enabled(feature_key):
                raise HTTPException(
                    status_code=503,
                    detail=f"Feature '{feature_key}' is currently disabled"
                )

            return await func(*args, **kwargs)
        return wrapper
    return decorator

# Usage example:
# @router.get("/documents")
# @require_feature("feature.vector_search")
# async def search_documents(
#     query: str,
#     flag_service: FeatureFlagService = Depends(get_feature_flag_service)
# ):
#     ...
```

#### 7.3.4 Conditional Service Initialization

```python
# backend/app/main.py (excerpt)
from app.config.settings import settings
from app.helpers import postgres, mongodb, neo4j_helper, redis_helper

@app.on_event("startup")
async def startup_event():
    """Initialize services based on feature flags."""

    # Always initialize core services
    await postgres.initialize()
    await redis_helper.initialize()

    # Conditional initialization based on build-time flags
    if settings.enable_mongodb:
        await mongodb.initialize()

    if settings.enable_neo4j:
        await neo4j_helper.initialize()

    if settings.enable_rabbitmq:
        from app.helpers.rabbitmq import rabbitmq_helper
        await rabbitmq_helper.initialize()

    # Initialize feature flags from database
    async with postgres.get_session() as session:
        from app.services.feature_flag_service import FeatureFlagService
        flag_service = FeatureFlagService(session)

        # Set default flags if not exist
        await flag_service.set_flag("feature.vector_search", True, {
            "requires": ["postgres", "pgvector"]
        })
        await flag_service.set_flag("feature.graph_queries",
            enabled=settings.enable_neo4j,
            metadata={"requires": ["neo4j"]}
        )
        await flag_service.set_flag("feature.llm_chat", True, {
            "providers": ["openai", "anthropic", "gemini", "ollama"]
        })
```

#### 7.3.5 Environment-Based Settings

```python
# backend/app/config/settings.py (updated)
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    # Build-time feature flags (from features.env)
    enable_postgres: bool = True
    enable_pgvector: bool = True
    enable_mongodb: bool = False
    enable_neo4j: bool = False
    enable_rabbitmq: bool = False
    enable_celery_worker: bool = False
    enable_frontend: bool = True

    # LLM providers
    enable_llm_openai: bool = True
    enable_llm_anthropic: bool = True
    enable_llm_google: bool = False
    enable_llm_ollama: bool = False
    enable_llm_litellm: bool = True
    enable_llm_langchain: bool = False

    # ... rest of settings
```

### 7.4 Feature Flag Categories

| Category | Examples | Controlled By |
|----------|----------|---------------|
| **Core Services** | Backend, Redis | Build-time (always on) |
| **Databases** | PostgreSQL, MongoDB, Neo4j | Build-time + Runtime |
| **Message Queue** | RabbitMQ, Celery | Build-time |
| **Frontend** | React app, Nginx | Build-time |
| **LLM Providers** | OpenAI, Claude, Gemini | Runtime (via Admin UI) |
| **Features** | Vector search, Graph queries, RAG | Runtime (via Admin UI) |
| **Integrations** | Payment gateways, Email service | Runtime (via Admin UI) |

### 7.5 Default Feature Configurations

The template ships with sensible defaults optimized for common use cases:

**Minimal Setup** (API-only backend):
```bash
ENABLE_BACKEND=true
ENABLE_REDIS=true
ENABLE_POSTGRES=true
ENABLE_FRONTEND=false
ENABLE_NGINX=false
# All others: false
```

**Full-Stack Setup** (Default):
```bash
ENABLE_BACKEND=true
ENABLE_REDIS=true
ENABLE_POSTGRES=true
ENABLE_PGVECTOR=true
ENABLE_FRONTEND=true
ENABLE_NGINX=true
ENABLE_LLM_OPENAI=true
ENABLE_LLM_LITELLM=true
# Others: false
```

**Microservices Setup** (All features):
```bash
# Everything enabled
ENABLE_*=true
```

---

## 8. Admin UI

> Status: frontend pages exist (login/dashboard/admin), but backend admin routes and authentication are currently absent. Treat this section as future intent rather than current behavior.

The Admin UI provides a **web-based interface** for managing feature flags, monitoring services, and configuring the application at runtime. It's designed for administrators to control the system without touching code or environment files.

### 8.1 Admin UI Architecture

```
┌─────────────────────────────────────────────────┐
│           Admin UI (React Dashboard)            │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  Feature     │  │   Service    │            │
│  │  Flags       │  │   Health     │            │
│  └──────────────┘  └──────────────┘            │
│                                                  │
│  ┌──────────────┐  ┌──────────────┐            │
│  │  User        │  │   System     │            │
│  │  Management  │  │   Logs       │            │
│  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────┘
                      │
                      ▼
            ┌──────────────────┐
            │  Admin API       │
            │  (FastAPI)       │
            └──────────────────┘
                      │
        ┌─────────────┼─────────────┐
        ▼             ▼             ▼
  ┌──────────┐  ┌──────────┐  ┌──────────┐
  │Feature   │  │ User DB  │  │ Service  │
  │Flags DB  │  │          │  │ Health   │
  └──────────┘  └──────────┘  └──────────┘
```

### 8.2 Admin UI Features

#### 8.2.1 Feature Flag Management

**Dashboard View:**
- List all feature flags by category (Database, LLM, Features, Integrations)
- Toggle switches for quick enable/disable
- Visual indicators (green=enabled, red=disabled, yellow=partially configured)
- Search and filter flags
- Bulk operations (enable/disable multiple flags)

**Flag Detail View:**
- Flag name and description
- Current status (enabled/disabled)
- Metadata configuration (JSON editor)
- Dependencies (shows which services this flag requires)
- Usage statistics (how many requests use this feature)
- History (when flag was toggled, by whom)

#### 8.2.2 Service Health Dashboard

**Real-time monitoring:**
- Service status indicators (PostgreSQL, MongoDB, Neo4j, Redis, RabbitMQ)
- Connection status (connected, disconnected, error)
- Latency metrics (response time)
- Resource usage (connections, memory)
- Error rates

**Actions:**
- Restart service (if Docker socket exposed)
- View logs
- Run health checks manually

#### 8.2.3 User Management

**Features:**
- List all users
- Create/edit/delete users
- Assign roles (admin, user, readonly)
- View user activity logs
- Password reset

#### 8.2.4 System Configuration

**Settings:**
- API rate limits
- CORS origins
- JWT token expiry
- Log levels
- Cache TTL settings
- Email configuration
- LLM provider API keys (masked)

### 8.3 Admin UI Implementation

#### 8.3.1 Backend API Routes

```python
# backend/app/api/v1/admin/feature_flags.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db, get_current_admin_user
from app.services.feature_flag_service import FeatureFlagService
from app.schemas.feature_flag import FeatureFlagList, FeatureFlagUpdate

router = APIRouter(prefix="/admin/feature-flags", tags=["admin"])

@router.get("/", response_model=FeatureFlagList)
async def list_feature_flags(
    category: Optional[str] = None,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """List all feature flags (admin only)."""
    service = FeatureFlagService(session)
    flags = await service.get_all_flags()

    if category:
        flags = [f for f in flags if f.category == category]

    return {"flags": flags}

@router.patch("/{flag_key}", response_model=FeatureFlag)
async def update_feature_flag(
    flag_key: str,
    update: FeatureFlagUpdate,
    session: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin_user)
):
    """Update a feature flag (admin only)."""
    service = FeatureFlagService(session)

    await service.set_flag(
        key=flag_key,
        enabled=update.enabled,
        metadata=update.metadata
    )

    # Log the change
    from app.services.audit_log_service import AuditLogService
    audit = AuditLogService(session)
    await audit.log_action(
        user_id=admin.id,
        action="feature_flag_updated",
        resource=flag_key,
        details={"enabled": update.enabled}
    )

    return await service.get_flag(flag_key)
```

```python
# backend/app/api/v1/admin/health.py
from fastapi import APIRouter, Depends
from app.api.deps import get_current_admin_user
from app.helpers import postgres, mongodb, neo4j_helper, redis_helper
from app.config.settings import settings

router = APIRouter(prefix="/admin/health", tags=["admin"])

@router.get("/")
async def get_system_health(
    admin: User = Depends(get_current_admin_user)
):
    """Get health status of all services (admin only)."""
    health = {
        "postgres": await check_postgres_health(),
        "redis": await check_redis_health(),
    }

    if settings.enable_mongodb:
        health["mongodb"] = await check_mongodb_health()

    if settings.enable_neo4j:
        health["neo4j"] = await check_neo4j_health()

    if settings.enable_rabbitmq:
        health["rabbitmq"] = await check_rabbitmq_health()

    return health

async def check_postgres_health():
    """Check PostgreSQL health."""
    try:
        async with postgres.get_session() as session:
            result = await session.execute(text("SELECT 1"))
            latency = # measure time
        return {
            "status": "healthy",
            "latency_ms": latency,
            "connections": # get connection count
        }
    except Exception as e:
        return {"status": "unhealthy", "error": str(e)}
```

#### 8.3.2 Frontend Admin Pages

```typescript
// frontend/src/pages/admin/FeatureFlags.tsx
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import { adminApi } from '@/api/admin';

export function FeatureFlagsPage() {
  const queryClient = useQueryClient();

  const { data: flags, isLoading } = useQuery({
    queryKey: ['admin', 'feature-flags'],
    queryFn: adminApi.getFeatureFlags,
  });

  const toggleMutation = useMutation({
    mutationFn: ({ key, enabled }: { key: string; enabled: boolean }) =>
      adminApi.updateFeatureFlag(key, { enabled }),
    onSuccess: () => {
      queryClient.invalidateQueries(['admin', 'feature-flags']);
    },
  });

  const flagsByCategory = groupBy(flags?.flags || [], 'category');

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Feature Flags</h1>

      {Object.entries(flagsByCategory).map(([category, categoryFlags]) => (
        <div key={category} className="mb-8">
          <h2 className="text-xl font-semibold mb-4 capitalize">{category}</h2>

          <div className="grid gap-4">
            {categoryFlags.map((flag) => (
              <div
                key={flag.key}
                className="border rounded-lg p-4 flex items-center justify-between"
              >
                <div className="flex-1">
                  <div className="flex items-center gap-3">
                    <h3 className="font-medium">{flag.key}</h3>
                    <Badge variant={flag.enabled ? 'success' : 'secondary'}>
                      {flag.enabled ? 'Enabled' : 'Disabled'}
                    </Badge>
                  </div>
                  <p className="text-sm text-gray-600 mt-1">
                    {flag.description}
                  </p>
                  {flag.metadata?.requires && (
                    <div className="mt-2">
                      <span className="text-xs text-gray-500">Requires:</span>
                      <span className="text-xs ml-2">
                        {flag.metadata.requires.join(', ')}
                      </span>
                    </div>
                  )}
                </div>

                <Switch
                  checked={flag.enabled}
                  onCheckedChange={(enabled) =>
                    toggleMutation.mutate({ key: flag.key, enabled })
                  }
                  disabled={toggleMutation.isLoading}
                />
              </div>
            ))}
          </div>
        </div>
      ))}
    </div>
  );
}
```

```typescript
// frontend/src/pages/admin/ServiceHealth.tsx
import { useQuery } from '@tanstack/react-query';
import { CheckCircle, XCircle, AlertCircle } from 'lucide-react';
import { adminApi } from '@/api/admin';

export function ServiceHealthPage() {
  const { data: health, isLoading } = useQuery({
    queryKey: ['admin', 'health'],
    queryFn: adminApi.getSystemHealth,
    refetchInterval: 5000, // Poll every 5 seconds
  });

  const getStatusIcon = (status: string) => {
    switch (status) {
      case 'healthy':
        return <CheckCircle className="text-green-500" />;
      case 'unhealthy':
        return <XCircle className="text-red-500" />;
      default:
        return <AlertCircle className="text-yellow-500" />;
    }
  };

  return (
    <div className="p-6">
      <h1 className="text-3xl font-bold mb-6">Service Health</h1>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
        {Object.entries(health || {}).map(([service, status]) => (
          <div
            key={service}
            className="border rounded-lg p-6 shadow-sm"
          >
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-lg font-semibold capitalize">{service}</h3>
              {getStatusIcon(status.status)}
            </div>

            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span className="text-gray-600">Status:</span>
                <span className="font-medium">{status.status}</span>
              </div>

              {status.latency_ms && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Latency:</span>
                  <span className="font-medium">{status.latency_ms}ms</span>
                </div>
              )}

              {status.connections && (
                <div className="flex justify-between">
                  <span className="text-gray-600">Connections:</span>
                  <span className="font-medium">{status.connections}</span>
                </div>
              )}

              {status.error && (
                <div className="mt-3 text-red-600 text-xs">
                  Error: {status.error}
                </div>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
```

#### 8.3.3 Admin UI Routes

```typescript
// frontend/src/App.tsx (excerpt)
import { FeatureFlagsPage } from '@/pages/admin/FeatureFlags';
import { ServiceHealthPage } from '@/pages/admin/ServiceHealth';
import { UserManagementPage } from '@/pages/admin/UserManagement';
import { SystemConfigPage } from '@/pages/admin/SystemConfig';
import { AdminLayout } from '@/layouts/AdminLayout';

function App() {
  return (
    <BrowserRouter>
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<Login />} />

        {/* User routes */}
        <Route element={<ProtectedRoute />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/documents" element={<Documents />} />
        </Route>

        {/* Admin routes */}
        <Route element={<AdminRoute />}>
          <Route path="/admin" element={<AdminLayout />}>
            <Route index element={<Navigate to="/admin/feature-flags" />} />
            <Route path="feature-flags" element={<FeatureFlagsPage />} />
            <Route path="health" element={<ServiceHealthPage />} />
            <Route path="users" element={<UserManagementPage />} />
            <Route path="config" element={<SystemConfigPage />} />
          </Route>
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
```

### 8.4 Admin Authentication

**Role-Based Access Control (RBAC):**

```python
# backend/app/models/postgres/user.py (updated)
from enum import Enum

class UserRole(str, Enum):
    ADMIN = "admin"
    USER = "user"
    READONLY = "readonly"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(Enum(UserRole), default=UserRole.USER)
    is_active = Column(Boolean, default=True)
    # ... other fields
```

```python
# backend/app/api/deps.py (updated)
async def get_current_admin_user(
    current_user: User = Depends(get_current_user)
) -> User:
    """Verify current user is an admin."""
    if current_user.role != UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Not enough permissions. Admin access required."
        )
    return current_user
```

### 8.5 Admin UI Access

**URL:** `http://localhost:3000/admin` (dev) or `https://yourdomain.com/admin` (prod)

**Default Admin Credentials:**
- Email: `admin@example.com`
- Password: `admin` (MUST be changed on first login)

**Security:**
- Admin routes protected by JWT + role check
- All admin actions logged to audit trail
- Rate limiting on admin endpoints
- CSRF protection
- Session timeout (15 minutes)

---

## 9. Docker Configuration

### 9.1 Services Overview

| Service | Image | Port | Purpose |
|---------|-------|------|---------|
| nginx | nginx:alpine | 80, 443 | Reverse proxy |
| backend | python:3.11-slim | 8000 | FastAPI app |
| celery-worker | python:3.11-slim | - | Background tasks |
| celery-beat | python:3.11-slim | - | Periodic tasks |
| frontend | node:20-alpine | 5173 | React dev server |
| postgres | postgres:16-alpine | 5432 | Main database |
| mongodb | mongo:7 | 27017 | Document store |
| neo4j | neo4j:5.15 | 7474, 7687 | Graph database |
| redis | redis:7-alpine | 6379 | Cache & broker |
| rabbitmq | rabbitmq:3.12-management | 5672, 15672 | Message queue |

### 9.2 Docker Compose Structure

**Three compose files:**

1. `docker-compose.yml`: Base configuration (databases, Redis, RabbitMQ)
2. `docker-compose.dev.yml`: Development overrides (hot-reload, exposed ports)
3. `docker-compose.prod.yml`: Production overrides (optimized builds, no dev tools)

**Usage:**
```bash
# Development
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Production
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

### 9.3 Networking

```yaml
networks:
  frontend-network:
    driver: bridge
  backend-network:
    driver: bridge
  db-network:
    driver: bridge

# Separation:
# - Frontend only connects to backend via nginx
# - Backend connects to all databases
# - Databases isolated in db-network
```

### 9.4 Volumes

```yaml
volumes:
  postgres_data:      # PostgreSQL data persistence
  mongodb_data:       # MongoDB data persistence
  neo4j_data:         # Neo4j data persistence
  redis_data:         # Redis data persistence
  rabbitmq_data:      # RabbitMQ data persistence
```

### 9.5 Health Checks

Each service includes health checks:

```yaml
healthcheck:
  test: ["CMD", "curl", "-f", "http://localhost:8000/health"]
  interval: 30s
  timeout: 10s
  retries: 3
  start_period: 40s
```

---

## 10. Service Helper Libraries

### 10.1 Helper Design Principles

1. **Singleton Pattern**: One instance per application lifecycle
2. **Lazy Initialization**: Connect only when needed
3. **Context Managers**: Automatic cleanup of resources
4. **Async/Await**: Non-blocking I/O for all operations
5. **Type Hints**: Full type coverage for IDE support
6. **Error Handling**: Graceful degradation and retries

### 10.2 Connection Management

```python
# backend/app/helpers/base.py
class BaseHelper:
    """Base class for all service helpers."""

    _instance = None
    _initialized = False

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    async def initialize(self):
        """Initialize connection. Called on app startup."""
        pass

    async def close(self):
        """Close connection. Called on app shutdown."""
        pass
```

### 10.3 Dependency Injection

```python
# backend/app/api/deps.py
async def get_postgres_session():
    """FastAPI dependency for DB sessions."""
    async with postgres_helper.get_session() as session:
        yield session

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_postgres_session)
) -> User:
    """Get current authenticated user."""
    payload = decode_jwt(token)
    user = await session.get(User, payload["sub"])
    return user
```

---

## 11. Example Implementations

> Current state: only the MongoDB document API and Neo4j graph API are present (`backend/app/api/v1/documents.py` and `backend/app/api/v1/graph.py`). User management, auth, search, and LLM chat examples below are legacy design notes and are not implemented.

### 11.1 Full CRUD Example: User Management

**Models:**
- `backend/app/models/postgres/user.py`: SQLAlchemy User model
- `backend/app/schemas/user.py`: Pydantic request/response schemas

**Repository:**
- `backend/app/repositories/user_repository.py`: Data access layer

**Service:**
- `backend/app/services/user_service.py`: Business logic

**API:**
- `backend/app/api/v1/users.py`: REST endpoints

**Frontend:**
- `frontend/src/api/users.ts`: API calls
- `frontend/src/components/users/UserList.tsx`: UI component

### 11.2 Vector Search Example

**Use case:** Semantic search over documents

1. Store document embeddings in PostgreSQL with PGVector
2. Generate embeddings using OpenAI or local model
3. Perform similarity search
4. Return ranked results

**Endpoints:**
- `POST /api/v1/documents`: Upload document + generate embedding
- `POST /api/v1/search`: Semantic search query

### 11.3 Graph Relationships Example

**Use case:** Social network graph

1. Store users and relationships in Neo4j
2. Query friend-of-friend relationships
3. Find shortest path between users
4. Recommend connections

**Endpoints:**
- `POST /api/v1/graph/relationships`: Create relationship
- `GET /api/v1/graph/friends/{user_id}`: Get friends list
- `GET /api/v1/graph/suggest/{user_id}`: Get recommendations

### 11.4 Background Task Example

**Use case:** Generate embeddings for uploaded documents

1. User uploads document via API
2. API returns immediately with task ID
3. Celery worker generates embeddings asynchronously
4. Frontend polls task status endpoint
5. Update UI when complete

**Implementation:**
- `backend/app/tasks/llm_tasks.py`: Celery task definition
- `backend/app/api/v1/tasks.py`: Task status endpoint

### 11.5 LLM Chat Example

**Use case:** Conversational AI with context

1. User sends message
2. Retrieve relevant documents (RAG)
3. Generate response using LLM
4. Stream response to frontend
5. Store conversation in MongoDB

**Features:**
- Streaming responses
- Context window management
- Multiple provider support
- Cost tracking

---

## 12. Configuration Management

### 12.1 Environment Variables

**Structure:**
```bash
# .env.example

# App
APP_NAME=python-project-template
APP_ENV=development
APP_DEBUG=true
SECRET_KEY=your-secret-key-here

# Backend
BACKEND_HOST=0.0.0.0
BACKEND_PORT=8000
BACKEND_RELOAD=true

# Frontend
VITE_API_URL=http://localhost:8000/api/v1

# PostgreSQL
POSTGRES_HOST=postgres
POSTGRES_PORT=5432
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_DB=app_db

# MongoDB
MONGODB_HOST=mongodb
MONGODB_PORT=27017
MONGODB_USER=mongo
MONGODB_PASSWORD=mongo
MONGODB_DB=app_db

# Neo4j
NEO4J_HOST=neo4j
NEO4J_PORT=7687
NEO4J_USER=neo4j
NEO4J_PASSWORD=password

# Redis
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# RabbitMQ
RABBITMQ_HOST=rabbitmq
RABBITMQ_PORT=5672
RABBITMQ_USER=guest
RABBITMQ_PASSWORD=guest

# Celery
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0

# OpenAI
OPENAI_API_KEY=your-openai-api-key

# Anthropic
ANTHROPIC_API_KEY=your-anthropic-api-key

# Google
GOOGLE_API_KEY=your-google-api-key

# Ollama
OLLAMA_HOST=http://host.docker.internal:11434
# Comma-separated list of models to auto-pull on startup
OLLAMA_MODELS=qwen2.5:7b,nomic-embed-text

# JWT
JWT_SECRET_KEY=your-jwt-secret
JWT_ALGORITHM=HS256
JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30
JWT_REFRESH_TOKEN_EXPIRE_DAYS=7

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

### 12.2 Pydantic Settings

```python
# backend/app/config/settings.py
from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        case_sensitive=False
    )

    # Auto-populated from .env
    app_name: str
    app_env: str
    postgres_host: str
    postgres_port: int
    # ... etc

    @property
    def database_url(self) -> str:
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

settings = Settings()
```

---

## 13. Development Workflow

### 13.1 Initial Setup

```bash
# 1. Clone repository
git clone https://github.com/yourusername/python-project-template.git
cd python-project-template

# 2. Copy environment variables
cp .env.example .env
# Edit .env with your API keys

# 3. Start all services
make dev

# Alternative without make:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### 13.2 Makefile Commands

```makefile
.PHONY: dev prod test lint format clean

dev:
	docker compose -f docker-compose.yml -f docker-compose.dev.yml up

prod:
	docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

test:
	docker compose exec backend pytest

lint:
	docker compose exec backend ruff check .
	cd frontend && npm run lint

format:
	docker compose exec backend black .
	docker compose exec backend ruff check --fix .
	cd frontend && npm run format

migrate:
	docker compose exec backend alembic upgrade head

migrate-create:
	docker compose exec backend alembic revision --autogenerate -m "$(msg)"

clean:
	docker compose down -v
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
```

### 13.3 Hot Reload

**Backend:**
- FastAPI runs with `--reload` flag in dev mode
- Code changes trigger automatic restart
- Volume mount: `./backend:/app`

**Frontend:**
- Vite dev server with HMR
- Instant updates on save
- Volume mount: `./frontend:/app`

### 13.4 Database Migrations

```bash
# Create migration
make migrate-create msg="add users table"

# Apply migrations
make migrate

# Rollback
docker compose exec backend alembic downgrade -1
```

---

## 14. CI/CD Pipeline

### 14.1 GitHub Actions

**Workflows:**

1. **Backend CI** (`.github/workflows/backend-ci.yml`)
   - Trigger: Push/PR to main
   - Steps:
     - Checkout code
     - Setup Python 3.11
     - Install dependencies with Poetry
     - Run ruff linting
     - Run black formatting check
     - Run mypy type checking
     - Run pytest with coverage
     - Upload coverage to Codecov

2. **Frontend CI** (`.github/workflows/frontend-ci.yml`)
   - Trigger: Push/PR to main
   - Steps:
     - Checkout code
     - Setup Node.js 20
     - Install dependencies
     - Run ESLint
     - Run TypeScript type check
     - Run Vitest tests
     - Build production bundle

3. **Docker Build** (`.github/workflows/docker-build.yml`)
   - Trigger: Push to main, tags
   - Steps:
     - Build backend image
     - Build frontend image
     - Build nginx image
     - Push to Docker Hub / GHCR
     - Tag with version and latest

### 14.2 GitLab CI

**Pipeline** (`.gitlab-ci.yml`):

```yaml
stages:
  - lint
  - test
  - build
  - deploy

lint:backend:
  stage: lint
  image: python:3.11
  script:
    - pip install ruff black mypy
    - ruff check backend/
    - black --check backend/

test:backend:
  stage: test
  services:
    - postgres:16
    - redis:7
  script:
    - cd backend
    - poetry install
    - pytest --cov

build:docker:
  stage: build
  script:
    - docker build -t $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA .
    - docker push $CI_REGISTRY_IMAGE:$CI_COMMIT_SHA
```

### 14.3 Pre-commit Hooks

**`.pre-commit-config.yaml`:**

```yaml
repos:
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix]
      - id: ruff-format

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-all]

  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: trailing-whitespace
      - id: end-of-file-fixer
      - id: check-yaml
      - id: check-added-large-files
```

**Installation:**
```bash
pip install pre-commit
pre-commit install
```

---

## 15. Security Considerations

### 15.1 Authentication & Authorization

- **JWT Tokens**: Short-lived access tokens (30 min), longer refresh tokens (7 days)
- **Password Hashing**: bcrypt with salt rounds
- **HTTPS Only**: Enforce SSL in production
- **CORS**: Whitelist specific origins
- **Rate Limiting**: Implement with slowapi or nginx

### 15.2 Environment Variables

- **Never commit `.env`**: Include in `.gitignore`
- **Provide `.env.example`**: Template without secrets
- **Docker secrets**: Use for production deployments
- **Validation**: Pydantic validates all settings on startup

### 15.3 Database Security

- **Parameterized Queries**: SQLAlchemy ORM prevents SQL injection
- **Connection Pooling**: Limit concurrent connections
- **Network Isolation**: Databases on separate Docker network
- **Backup Strategy**: Regular automated backups

### 15.4 API Security

- **Input Validation**: Pydantic schemas validate all inputs
- **Output Sanitization**: Strip sensitive fields in responses
- **Error Messages**: Don't leak stack traces in production
- **CSRF Protection**: Token-based for state-changing operations

### 15.5 Dependencies

- **Dependency Scanning**: GitHub/GitLab vulnerability alerts
- **Regular Updates**: Automated PRs via Dependabot
- **Lock Files**: `poetry.lock` and `package-lock.json` committed
- **Minimal Images**: Use Alpine-based Docker images

---

## 16. Testing Strategy

> Current state: the `backend/tests` directories are empty and no automated tests run today. The examples below describe intended coverage, but they are not implemented; TESTING.md and TESTING_GUIDE.md still reference the removed auth flows.

### 16.1 Backend Testing

**Structure:**
```
tests/
├── unit/              # Fast, isolated tests
│   ├── test_helpers.py
│   ├── test_services.py
│   └── test_utils.py
├── integration/       # Tests with DB/external services
│   ├── test_repositories.py
│   └── test_api.py
└── e2e/              # Full user flows
    └── test_user_journey.py
```

**Tools:**
- `pytest`: Test runner
- `pytest-asyncio`: Async test support
- `pytest-cov`: Coverage reporting
- `httpx`: Async HTTP client for API tests
- `faker`: Test data generation

**Fixtures:**
```python
# tests/conftest.py
@pytest.fixture
async def test_db():
    """Provide clean test database."""
    engine = create_async_engine(TEST_DATABASE_URL)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield engine
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)

@pytest.fixture
async def client(test_db):
    """Provide test client."""
    async with AsyncClient(app=app, base_url="http://test") as ac:
        yield ac
```

### 16.2 Frontend Testing

**Tools:**
- `Vitest`: Fast test runner
- `Testing Library`: User-centric testing
- `MSW`: API mocking
- `Playwright`: E2E tests

**Example:**
```typescript
// src/components/__tests__/UserList.test.tsx
import { render, screen } from '@testing-library/react';
import { UserList } from '../UserList';

test('renders user list', async () => {
  render(<UserList />);
  expect(await screen.findByText('Users')).toBeInTheDocument();
});
```

### 16.3 Coverage Goals

- **Backend**: Minimum 80% coverage
- **Frontend**: Minimum 70% coverage
- **Critical Paths**: 100% coverage (auth, payments, etc.)

---

## 17. Deployment Guide

### 17.1 Local Development

```bash
# Start everything
docker compose -f docker-compose.yml -f docker-compose.dev.yml up

# Access services
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs
- RabbitMQ UI: http://localhost:15672
- Neo4j Browser: http://localhost:7474
```

### 17.2 Production Deployment

**Prerequisites:**
- Docker Engine 24+
- Docker Compose 2.0+
- Domain name with DNS configured
- SSL certificates (Let's Encrypt)

**Steps:**

1. **Configure Environment**
```bash
cp .env.example .env
# Edit .env with production values
# - Set APP_ENV=production
# - Set APP_DEBUG=false
# - Use strong passwords
# - Configure real API keys
```

2. **Build Images**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml build
```

3. **Run Migrations**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml run backend alembic upgrade head
```

4. **Start Services**
```bash
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

5. **Verify Health**
```bash
curl http://localhost/api/v1/health
```

### 17.3 Cloud Deployment

**AWS ECS:**
- Use Fargate for serverless containers
- RDS for PostgreSQL
- DocumentDB for MongoDB
- ElastiCache for Redis
- Amazon MQ for RabbitMQ

**Google Cloud Run:**
- Deploy each service separately
- Cloud SQL for PostgreSQL
- Firestore for MongoDB alternative
- Memorystore for Redis
- Cloud Tasks for background jobs

**DigitalOcean App Platform:**
- Use managed databases
- Deploy from GitHub
- Auto-scaling enabled

---

## 18. Future Extensibility

### 18.1 Adding New Features

**To add a new feature (e.g., "payments"):**

1. **Backend:**
   - Create `models/postgres/payment.py`
   - Create `schemas/payment.py`
   - Create `repositories/payment_repository.py`
   - Create `services/payment_service.py`
   - Create `api/v1/payments.py`
   - Register router in `api/v1/router.py`

2. **Frontend:**
   - Create `api/payments.ts`
   - Create `components/payments/`
   - Add routes to `App.tsx`

### 18.2 Adding New Database

**To add a new database (e.g., Elasticsearch):**

1. Add service to `docker-compose.yml`
2. Create `helpers/elasticsearch.py`
3. Add connection string to `config/settings.py`
4. Create repository layer
5. Update health checks

### 18.3 Adding New LLM Provider

**To add a new LLM provider (e.g., Cohere):**

1. Add SDK to `pyproject.toml`
2. Create `helpers/llm/cohere_client.py`
3. Add API key to `.env.example`
4. Update `LLMSettings` in config
5. Add to LiteLLM configuration

### 18.4 Customization Points

**Designed for easy customization:**
- Replace authentication system
- Swap out frontend framework
- Add GraphQL layer
- Integrate monitoring (Prometheus, Grafana)
- Add API gateway (Kong, Traefik)
- Implement event sourcing
- Add search (Elasticsearch, Typesense)

---

## Appendix A: Technology Decisions

### Why FastAPI?
- Automatic API documentation
- Native async/await support
- Pydantic integration
- High performance
- Type hints everywhere

### Why Poetry?
- Deterministic dependency resolution
- Lock file for reproducible builds
- Better than pip + requirements.txt
- Active development

### Why Pydantic Settings?
- Type-safe configuration
- Automatic validation
- IDE autocomplete
- Environment variable parsing

### Why PostgreSQL + PGVector?
- Single database for relational + vector data
- ACID compliance
- Mature ecosystem
- pgvector extension for embeddings

### Why MongoDB?
- Flexible schema for unstructured data
- Horizontal scalability
- Rich query language
- GridFS for files

### Why Neo4j?
- Purpose-built for graphs
- Cypher query language
- ACID transactions
- Graph algorithms library

### Why RabbitMQ + Celery?
- Industry standard
- Reliable message delivery
- Dead letter queues
- Easy to monitor

### Why React Query?
- Declarative data fetching
- Automatic caching
- Optimistic updates
- DevTools

### Why LiteLLM?
- Single API for all providers
- Cost tracking
- Automatic retries
- Fallbacks

---

## Appendix B: File Templates

### Backend Model Template
```python
# backend/app/models/postgres/example.py
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from app.models.postgres.base import Base

class Example(Base):
    __tablename__ = "examples"

    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
```

### Schema Template
```python
# backend/app/schemas/example.py
from pydantic import BaseModel, Field
from datetime import datetime

class ExampleBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)

class ExampleCreate(ExampleBase):
    pass

class ExampleUpdate(ExampleBase):
    name: str | None = None

class ExampleInDB(ExampleBase):
    id: int
    created_at: datetime
    updated_at: datetime | None

    model_config = {"from_attributes": True}
```

### Repository Template
```python
# backend/app/repositories/example_repository.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.postgres.example import Example
from app.schemas.example import ExampleCreate, ExampleUpdate

class ExampleRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get(self, id: int) -> Example | None:
        result = await self.session.execute(
            select(Example).where(Example.id == id)
        )
        return result.scalar_one_or_none()

    async def create(self, data: ExampleCreate) -> Example:
        obj = Example(**data.model_dump())
        self.session.add(obj)
        await self.session.commit()
        await self.session.refresh(obj)
        return obj
```

### API Route Template
```python
# backend/app/api/v1/examples.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db
from app.schemas.example import ExampleCreate, ExampleInDB
from app.repositories.example_repository import ExampleRepository

router = APIRouter(prefix="/examples", tags=["examples"])

@router.post("/", response_model=ExampleInDB)
async def create_example(
    data: ExampleCreate,
    session: AsyncSession = Depends(get_db)
):
    repo = ExampleRepository(session)
    return await repo.create(data)
```

---

## Appendix C: Useful Commands

### Docker Commands
```bash
# View logs
docker compose logs -f backend

# Execute command in container
docker compose exec backend bash

# Restart specific service
docker compose restart backend

# Remove all volumes
docker compose down -v
```

### Database Commands
```bash
# PostgreSQL shell
docker compose exec postgres psql -U postgres -d app_db

# MongoDB shell
docker compose exec mongodb mongosh -u mongo -p mongo

# Neo4j Cypher shell
docker compose exec neo4j cypher-shell -u neo4j -p password

# Redis CLI
docker compose exec redis redis-cli
```

### Backend Commands
```bash
# Install new package
docker compose exec backend poetry add fastapi-users

# Run tests
docker compose exec backend pytest -v

# Format code
docker compose exec backend black .

# Type check
docker compose exec backend mypy .
```

### Frontend Commands
```bash
# Install package
docker compose exec frontend npm install axios

# Build production
docker compose exec frontend npm run build

# Run tests
docker compose exec frontend npm test
```

---

## Conclusion

This technical design provides a comprehensive blueprint for a production-ready Python full-stack project template. The architecture balances:

- **Developer Experience**: Fast setup, hot reload, type safety
- **Production Readiness**: Monitoring, logging, migrations
- **Flexibility**: Easy to customize and extend
- **Best Practices**: Industry-standard patterns and tools

**Next Steps:**
1. Review this document
2. Provide feedback and requested changes
3. Iterate until approved
4. Begin implementation

---

**Document Status:** Draft v2.0
**Ready for Review:** Yes
**Estimated Implementation Time:** Not applicable per user request

---

## Summary of Changes in v2.0

### 1. Feature Flag System (Section 7)
- **Build-time flags**: Control which Docker services start via `features.env` and Docker Compose profiles
- **Runtime flags**: Dynamic feature toggling stored in database, managed via Admin UI
- **Configuration presets**: Minimal, Full-stack, and Microservices templates
- **Smart initialization**: Services only start when enabled, saving resources

### 2. Admin UI (Section 8)
- **Feature Flag Management**: Web dashboard to enable/disable features without code changes
- **Service Health Monitoring**: Real-time status of all databases and services
- **User Management**: Admin interface for user roles and permissions
- **System Configuration**: Runtime configuration of API limits, CORS, JWT settings, etc.
- **Audit Trail**: All admin actions logged for security compliance
- **RBAC**: Role-based access control (Admin, User, Readonly)

### 3. Updated Project Structure
- New `features.env` files for service configuration
- `scripts/generate-profiles.sh` for Docker Compose profile management
- Admin-specific backend routes in `backend/app/api/v1/admin/`
- Admin-specific frontend pages in `frontend/src/pages/admin/`
- Feature flag models, services, and schemas
- Audit log system for tracking changes

### Key Benefits
✅ **Modularity**: Only use what you need (don't need MongoDB? Just disable it!)
✅ **Cost Efficiency**: Save resources by not running unused services
✅ **Production Control**: Toggle features without redeployment
✅ **Easy Onboarding**: Presets for common use cases (API-only, full-stack, etc.)
✅ **Admin Control**: Non-technical admins can manage features via UI
