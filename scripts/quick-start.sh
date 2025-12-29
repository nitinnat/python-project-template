#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Configuration variables
PROJECT_NAME=""
ENABLE_FRONTEND="true"
ENABLE_NGINX="true"
ENABLE_MONGODB="false"
ENABLE_NEO4J="false"
ENABLE_RABBITMQ="false"
ENABLE_CELERY_WORKER="false"
LLM_PROVIDER="ollama"
OLLAMA_MODELS="phi3,nomic-embed-text"

# Parse command-line arguments
INTERACTIVE=true
PRESET=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --no-interactive)
            INTERACTIVE=false
            shift
            ;;
        --preset)
            PRESET="$2"
            INTERACTIVE=false
            shift 2
            ;;
        --name)
            PROJECT_NAME="$2"
            shift 2
            ;;
        --frontend)
            ENABLE_FRONTEND="true"
            shift
            ;;
        --no-frontend)
            ENABLE_FRONTEND="false"
            shift
            ;;
        --nginx)
            ENABLE_NGINX="true"
            shift
            ;;
        --no-nginx)
            ENABLE_NGINX="false"
            shift
            ;;
        --ollama)
            LLM_PROVIDER="ollama"
            shift
            ;;
        --openai)
            LLM_PROVIDER="openai"
            shift
            ;;
        --mongodb)
            ENABLE_MONGODB="true"
            shift
            ;;
        --neo4j)
            ENABLE_NEO4J="true"
            shift
            ;;
        --celery)
            ENABLE_CELERY_WORKER="true"
            ENABLE_RABBITMQ="true"
            shift
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Helper functions
ask_input() {
    local prompt="$1"
    local default="$2"
    local result

    if [ -n "$default" ]; then
        read -p "$prompt [$default]: " result
        echo "${result:-$default}"
    else
        read -p "$prompt: " result
        echo "$result"
    fi
}

ask_yes_no() {
    local prompt="$1"
    local default="$2"
    local result

    if [ "$default" = "y" ]; then
        read -p "$prompt (Y/n): " result
        result="${result:-y}"
    else
        read -p "$prompt (y/N): " result
        result="${result:-n}"
    fi

    [[ "$result" =~ ^[Yy] ]]
}

ask_choice() {
    local prompt="$1"
    shift
    local options=("$@")
    local choice

    echo -e "$prompt"
    for i in "${!options[@]}"; do
        echo -e "  $((i+1))) ${options[$i]}"
    done
    echo ""

    while true; do
        read -p "Choice [1]: " choice
        choice="${choice:-1}"
        if [[ "$choice" =~ ^[0-9]+$ ]] && [ "$choice" -ge 1 ] && [ "$choice" -le "${#options[@]}" ]; then
            echo "$((choice-1))"
            return
        fi
        echo -e "${RED}Invalid choice. Please enter a number between 1 and ${#options[@]}${NC}"
    done
}

apply_preset() {
    local preset="$1"

    case "$preset" in
        minimal)
            ENABLE_FRONTEND="false"
            ENABLE_NGINX="false"
            ENABLE_MONGODB="false"
            ENABLE_NEO4J="false"
            ENABLE_RABBITMQ="false"
            ENABLE_CELERY_WORKER="false"
            LLM_PROVIDER="none"
            ;;
        fullstack)
            ENABLE_FRONTEND="true"
            ENABLE_NGINX="true"
            ENABLE_MONGODB="false"
            ENABLE_NEO4J="false"
            ENABLE_RABBITMQ="false"
            ENABLE_CELERY_WORKER="false"
            LLM_PROVIDER="ollama"
            OLLAMA_MODELS="phi3,nomic-embed-text"
            ;;
        ai-local)
            ENABLE_FRONTEND="false"
            ENABLE_NGINX="false"
            ENABLE_MONGODB="false"
            ENABLE_NEO4J="false"
            ENABLE_RABBITMQ="false"
            ENABLE_CELERY_WORKER="false"
            LLM_PROVIDER="ollama"
            OLLAMA_MODELS="qwen2.5:7b,nomic-embed-text"
            ;;
        ai-cloud)
            ENABLE_FRONTEND="false"
            ENABLE_NGINX="false"
            ENABLE_MONGODB="false"
            ENABLE_NEO4J="false"
            ENABLE_RABBITMQ="false"
            ENABLE_CELERY_WORKER="false"
            LLM_PROVIDER="cloud"
            ;;
        async-tasks)
            ENABLE_FRONTEND="false"
            ENABLE_NGINX="false"
            ENABLE_MONGODB="false"
            ENABLE_NEO4J="false"
            ENABLE_RABBITMQ="true"
            ENABLE_CELERY_WORKER="true"
            LLM_PROVIDER="none"
            ;;
        data-platform)
            ENABLE_FRONTEND="false"
            ENABLE_NGINX="false"
            ENABLE_MONGODB="true"
            ENABLE_NEO4J="true"
            ENABLE_RABBITMQ="false"
            ENABLE_CELERY_WORKER="false"
            LLM_PROVIDER="none"
            ;;
        *)
            echo -e "${RED}Unknown preset: $preset${NC}"
            echo "Available presets: minimal, fullstack, ai-local, ai-cloud, async-tasks, data-platform"
            exit 1
            ;;
    esac
}

