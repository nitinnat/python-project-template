# Backend Dockerfile for FastAPI application
FROM python:3.11-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    postgresql-client \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install poetry==1.7.1

# Copy dependency files (poetry.lock must exist for fast builds)
COPY pyproject.toml poetry.lock ./

# Accept build arguments for individual extras
ARG ENABLE_MONGODB=false
ARG ENABLE_NEO4J=false
ARG ENABLE_CELERY_WORKER=false
ARG ENABLE_LLM_OPENAI=false
ARG ENABLE_LLM_ANTHROPIC=false
ARG ENABLE_LLM_GOOGLE=false
ARG ENABLE_LLM_LITELLM=false
ARG ENABLE_LLM_LANGCHAIN=false

# Install Python dependencies with selected extras based on enabled features
RUN poetry config virtualenvs.create false

RUN EXTRAS=""; \
    [ "$ENABLE_MONGODB" = "true" ] && EXTRAS="$EXTRAS mongodb"; \
    [ "$ENABLE_NEO4J" = "true" ] && EXTRAS="$EXTRAS neo4j"; \
    [ "$ENABLE_CELERY_WORKER" = "true" ] && EXTRAS="$EXTRAS celery"; \
    [ "$ENABLE_LLM_OPENAI" = "true" ] && EXTRAS="$EXTRAS openai"; \
    [ "$ENABLE_LLM_ANTHROPIC" = "true" ] && EXTRAS="$EXTRAS anthropic"; \
    [ "$ENABLE_LLM_GOOGLE" = "true" ] && EXTRAS="$EXTRAS google"; \
    [ "$ENABLE_LLM_LITELLM" = "true" ] && EXTRAS="$EXTRAS litellm"; \
    [ "$ENABLE_LLM_LANGCHAIN" = "true" ] && EXTRAS="$EXTRAS langchain"; \
    if [ -n "$EXTRAS" ]; then \
      echo "Installing with extras:$EXTRAS"; \
      poetry install --no-interaction --no-ansi --no-root $(echo $EXTRAS | sed 's/ / --extras /g' | sed 's/^/--extras /'); \
    else \
      echo "Installing base dependencies only"; \
      poetry install --no-interaction --no-ansi --no-root; \
    fi

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
