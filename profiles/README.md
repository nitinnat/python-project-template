# Feature Configuration Profiles

Pre-configured `features.env` profiles for different use cases. Copy one to the root directory as `features.env` to get started quickly.

## Quick Start

```bash
# Copy a profile to use it
cp profiles/PROFILE_NAME.env features.env

# Start the stack
make dev
```

## Available Profiles

### 🚀 minimal.env
**Best for:** Simple REST APIs, microservices, learning basics
**Containers:** Backend, PostgreSQL, Redis
**Dependencies:** Base packages only
**Size:** ~500MB

### 🌐 fullstack.env
**Best for:** Modern web apps with React frontend
**Containers:** Backend, Frontend, PostgreSQL (PGVector), Redis, Nginx
**Dependencies:** Base packages
**Size:** ~1GB

### 🤖 ai-local.env
**Best for:** AI/ML development with local models (privacy-first)
**Containers:** Backend, PostgreSQL (PGVector), Redis, Ollama
**Models:** qwen2.5:7b (chat), nomic-embed-text (embeddings)
**Dependencies:** Base packages only
**Size:** ~5GB (includes models)
**Use cases:** RAG systems, embeddings, local LLM development

### ☁️ ai-cloud.env
**Best for:** Production AI apps with cloud LLM providers
**Containers:** Backend, PostgreSQL (PGVector), Redis
**Dependencies:** Base + OpenAI + Anthropic + Google SDKs
**Size:** ~800MB
**Requires:** API keys for OpenAI/Anthropic/Google
**Use cases:** Production chatbots, AI assistants, content generation

### 📊 data-platform.env
**Best for:** Data-intensive apps, analytics, graph databases
**Containers:** Backend, PostgreSQL, MongoDB, Neo4j, Redis
**Dependencies:** Base + MongoDB (motor) + Neo4j drivers
**Size:** ~2GB
**Use cases:** Social networks, knowledge graphs, document stores

### ⚡ async-tasks.env
**Best for:** Background job processing, scheduled tasks
**Containers:** Backend, PostgreSQL, Redis, RabbitMQ, Celery (Worker + Beat)
**Dependencies:** Base + Celery + Kombu
**Size:** ~1GB
**Use cases:** Email sending, report generation, data processing

### 🎯 everything.env
**Best for:** Exploring all features, comprehensive learning
**Containers:** ALL (11 containers)
**Dependencies:** ALL optional packages
**Size:** ~15GB
**Warning:** Large download, slower builds

## Customization

After copying a profile, you can customize it:

1. Edit `features.env` to enable/disable specific features
2. Customize Ollama models: Add `OLLAMA_MODELS=model1,model2` to `.env` (default: `qwen2.5:7b,nomic-embed-text`)
3. Restart services: `docker compose down && make dev`

**Ollama Model Configuration:**
- Set `OLLAMA_MODELS` in `.env` with comma-separated model names
- Models auto-download on Ollama container startup
- Default models: `qwen2.5:7b` (chat, 4.7GB), `nomic-embed-text` (embeddings, 274MB)
- Examples: `llama3.3:70b`, `mistral`, `codellama`, `phi3`, `gemma2:27b`

## Profile Comparison

| Profile | Containers | Build Time | Disk Space | Use Case |
|---------|-----------|------------|------------|----------|
| minimal | 3 | ~2 min | ~500MB | Simple API |
| fullstack | 5 | ~3 min | ~1GB | Web app |
| ai-local | 4 | ~5 min* | ~5GB | Local AI |
| ai-cloud | 3 | ~3 min | ~800MB | Cloud AI |
| data-platform | 5 | ~4 min | ~2GB | Multi-DB |
| async-tasks | 6 | ~3 min | ~1GB | Background jobs |
| everything | 11 | ~10 min* | ~15GB | Full exploration |

*Includes model downloads for Ollama

## Examples

### Start with minimal API
```bash
cp profiles/minimal.env features.env
make dev
# Access API: http://localhost:8000/docs
```

### AI development with local models
```bash
cp profiles/ai-local.env features.env
make dev
# Models auto-download on first start
# Test: docker compose exec ollama ollama list
```

### Production AI app with cloud providers
```bash
cp profiles/ai-cloud.env features.env
# Add API keys to .env first
make dev
```

### Full-stack web app
```bash
cp profiles/fullstack.env features.env
make dev
# Frontend: http://localhost:5173
# Backend: http://localhost:8000
```