# Project name is determined by parent folder name
# No need to rename anything - Docker Compose will use directory name as project name

generate_env_file() {
    echo -e "${BLUE}📄 Generating .env file...${NC}"

    cat > .env << EOF
# App Configuration
APP_NAME=${PROJECT_NAME}
APP_ENV=development
APP_DEBUG=true
SECRET_KEY=change-this-to-a-random-secret-key-in-production

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
REDIS_PASSWORD=

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

# Google Gemini
GOOGLE_API_KEY=your-google-api-key

# Ollama
OLLAMA_HOST=http://ollama:11434
OLLAMA_MODELS=${OLLAMA_MODELS}

# CORS
CORS_ORIGINS=http://localhost:3000,http://localhost:5173,http://localhost:80

# Feature Flags - Services
ENABLE_BACKEND=true
ENABLE_REDIS=true
ENABLE_POSTGRES=true
ENABLE_PGVECTOR=true
ENABLE_MONGODB=${ENABLE_MONGODB}
ENABLE_NEO4J=${ENABLE_NEO4J}
ENABLE_RABBITMQ=${ENABLE_RABBITMQ}
ENABLE_CELERY_WORKER=${ENABLE_CELERY_WORKER}
ENABLE_CELERY_BEAT=${ENABLE_CELERY_WORKER}
ENABLE_FRONTEND=${ENABLE_FRONTEND}
ENABLE_NGINX=${ENABLE_NGINX}

# Feature Flags - LLM Providers
ENABLE_LLM_OPENAI=$([ "$LLM_PROVIDER" = "openai" ] || [ "$LLM_PROVIDER" = "cloud" ] && echo "true" || echo "false")
ENABLE_LLM_ANTHROPIC=$([ "$LLM_PROVIDER" = "anthropic" ] || [ "$LLM_PROVIDER" = "cloud" ] && echo "true" || echo "false")
ENABLE_LLM_GOOGLE=$([ "$LLM_PROVIDER" = "google" ] || [ "$LLM_PROVIDER" = "cloud" ] && echo "true" || echo "false")
ENABLE_LLM_OLLAMA=$([ "$LLM_PROVIDER" = "ollama" ] && echo "true" || echo "false")
ENABLE_LLM_LITELLM=false
ENABLE_LLM_LANGCHAIN=false
EOF

    echo -e "${GREEN}✅ Created .env${NC}"
}

# Main script
echo "============================================================"
echo "🚀 Python Full-Stack Project Template - Quick Start"
echo "============================================================"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}❌ Error: Docker is not running. Please start Docker Desktop.${NC}"
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Apply preset if specified
if [ -n "$PRESET" ]; then
    apply_preset "$PRESET"
    echo -e "${GREEN}✅ Applied preset: ${PRESET}${NC}"
    echo ""
fi

# Interactive setup
if [ "$INTERACTIVE" = true ]; then
    # Service selection
    echo -e "${BLUE}🎯 Service Selection${NC}"
    if ask_yes_no "Do you want a frontend" "y"; then
        ENABLE_FRONTEND="true"
        if ask_yes_no "Do you want Nginx reverse proxy" "y"; then
            ENABLE_NGINX="true"
        else
            ENABLE_NGINX="false"
        fi
    else
        ENABLE_FRONTEND="false"
        ENABLE_NGINX="false"
    fi
    echo ""

    # LLM provider selection
    echo -e "${BLUE}🤖 AI/LLM Setup${NC}"
    llm_choice=$(ask_choice "Which LLM provider do you want?" \
        "None" \
        "Ollama (local, free)" \
        "OpenAI (requires API key)" \
        "Anthropic (requires API key)" \
        "Google Gemini (requires API key)" \
        "Multiple cloud providers")

    case $llm_choice in
        0) LLM_PROVIDER="none" ;;
        1) LLM_PROVIDER="ollama"
           OLLAMA_MODELS=$(ask_input "Which Ollama models? (comma-separated)" "phi3,nomic-embed-text")
           ;;
        2) LLM_PROVIDER="openai" ;;
        3) LLM_PROVIDER="anthropic" ;;
        4) LLM_PROVIDER="google" ;;
        5) LLM_PROVIDER="cloud" ;;
    esac
    echo ""

    # Database selection
    echo -e "${BLUE}📊 Database Selection${NC}"
    echo "PostgreSQL and Redis are required and always enabled."
    if ask_yes_no "Do you need MongoDB" "n"; then
        ENABLE_MONGODB="true"
    fi
    if ask_yes_no "Do you need Neo4j" "n"; then
        ENABLE_NEO4J="true"
    fi
    echo ""

    # Advanced features
    echo -e "${BLUE}🔧 Advanced Features${NC}"
    if ask_yes_no "Do you need background task processing (Celery)" "n"; then
        ENABLE_CELERY_WORKER="true"
        ENABLE_RABBITMQ="true"
    fi
    echo ""

    echo -e "${GREEN}✅ Configuration complete!${NC}"
    echo ""
