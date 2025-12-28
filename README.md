# 🚀 Python Full-Stack Project Template

<div align="center">

**A production-ready, batteries-included template for building modern full-stack applications**

[![Python 3.11+](https://img.shields.io/badge/python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.109+-00a393.svg)](https://fastapi.tiangolo.com)
[![React 18](https://img.shields.io/badge/React-18-61dafb.svg)](https://react.dev)
[![TypeScript](https://img.shields.io/badge/TypeScript-5.3+-3178c6.svg)](https://www.typescriptlang.org)
[![Docker](https://img.shields.io/badge/Docker-24+-2496ed.svg)](https://www.docker.com)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

*Clone, configure, and deploy in minutes. Not hours.*

[Features](#-features) •
[Quick Start](#-quick-start) •
[Architecture](#-architecture) •
[Documentation](#-documentation) •
[Examples](#-examples)

</div>

---

## 📋 Table of Contents

- [Overview](#-overview)
- [Features](#-features)
- [Architecture](#-architecture)
- [Tech Stack](#-tech-stack)
- [Quick Start](#-quick-start)
- [Project Structure](#-project-structure)
- [Service Health Monitoring](#-service-health-monitoring)
- [Feature Flag System](#-feature-flag-system)
- [LLM Integration](#-llm-integration)
- [Database Support](#-database-support)
- [API Examples](#-api-examples)
- [Development Workflow](#-development-workflow)
- [Configuration](#-configuration)
- [Testing](#-testing)
- [Deployment](#-deployment)
- [Customization](#-customization)
- [Contributing](#-contributing)

---

## 🎯 Overview

This template provides a **production-ready foundation** for building modern full-stack applications with Python and React. It includes:

- ✅ **FastAPI backend** with async/await support
- ✅ **React 18 frontend** with TypeScript and Vite
- ✅ **Multiple database options** (PostgreSQL, MongoDB, Neo4j, Redis)
- ✅ **LLM integration** (OpenAI, Anthropic, Google Gemini, Ollama)
- ✅ **Background tasks** with Celery and RabbitMQ
- ✅ **Feature flag system** for runtime control
- ✅ **Admin dashboard** for monitoring and management
- ✅ **Docker Compose** setup for one-command deployment
- ✅ **Hot reload** for rapid development
- ✅ **Type safety** with Pydantic and TypeScript

### Why This Template?

**Problem:** Starting a new full-stack project means hours of boilerplate setup, configuration, and integration work.

**Solution:** Clone this template and get a fully-functional, production-ready application with best practices built in.

```bash
# Traditional approach
⏱️  2-3 days of setup → Configure FastAPI → Setup React → Add databases →
   Integrate auth → Configure Docker → Add monitoring → Write tests

# With this template
⏱️  5 minutes → Clone → Configure → Start → Build your features
```

---

## ✨ Features

### 🏗️ Core Infrastructure

| Feature | Description |
|---------|-------------|
| **FastAPI Backend** | Modern Python web framework with automatic OpenAPI docs |
| **React Frontend** | Component-based UI with hot module replacement (HMR) |
| **Docker Compose** | One-command deployment with service orchestration |
| **Nginx Reverse Proxy** | Production-ready routing and SSL termination |

### 💾 Data Layer

| Database | Use Case | Status |
|----------|----------|--------|
| **PostgreSQL 16** | Relational data + PGVector for embeddings | ✅ Always enabled |
| **MongoDB 7** | Document store for flexible schemas | 🔧 Optional |
| **Neo4j 5.15** | Graph relationships and social networks | 🔧 Optional |
| **Redis 7** | Caching, sessions, Celery broker | ✅ Always enabled |

### 🤖 LLM Integration

| Provider | Models | Status |
|----------|--------|--------|
| **OpenAI** | GPT-4, GPT-3.5 | 🔑 API key required |
| **Anthropic** | Claude 3 Opus, Sonnet | 🔑 API key required |
| **Google** | Gemini Flash | 🔑 API key required |
| **Ollama** | qwen2.5:7b (local) | ✅ Included (11GB) |
| **LiteLLM** | Unified interface | ✅ Configured |

### 🎛️ Advanced Features

- **Feature Flags**: Runtime control of features without redeployment
- **Admin Dashboard**: Web UI for monitoring and management
- **Service Health Checks**: Real-time monitoring of all services
- **Background Tasks**: Celery workers for async processing
- **API Versioning**: `/api/v1/` with automatic documentation
- **Type Safety**: Full type coverage with Pydantic and TypeScript
- **Hot Reload**: Instant updates during development
- **Pre-configured CI/CD**: GitHub Actions and GitLab CI templates

---

## 🏛️ Architecture

### System Overview

```mermaid
graph TB
    subgraph "Frontend Layer"
        FE[React + Vite<br/>TypeScript + TailwindCSS]
    end

    subgraph "API Gateway"
        NGINX[Nginx<br/>Reverse Proxy]
    end

    subgraph "Application Layer"
        API[FastAPI Backend<br/>Async/Await]
        CELERY[Celery Workers<br/>Background Tasks]
    end

    subgraph "Data Layer"
        PG[(PostgreSQL<br/>+ PGVector)]
        MONGO[(MongoDB)]
        NEO[(Neo4j)]
        REDIS[(Redis)]
        RMQ[RabbitMQ]
    end

    subgraph "External Services"
        OPENAI[OpenAI<br/>GPT-4]
        CLAUDE[Anthropic<br/>Claude]
        GEMINI[Google<br/>Gemini]
        OLLAMA[Ollama<br/>Local LLM]
    end

    FE -->|HTTP/5173| NGINX
    NGINX -->|Proxy| API
    API --> PG
    API --> MONGO
    API --> NEO
    API --> REDIS
    API --> RMQ
    RMQ --> CELERY
    CELERY --> PG
    API -.->|API Calls| OPENAI
    API -.->|API Calls| CLAUDE
    API -.->|API Calls| GEMINI
    API -->|HTTP| OLLAMA

    style FE fill:#61dafb,stroke:#333,color:#000
    style API fill:#00a393,stroke:#333,color:#fff
    style NGINX fill:#009639,stroke:#333,color:#fff
    style PG fill:#336791,stroke:#333,color:#fff
    style MONGO fill:#4db33d,stroke:#333,color:#fff
    style NEO fill:#008cc1,stroke:#333,color:#fff
    style REDIS fill:#d82c20,stroke:#333,color:#fff
```

### Application Layers

```mermaid
graph LR
    subgraph "Request Flow"
        A[Client Browser] --> B[Nginx :80]
        B --> C[React Dev Server :5173]
        B --> D[FastAPI :8000]
        D --> E[Service Layer]
        E --> F[Repository Layer]
        F --> G[Database Layer]
    end

    style A fill:#f9f9f9,stroke:#333
    style B fill:#009639,stroke:#333,color:#fff
    style C fill:#61dafb,stroke:#333,color:#000
    style D fill:#00a393,stroke:#333,color:#fff
    style E fill:#ff6b6b,stroke:#333,color:#fff
    style F fill:#4ecdc4,stroke:#333,color:#fff
    style G fill:#336791,stroke:#333,color:#fff
```

**Layer Responsibilities:**

1. **Presentation Layer** - React components, state management, routing
2. **API Gateway** - Nginx reverse proxy, SSL termination, load balancing
3. **Application Layer** - FastAPI routes, request validation, response formatting
4. **Service Layer** - Business logic, orchestration, feature flag checks
5. **Repository Layer** - Data access patterns, query abstraction
6. **Integration Layer** - Database helpers, external API clients
7. **Data Layer** - PostgreSQL, MongoDB, Neo4j, Redis

---

## 🛠️ Tech Stack

### Backend

<table>
<tr>
<td>

**Core**
- Python 3.11
- FastAPI 0.109+
- Pydantic v2
- SQLAlchemy 2.0

</td>
<td>

**Async**
- asyncio
- aioredis
- Motor (MongoDB)
- httpx

</td>
<td>

**Queue**
- Celery 5.3+
- RabbitMQ
- Kombu

</td>
</tr>
</table>

### Frontend

<table>
<tr>
<td>

**Core**
- React 18
- TypeScript 5.3+
- Vite 5

</td>
<td>

**UI/Styling**
- TailwindCSS 3.4
- Lucide Icons
- Custom Components

</td>
<td>

**State/Data**
- TanStack Query v5
- Axios
- React Router v6

</td>
</tr>
</table>

### Infrastructure

<table>
<tr>
<td>

**Containerization**
- Docker 24+
- Docker Compose
- Multi-stage builds

</td>
<td>

**Databases**
- PostgreSQL 16
- MongoDB 7
- Neo4j 5.15
- Redis 7

</td>
<td>

**DevOps**
- Nginx
- Alembic migrations
- GitHub Actions
- Pre-commit hooks

</td>
</tr>
</table>

---

## 🚀 Quick Start

### Prerequisites

- **Docker Desktop** 24+ ([Download](https://www.docker.com/products/docker-desktop))
- **Docker Compose** 2.0+ (included with Docker Desktop)
- **Git** ([Download](https://git-scm.com/downloads))
- *Optional:* Make utility for convenience commands

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/nitinnat/python-project-template.git
cd python-project-template
```

### 2️⃣ Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit with your API keys (optional)
# - OPENAI_API_KEY for GPT models
# - ANTHROPIC_API_KEY for Claude
# - GOOGLE_API_KEY or GEMINI_API_KEY for Gemini
# Ollama works out-of-the-box without API keys!
```

### 3️⃣ Choose Your Setup

#### Option A: Full Stack (Recommended)
All features enabled: Frontend, Backend, Databases, Ollama LLM

```bash
./scripts/quick-start.sh
# or
make dev
```

#### Option B: Minimal (API Only)
Just backend + PostgreSQL + Redis

```bash
docker compose -f docker-compose.minimal.yml up
```

#### Option C: Custom Configuration
Edit `features.env` to enable/disable specific services, then:

```bash
make dev
```

### 4️⃣ Access Your Application

| Service | URL | Credentials |
|---------|-----|-------------|
| **Frontend** | http://localhost:5173 | N/A (auth disabled) |
| **Backend API** | http://localhost:8000 | N/A |
| **API Documentation** | http://localhost:8000/docs | Interactive Swagger UI |
| **Admin Dashboard** | http://localhost:5173/admin | Feature flags, health monitoring |
| **RabbitMQ UI** | http://localhost:15672 | guest / guest |
| **Neo4j Browser** | http://localhost:7474 | neo4j / password |
| **Ollama API** | http://localhost:11434 | Local LLM endpoint |

### 5️⃣ Verify Installation

```bash
# Check all services are healthy
curl http://localhost:8000/api/v1/health/services | jq

# Expected output:
# {
#   "status": "healthy",
#   "services": {
#     "postgres": { "status": "healthy", "latency_ms": 8.56 },
#     "redis": { "status": "healthy", "latency_ms": 1.05 },
#     "mongodb": { "status": "healthy", "latency_ms": 2.36 },
#     "neo4j": { "status": "healthy", "latency_ms": 9.10 },
#     "ollama": { "status": "healthy", "latency_ms": 22.09 }
#   }
# }
```

### 🎉 You're Ready!

The template is running with:
- ✅ Backend API at http://localhost:8000
- ✅ Frontend UI at http://localhost:5173
- ✅ All databases connected
- ✅ Local LLM available (Ollama with qwen2.5:7b)
- ✅ Hot reload enabled for development

---

## 📁 Project Structure

```
python-project-template/
├── backend/                      # FastAPI application
│   ├── app/
│   │   ├── main.py              # Application entry point
│   │   ├── config/
│   │   │   └── settings.py      # Pydantic settings + feature flags
│   │   ├── core/                # Core utilities
│   │   │   ├── auth.py          # JWT (removed, placeholder)
│   │   │   ├── decorators.py    # Feature flag decorators
│   │   │   ├── logging.py       # Logging configuration
│   │   │   └── telemetry.py     # OpenTelemetry setup
│   │   ├── helpers/             # External service clients
│   │   │   ├── postgres.py      # PostgreSQL + PGVector
│   │   │   ├── mongodb.py       # Async MongoDB client
│   │   │   ├── neo4j_helper.py  # Neo4j graph database
│   │   │   ├── redis_helper.py  # Redis cache/sessions
│   │   │   ├── rabbitmq.py      # RabbitMQ producer/consumer
│   │   │   ├── celery_app.py    # Celery configuration
│   │   │   └── llm/             # LLM client integrations
│   │   │       ├── openai_client.py
│   │   │       ├── anthropic_client.py
│   │   │       ├── gemini_client.py
│   │   │       ├── ollama_client.py
│   │   │       ├── litellm_client.py
│   │   │       └── langchain_client.py
│   │   ├── models/              # Database models
│   │   │   ├── postgres/        # SQLAlchemy models
│   │   │   ├── mongodb/         # Motor models
│   │   │   └── neo4j/           # Neomodel graph models
│   │   ├── schemas/             # Pydantic request/response schemas
│   │   ├── repositories/        # Data access layer
│   │   ├── services/            # Business logic layer
│   │   ├── api/v1/              # API routes
│   │   │   ├── admin.py         # Feature flags management
│   │   │   ├── health.py        # Service health checks
│   │   │   ├── documents.py     # MongoDB document API
│   │   │   ├── graph.py         # Neo4j graph API
│   │   │   └── router.py        # API router aggregator
│   │   └── tasks/               # Celery background tasks
│   ├── alembic/                 # Database migrations
│   ├── tests/                   # Test suite (to be implemented)
│   ├── pyproject.toml           # Poetry dependencies
│   ├── Dockerfile               # Backend container
│   └── Dockerfile.celery        # Celery worker container
│
├── frontend/                    # React application
│   ├── src/
│   │   ├── main.tsx            # Application entry point
│   │   ├── App.tsx             # Root component + routing
│   │   ├── api/                # Backend API clients
│   │   │   ├── client.ts       # Axios instance + interceptors
│   │   │   ├── admin.ts        # Admin endpoints
│   │   │   └── types.ts        # TypeScript types
│   │   ├── components/         # Reusable components
│   │   │   ├── common/         # Badge, Switch, etc.
│   │   │   └── auth/           # Auth guards (simplified)
│   │   ├── pages/              # Page components
│   │   │   ├── Dashboard.tsx   # Main dashboard
│   │   │   └── admin/          # Admin pages
│   │   │       ├── FeatureFlags.tsx  # Feature flag management
│   │   │       └── ServiceHealth.tsx # Service monitoring
│   │   ├── layouts/            # Layout components
│   │   ├── hooks/              # Custom React hooks
│   │   ├── lib/                # Utilities
│   │   └── styles/             # Global styles + Tailwind
│   ├── package.json            # npm dependencies
│   ├── vite.config.ts          # Vite configuration
│   ├── tailwind.config.js      # TailwindCSS configuration
│   └── Dockerfile              # Frontend container
│
├── nginx/                       # Reverse proxy
│   ├── nginx.conf              # Nginx configuration
│   └── Dockerfile              # Nginx container
│
├── scripts/                     # Utility scripts
│   ├── quick-start.sh          # One-command startup
│   ├── generate-profiles.sh    # Docker Compose profile generator
│   └── init-project.sh         # Project initialization
│
├── docker-compose.yml           # Base compose configuration
├── docker-compose.dev.yml       # Development overrides
├── docker-compose.prod.yml      # Production overrides
├── docker-compose.minimal.yml   # Minimal setup (backend only)
├── features.env                 # Build-time feature flags
├── .env.example                 # Environment template
├── Makefile                     # Development commands
├── README.md                    # This file
└── TECHNICAL_DESIGN.md          # Detailed architecture docs
```

---

## 🏥 Service Health Monitoring

The template includes a **real-time service health monitoring dashboard** accessible at:

**http://localhost:5173/admin/health**

### Health Check Dashboard

```mermaid
graph TD
    A[Health Dashboard] --> B[PostgreSQL Check]
    A --> C[Redis Check]
    A --> D[MongoDB Check]
    A --> E[Neo4j Check]
    A --> F[RabbitMQ Check]
    A --> G[Ollama Check]

    B --> B1[SELECT 1 Query]
    B --> B2[Measure Latency]

    C --> C1[PING Command]
    C --> C2[Measure Latency]

    D --> D1[Ping Command]
    D --> D2[Measure Latency]

    E --> E1[RETURN 1 Query]
    E --> E2[Measure Latency]

    F --> F1[Config Check]

    G --> G1[/api/tags Endpoint]
    G --> G2[Measure Latency]

    style A fill:#4ecdc4,stroke:#333,color:#000
    style B fill:#336791,stroke:#333,color:#fff
    style C fill:#d82c20,stroke:#333,color:#fff
    style D fill:#4db33d,stroke:#333,color:#fff
    style E fill:#008cc1,stroke:#333,color:#fff
    style F fill:#ff6600,stroke:#333,color:#fff
    style G fill:#00a896,stroke:#333,color:#fff
```

### Features

- ✅ **Real-time monitoring** - Auto-refreshes every 5 seconds
- ✅ **Latency metrics** - Response time for each service
- ✅ **Visual indicators** - Color-coded status (green/red/yellow)
- ✅ **Error details** - Shows error messages when services fail
- ✅ **Conditional checks** - Only monitors enabled services

### API Endpoint

```bash
# Get service health via API
curl http://localhost:8000/api/v1/health/services | jq

# Response example
{
  "status": "healthy",
  "timestamp": 1735374595.936851,
  "services": {
    "postgres": {
      "status": "healthy",
      "latency_ms": 8.56,
      "message": "PostgreSQL is responding"
    },
    "redis": {
      "status": "healthy",
      "latency_ms": 1.05,
      "message": "Redis is responding"
    },
    "mongodb": {
      "status": "healthy",
      "latency_ms": 2.36,
      "message": "MongoDB is responding"
    },
    "neo4j": {
      "status": "healthy",
      "latency_ms": 9.10,
      "message": "Neo4j is responding"
    },
    "rabbitmq": {
      "status": "healthy",
      "message": "RabbitMQ configuration present"
    },
    "ollama": {
      "status": "healthy",
      "latency_ms": 22.09,
      "message": "Ollama is responding"
    }
  }
}
```

---

## 🎛️ Feature Flag System

Control which services and features are enabled without changing code.

### Two-Tier System

```mermaid
graph LR
    A[Feature Flags] --> B[Build-Time Flags]
    A --> C[Runtime Flags]

    B --> D[features.env]
    B --> E[Docker Compose Profiles]

    C --> F[Database Storage]
    C --> G[Admin UI Management]

    D --> H[Enable/Disable Services]
    E --> I[Start Only Needed Containers]

    F --> J[Toggle Features Live]
    G --> K[No Code Deployment]

    style A fill:#4ecdc4,stroke:#333,color:#000
    style B fill:#ff6b6b,stroke:#333,color:#fff
    style C fill:#95e1d3,stroke:#333,color:#000
```

### Build-Time Flags (`features.env`)

Control which **Docker containers** start:

```bash
# Core Services (always recommended)
ENABLE_BACKEND=true
ENABLE_REDIS=true
ENABLE_POSTGRES=true

# Frontend
ENABLE_FRONTEND=true
ENABLE_NGINX=true

# Optional Databases
ENABLE_MONGODB=true
ENABLE_NEO4J=true
ENABLE_PGVECTOR=true

# Background Processing
ENABLE_RABBITMQ=false
ENABLE_CELERY_WORKER=false
ENABLE_CELERY_BEAT=false

# LLM Providers
ENABLE_LLM_OLLAMA=true
ENABLE_LLM_OPENAI=true
ENABLE_LLM_ANTHROPIC=true
ENABLE_LLM_GOOGLE=false
```

**Apply changes:**
```bash
# Edit features.env, then restart
make dev
```

**Optimized Dependencies:** Feature flags automatically control which Python dependencies are installed during build. Disabling MongoDB/Neo4j/LLM providers in `features.env` skips their corresponding packages, reducing build time by 50%+ and container size significantly.

### Runtime Flags (Admin UI)

Control **application features** without restarting:

**Access:** http://localhost:5173/admin/feature-flags

**Features:**
- ✅ List all feature flags by category
- ✅ Toggle flags on/off with visual switches
- ✅ View flag metadata and dependencies
- ✅ Changes take effect immediately (60s cache TTL)

**Categories:**
- **Database** - MongoDB, Neo4j, PGVector usage
- **Features** - Vector search, graph queries, document storage
- **LLM** - OpenAI, Anthropic, Google, Ollama integrations
- **Integrations** - External service connections

**Example flags:**
- `feature.vector_search` - Enable semantic search with PGVector
- `feature.graph_queries` - Enable Neo4j graph traversal
- `llm.openai` - Enable OpenAI GPT models
- `database.mongodb` - Enable MongoDB document storage

---

## 🤖 LLM Integration

The template includes **4 LLM providers** out-of-the-box with a unified interface.

### Ollama (Local LLM) - Pre-configured ✅

**No API key needed!** Runs entirely on your machine.

```bash
# Test Ollama (already includes qwen2.5:7b model)
docker compose exec backend python -c "
import asyncio
from app.helpers.llm.ollama_client import ollama_client

async def test():
    response = await ollama_client.generate('Say hello from the template!')
    print(response['content'])

asyncio.run(test())
"
```

**Model:** `qwen2.5:7b` (7 billion parameters, ~11GB)
**Performance:** Fast inference on modern CPUs/GPUs
**Use cases:** Development, testing, privacy-sensitive applications

### Google Gemini

```bash
# Set API key in .env
GOOGLE_API_KEY=your-key-here
# or
GEMINI_API_KEY=your-key-here
```

**Model:** `gemini-1.5-flash-latest`
**Strengths:** Fast, cost-effective, multimodal support

### OpenAI

```bash
# Set API key in .env
OPENAI_API_KEY=sk-...
```

**Models:** GPT-4, GPT-4 Turbo, GPT-3.5 Turbo
**Strengths:** State-of-the-art reasoning, broad knowledge

### Anthropic Claude

```bash
# Set API key in .env
ANTHROPIC_API_KEY=sk-ant-...
```

**Models:** Claude 3 Opus, Sonnet, Haiku
**Strengths:** Long context windows, safety, coding tasks

### LiteLLM - Unified Interface

Use **any provider** with a single API:

```python
from app.helpers.llm.litellm_client import litellm_client

# Automatically routes to correct provider
response = await litellm_client.complete(
    model="gpt-4",  # or "claude-3-opus", "gemini-flash", etc.
    messages=[{"role": "user", "content": "Hello!"}]
)
```

**Benefits:**
- ✅ Consistent API across all providers
- ✅ Automatic retries and fallbacks
- ✅ Cost tracking and logging
- ✅ Load balancing

---

## 💾 Database Support

### PostgreSQL + PGVector

**Primary relational database with vector similarity search.**

```python
# Example: Store document with embedding
from app.helpers.postgres import postgres_helper
from pgvector.sqlalchemy import Vector

async with postgres_helper.get_session() as session:
    # Store embedding (1536 dimensions for OpenAI)
    doc = Document(
        content="Machine learning is...",
        embedding=[0.1, 0.2, ..., 0.9]  # 1536 floats
    )
    session.add(doc)
    await session.commit()

    # Similarity search
    similar_docs = await session.execute(
        select(Document)
        .order_by(Document.embedding.l2_distance(query_embedding))
        .limit(10)
    )
```

**Use cases:** User data, transactions, vector search, RAG systems

### MongoDB

**Document store for flexible schemas.**

```python
from app.helpers.mongodb import mongodb_helper

db = mongodb_helper.get_database()
collection = db["products"]

# Insert document
await collection.insert_one({
    "name": "Widget",
    "price": 29.99,
    "tags": ["gadget", "electronics"],
    "metadata": {"color": "blue", "weight_kg": 0.5}
})

# Query with rich filters
products = await collection.find({
    "price": {"$lt": 50},
    "tags": {"$in": ["electronics"]}
}).to_list(length=100)
```

**Use cases:** Product catalogs, logs, unstructured data, rapid prototyping

### Neo4j

**Graph database for relationships and networks.**

```python
from app.helpers.neo4j_helper import neo4j_helper

driver = neo4j_helper.get_driver()

async with driver.session() as session:
    # Create relationship
    await session.run("""
        MATCH (a:Person {name: $person1})
        MATCH (b:Person {name: $person2})
        CREATE (a)-[:FOLLOWS]->(b)
    """, person1="Alice", person2="Bob")

    # Find friends-of-friends
    result = await session.run("""
        MATCH (me:Person {name: $name})-[:FOLLOWS]->()-[:FOLLOWS]->(friend)
        WHERE NOT (me)-[:FOLLOWS]->(friend)
        RETURN friend.name
    """, name="Alice")
```

**Use cases:** Social networks, recommendation engines, knowledge graphs, fraud detection

### Redis

**In-memory cache and session store.**

```python
from app.helpers.redis_helper import redis_helper

redis = redis_helper.get_client()

# Cache with TTL
await redis.set("user:123:profile", json.dumps(user_data), ex=300)

# Retrieve
cached = await redis.get("user:123:profile")

# Pub/Sub
await redis.publish("notifications", json.dumps(message))
```

**Use cases:** Session storage, caching, rate limiting, real-time features

---

## 📚 API Examples

### Health Check

```bash
# Basic health check
curl http://localhost:8000/health

# Response
{
  "status": "healthy",
  "service": "python-project-template",
  "version": "1.0.0"
}
```

### Feature Flags

```bash
# List all feature flags
curl http://localhost:8000/api/v1/admin/feature-flags | jq

# Update a flag
curl -X PATCH http://localhost:8000/api/v1/admin/feature-flags/llm.openai \
  -H "Content-Type: application/json" \
  -d '{"enabled": true}'
```

### Document API (MongoDB)

```bash
# Create document
curl -X POST http://localhost:8000/api/v1/documents \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Getting Started",
    "content": "This is a sample document",
    "tags": ["tutorial", "guide"]
  }'

# List documents
curl http://localhost:8000/api/v1/documents | jq
```

### Graph API (Neo4j)

```bash
# Create node
curl -X POST http://localhost:8000/api/v1/graph/nodes \
  -H "Content-Type: application/json" \
  -d '{
    "label": "Person",
    "properties": {"name": "Alice", "age": 30}
  }'

# Create relationship
curl -X POST http://localhost:8000/api/v1/graph/relationships \
  -H "Content-Type: application/json" \
  -d '{
    "from_id": "node_1",
    "to_id": "node_2",
    "type": "KNOWS"
  }'
```

### Interactive API Documentation

Visit **http://localhost:8000/docs** for:
- ✅ Full API documentation (auto-generated from code)
- ✅ Interactive "Try it out" feature
- ✅ Request/response schemas
- ✅ Authentication testing

---

## 🔧 Development Workflow

### Makefile Commands

```bash
# Development
make dev              # Start with hot reload
make down             # Stop all services
make clean            # Remove volumes and caches

# Database
make migrate          # Run migrations
make migrate-create   # Create new migration
                     # Usage: make migrate-create msg="add users table"

# Code Quality
make lint             # Run linters (backend + frontend)
make format           # Format code (black + prettier)
make test             # Run test suites

# Logs
make logs             # View all logs
make logs-backend     # Backend logs only
make logs-frontend    # Frontend logs only
```

### Hot Reload

**Backend (FastAPI):**
- Code changes → Auto-reload (< 1 second)
- Volume mount: `./backend:/app`
- Runs with `--reload` flag

**Frontend (Vite):**
- Code changes → Hot Module Replacement (< 200ms)
- Volume mount: `./frontend:/app`
- Preserves React component state

### Database Migrations

```bash
# Create migration (auto-generates from model changes)
make migrate-create msg="add feature flags table"

# Review generated migration
cat backend/alembic/versions/*_add_feature_flags_table.py

# Apply migration
make migrate

# Rollback one version
docker compose exec backend alembic downgrade -1
```

### Adding a New Feature

**Example: Add a "tasks" feature**

1. **Backend Model** (`backend/app/models/postgres/task.py`)
```python
from sqlalchemy import Column, Integer, String, Boolean
from app.models.postgres.base import Base

class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    completed = Column(Boolean, default=False)
```

2. **Schema** (`backend/app/schemas/task.py`)
```python
from pydantic import BaseModel

class TaskCreate(BaseModel):
    title: str

class TaskResponse(BaseModel):
    id: int
    title: str
    completed: bool

    model_config = {"from_attributes": True}
```

3. **API Route** (`backend/app/api/v1/tasks.py`)
```python
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.api.deps import get_db

router = APIRouter(prefix="/tasks", tags=["tasks"])

@router.post("/", response_model=TaskResponse)
async def create_task(data: TaskCreate, db: AsyncSession = Depends(get_db)):
    task = Task(**data.model_dump())
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task
```

4. **Register Router** (`backend/app/api/v1/router.py`)
```python
from app.api.v1 import tasks

api_router.include_router(tasks.router)
```

5. **Migration**
```bash
make migrate-create msg="add tasks table"
make migrate
```

6. **Frontend API Client** (`frontend/src/api/tasks.ts`)
```typescript
import { apiClient } from './client';

export const tasksApi = {
  async create(title: string) {
    const response = await apiClient.post('/tasks', { title });
    return response.data;
  },

  async list() {
    const response = await apiClient.get('/tasks');
    return response.data;
  }
};
```

---

## ⚙️ Configuration

### Environment Variables

**Backend** (`.env`):
```bash
# Application
APP_NAME=python-project-template
APP_ENV=development
SECRET_KEY=your-secret-key-change-in-production

# Database URLs (auto-configured in Docker)
POSTGRES_URL=postgresql+asyncpg://postgres:postgres@postgres:5432/app_db
MONGODB_URL=mongodb://mongo:mongo@mongodb:27017/app_db
NEO4J_URL=bolt://neo4j:password@neo4j:7687
REDIS_URL=redis://redis:6379/0

# LLM API Keys
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
GOOGLE_API_KEY=...
GEMINI_API_KEY=...

# Ollama (local)
OLLAMA_HOST=http://ollama:11434

# Celery
CELERY_BROKER_URL=amqp://guest:guest@rabbitmq:5672//
CELERY_RESULT_BACKEND=redis://redis:6379/0
```

**Frontend** (`.env`):
```bash
VITE_API_URL=http://localhost:8000/api/v1
```

### Feature Flags

Edit `features.env` to control which services start:

```bash
# Enable all features (microservices setup)
cp features.env.microservices features.env
make dev

# Minimal setup (API only)
cp features.env.minimal features.env
make dev

# Custom configuration
vi features.env  # Edit to your needs
make dev
```

---

## 🧪 Testing

### Backend Tests

```bash
# Run all tests
make test

# Run with coverage
docker compose exec backend pytest --cov=app --cov-report=html

# Run specific test file
docker compose exec backend pytest tests/unit/test_services.py -v

# Run with markers
docker compose exec backend pytest -m "not slow"
```

**Structure:**
```
backend/tests/
├── unit/              # Fast, isolated tests
├── integration/       # Tests with databases
└── e2e/              # Full API tests
```

### Frontend Tests

```bash
# Run tests
docker compose exec frontend npm test

# Run in watch mode
docker compose exec frontend npm test -- --watch

# Coverage report
docker compose exec frontend npm test -- --coverage
```

**Tools:**
- Vitest (test runner)
- React Testing Library (component tests)
- MSW (API mocking)

---

## 🚀 Deployment

### Local Development

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

### Production

```bash
# 1. Configure production environment
cp .env.example .env.prod
# Edit .env.prod with:
# - APP_ENV=production
# - APP_DEBUG=false
# - Strong SECRET_KEY
# - Production database URLs
# - Real API keys

# 2. Build production images
docker compose -f docker-compose.yml -f docker-compose.prod.yml build

# 3. Run migrations
docker compose -f docker-compose.yml -f docker-compose.prod.yml run backend alembic upgrade head

# 4. Start services
docker compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 5. Verify
curl https://yourdomain.com/api/v1/health
```

### Cloud Platforms

**AWS ECS:**
- Use Fargate for serverless containers
- RDS for PostgreSQL
- DocumentDB for MongoDB
- ElastiCache for Redis
- Application Load Balancer

**Google Cloud Run:**
- Deploy each service separately
- Cloud SQL for PostgreSQL
- Firestore or MongoDB Atlas
- Memorystore for Redis
- Cloud Load Balancing

**DigitalOcean:**
- App Platform for auto-deployment
- Managed PostgreSQL database
- Managed Redis cluster
- Container Registry

### Docker Hub

```bash
# Build and tag
docker build -t yourusername/project-backend:1.0 ./backend
docker build -t yourusername/project-frontend:1.0 ./frontend

# Push
docker push yourusername/project-backend:1.0
docker push yourusername/project-frontend:1.0
```

---

## 🎨 Customization

### Replace Frontend Framework

Keep the backend, replace React with Vue/Svelte/Angular:

1. Keep `backend/` unchanged
2. Replace `frontend/` with your preferred framework
3. Update `nginx/nginx.conf` proxy settings
4. Ensure your framework calls `http://backend:8000/api/v1`

### Add New Database

Example: Elasticsearch for search

1. **Add to docker-compose.yml:**
```yaml
elasticsearch:
  image: elasticsearch:8.11
  environment:
    - discovery.type=single-node
  ports:
    - "9200:9200"
  profiles:
    - elasticsearch
```

2. **Create helper:**
```python
# backend/app/helpers/elasticsearch.py
from elasticsearch import AsyncElasticsearch

class ElasticsearchHelper:
    def __init__(self):
        self.client = AsyncElasticsearch(["http://elasticsearch:9200"])

    async def search(self, index: str, query: dict):
        return await self.client.search(index=index, body=query)
```

3. **Enable in features.env:**
```bash
ENABLE_ELASTICSEARCH=true
```

---

## 🤝 Contributing

We welcome contributions! Whether you're fixing bugs, adding features, or improving documentation, your help is appreciated.

### How to Contribute

```bash
# 1. Fork and clone the repository
git clone https://github.com/your-username/python-project-template.git
cd python-project-template

# 2. Create a feature branch
git checkout -b feature/amazing-feature

# 3. Make your changes and test thoroughly
make dev
make test
make lint

# 4. Commit using conventional commits
git commit -m "feat: add amazing feature"

# 5. Push to your fork
git push origin feature/amazing-feature

# 6. Open a Pull Request on GitHub
```

### Code Standards

- **Python:** Black formatting, Ruff linting, type hints required
- **TypeScript:** Prettier formatting, ESLint, strict mode
- **Commits:** Follow [Conventional Commits](https://www.conventionalcommits.org/) (feat:, fix:, docs:, etc.)
- **Tests:** Required for new features
- **Documentation:** Update README.md and TECHNICAL_DESIGN.md as needed

### Pull Request Guidelines

1. **Describe your changes** - Explain what and why
2. **Add tests** - Ensure new code is covered
3. **Update documentation** - Keep docs in sync
4. **Follow code style** - Run `make lint` and `make format`
5. **Keep commits atomic** - One logical change per commit
6. **Reference issues** - Link to related issues if applicable

### Getting Help

- **Documentation:** See [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) for detailed architecture
- **API Docs:** http://localhost:8000/docs (when running)
- **Issues:** [Report bugs](https://github.com/nitinnat/python-project-template/issues)
- **Discussions:** [Ask questions](https://github.com/nitinnat/python-project-template/discussions)

### Reporting Bugs

When reporting bugs, please include:
1. **Steps to reproduce** - Clear, numbered steps
2. **Expected behavior** - What should happen
3. **Actual behavior** - What actually happens
4. **Environment** - OS, Docker version, browser (if applicable)
5. **Logs** - Relevant error messages or stack traces

---

## 📄 License

This project is licensed under the **MIT License** - see the [LICENSE](LICENSE) file for details.

You are free to:
- ✅ Use commercially
- ✅ Modify
- ✅ Distribute
- ✅ Use privately

---

<div align="center">

**Built with ❤️ for developers who want to ship faster**

⭐ **Star this repo** if you find it helpful!

[Report Bug](https://github.com/nitinnat/python-project-template/issues) •
[Request Feature](https://github.com/nitinnat/python-project-template/issues) •
[Discussions](https://github.com/nitinnat/python-project-template/discussions)

</div>
