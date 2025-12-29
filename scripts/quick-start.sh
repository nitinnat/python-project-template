#!/bin/bash
set -e

echo "============================================================"
echo "🚀 Python Full-Stack Project Template - Quick Start"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Parse arguments
PROFILE="${1:-default}"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Error: Docker is not running. Please start Docker Desktop."
    exit 1
fi

echo -e "${GREEN}✅ Docker is running${NC}"
echo ""

# Setup environment files
echo -e "${BLUE}📋 Setting up environment...${NC}"

# Copy .env.example to .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env.example .env
    echo -e "${GREEN}✅ Created .env from .env.example${NC}"
else
    echo -e "${YELLOW}ℹ️  .env already exists, skipping${NC}"
fi

# Setup features.env based on profile
if [ "$PROFILE" != "default" ]; then
    PROFILE_FILE="profiles/${PROFILE}.env"
    if [ ! -f "$PROFILE_FILE" ]; then
        echo -e "${RED}❌ Error: Profile '${PROFILE}' not found at ${PROFILE_FILE}${NC}"
        echo ""
        echo "Available profiles:"
        ls -1 profiles/*.env | sed 's|profiles/||' | sed 's|.env||' | sed 's/^/  - /'
        exit 1
    fi
    cp "$PROFILE_FILE" features.env
    echo -e "${GREEN}✅ Using profile: ${PROFILE}${NC}"
else
    # Use default features.env if it exists, otherwise create from fullstack profile (Frontend + Backend + Nginx + Postgres + PGVector + Ollama)
    if [ ! -f features.env ]; then
        cp profiles/fullstack.env features.env
        echo -e "${GREEN}✅ Created features.env from fullstack profile (default: Frontend, Backend, Nginx, Postgres+PGVector, Ollama with phi3 + nomic-embed-text)${NC}"
    else
        echo -e "${YELLOW}ℹ️  features.env already exists, skipping${NC}"
    fi
fi
echo ""

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
echo -e "${BLUE}📦 Starting Docker services...${NC}"
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
echo -e "  🌐 Frontend:     ${BLUE}http://localhost:80${NC}"
echo -e "  🔧 Backend API:  ${BLUE}http://localhost:8000${NC}"
echo -e "  📚 API Docs:     ${BLUE}http://localhost:8000/docs${NC}"
echo -e "  👨‍💼 Admin Panel:  ${BLUE}http://localhost:80/admin${NC}"
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