fi

# Set PROJECT_NAME from directory name
PROJECT_NAME=$(basename "$(pwd)")

# Generate .env file
generate_env_file

# Prompt user to review and edit .env if needed
echo ""
echo -e "${YELLOW}📝 IMPORTANT: Review your .env file before continuing${NC}"
echo ""
echo "The .env file has been generated at: $(pwd)/.env"
echo ""
echo "You may need to update:"
echo "  - API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY, GOOGLE_API_KEY)"
echo "  - Database passwords (for production)"
echo "  - SECRET_KEY (change in production)"
echo ""

if [ "$INTERACTIVE" = true ]; then
    if ! ask_yes_no "Continue with Docker setup" "y"; then
        echo ""
        echo -e "${GREEN}✅ Configuration saved to .env${NC}"
        echo ""
        echo -e "${YELLOW}Setup paused. Next steps:${NC}"
        echo "  1. Edit .env file and add your API keys"
        echo "  2. When ready, run: ./scripts/quick-start.sh --no-interactive"
        echo "     Or run: make dev"
        echo ""
        exit 0
    fi
fi

# Regenerate poetry.lock if pyproject.toml was modified
if [ backend/pyproject.toml -nt backend/poetry.lock ]; then
    echo -e "${BLUE}📝 pyproject.toml updated, regenerating poetry.lock...${NC}"
    cd backend && poetry lock && cd ..
    echo -e "${GREEN}✅ poetry.lock updated${NC}"
    echo ""
fi

# Check if services are already running
if docker compose ps | grep -q "Up"; then
    echo -e "${YELLOW}⚠️  Services are already running. Stopping them first...${NC}"
    docker compose down
    echo ""
fi

# Start services
echo ""
echo -e "${BLUE}🐳 Starting Docker containers...${NC}"
PROFILES=$(./scripts/generate-profiles.sh)
docker compose -f docker-compose.yml -f docker-compose.dev.yml $PROFILES up -d

echo ""
echo -e "${BLUE}⏳ Waiting for services to be healthy...${NC}"
sleep 10

# Check if backend is up
echo -e "${BLUE}🔍 Checking backend status...${NC}"
until docker compose exec backend curl -f http://localhost:8000/health > /dev/null 2>&1; do
    echo "   Waiting for backend..."
    sleep 2
done
echo -e "${GREEN}✅ Backend is ready${NC}"

# Run migrations
echo ""
echo -e "${BLUE}🗄️  Running database migrations...${NC}"
docker compose exec backend alembic upgrade head
echo -e "${GREEN}✅ Migrations complete${NC}"

# Seed data
echo ""
echo -e "${BLUE}🌱 Seeding initial data...${NC}"
docker compose exec backend python scripts/seed_data.py
echo ""

echo "============================================================"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo "============================================================"
echo ""
echo "Access the application:"
if [ "$ENABLE_NGINX" = "true" ]; then
    echo -e "  🌐 Frontend:     ${BLUE}http://localhost:80${NC}"
fi
if [ "$ENABLE_FRONTEND" = "true" ] && [ "$ENABLE_NGINX" = "false" ]; then
    echo -e "  🌐 Frontend:     ${BLUE}http://localhost:5173${NC}"
fi
echo -e "  🔧 Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "  📚 API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
if [ "$ENABLE_LLM_OLLAMA" = "true" ]; then
    echo -e "  🤖 Ollama:       ${BLUE}http://localhost:11434${NC}"
fi
echo ""
echo "Default credentials:"
echo "  📧 Email:    admin@example.com"
echo "  🔑 Password: admin"
echo ""
echo "Useful commands:"
echo "  📊 View logs:        docker compose logs -f"
echo "  🛑 Stop services:    docker compose down"
echo "  🔄 Restart:          docker compose restart"
echo "  🧹 Clean everything: docker compose down -v"
echo ""
echo "============================================================"
