#!/bin/bash
set -e

echo "============================================================"
echo "🔍 Verifying Full-Stack Setup"
echo "============================================================"
echo ""

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track failures
FAILED=0

# Function to check if container is running
check_container() {
    local container=$1
    local friendly_name=$2

    if docker compose ps | grep -q "$container.*Up"; then
        echo -e "${GREEN}✅ $friendly_name is running${NC}"
        return 0
    else
        echo -e "${RED}❌ $friendly_name is NOT running${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

# Function to check service health
check_service_health() {
    local service=$1
    local health_check=$2
    local friendly_name=$3

    if eval "$health_check" > /dev/null 2>&1; then
        echo -e "${GREEN}✅ $friendly_name is healthy${NC}"
        return 0
    else
        echo -e "${RED}❌ $friendly_name is NOT healthy${NC}"
        FAILED=$((FAILED + 1))
        return 1
    fi
}

echo -e "${YELLOW}Checking required containers...${NC}"
check_container "backend" "Backend API"
check_container "frontend" "Frontend (Vite)"
check_container "postgres" "PostgreSQL"
check_container "redis" "Redis"
check_container "ollama" "Ollama"
echo ""

# Check that nginx and other optional services are NOT running
echo -e "${YELLOW}Checking that extra services are NOT running...${NC}"
if docker compose ps | grep -q "nginx.*Up"; then
    echo -e "${RED}❌ Nginx should NOT be running (only frontend needed)${NC}"
    FAILED=$((FAILED + 1))
else
    echo -e "${GREEN}✅ Nginx correctly not running${NC}"
fi

if docker compose ps | grep -q "mongod\|mongodb.*Up"; then
    echo -e "${RED}❌ MongoDB should NOT be running${NC}"
    FAILED=$((FAILED + 1))
else
    echo -e "${GREEN}✅ MongoDB correctly not running${NC}"
fi

if docker compose ps | grep -q "neo4j.*Up"; then
    echo -e "${RED}❌ Neo4j should NOT be running${NC}"
    FAILED=$((FAILED + 1))
else
    echo -e "${GREEN}✅ Neo4j correctly not running${NC}"
fi
echo ""

# Check service health
echo -e "${YELLOW}Checking service health...${NC}"
check_service_health "backend" "docker compose exec -T backend curl -f http://localhost:8000/health 2>/dev/null" "Backend health endpoint"
check_service_health "frontend" "docker compose exec -T frontend curl -f http://localhost:5173 2>/dev/null" "Frontend dev server"
check_service_health "postgres" "docker compose exec -T postgres pg_isready -U postgres 2>/dev/null | grep -q 'accepting'" "PostgreSQL connection"
check_service_health "redis" "docker compose exec -T redis redis-cli ping 2>/dev/null | grep -q PONG" "Redis connection"
echo ""

# Check PostgreSQL has PGVector extension
echo -e "${YELLOW}Checking PostgreSQL extensions...${NC}"
if docker compose exec -T postgres psql -U postgres -d app_db -c "CREATE EXTENSION IF NOT EXISTS vector;" > /dev/null 2>&1; then
    echo -e "${GREEN}✅ PostgreSQL has PGVector extension${NC}"
else
    echo -e "${RED}❌ PostgreSQL does NOT have PGVector extension${NC}"
    FAILED=$((FAILED + 1))
fi
echo ""

# Check Ollama models
echo -e "${YELLOW}Checking Ollama models...${NC}"
OLLAMA_MODELS=$(docker compose exec -T ollama ollama list 2>/dev/null || echo "")

if echo "$OLLAMA_MODELS" | grep -q "phi3"; then
    echo -e "${GREEN}✅ phi3 model is available${NC}"
else
    echo -e "${RED}❌ phi3 model is NOT available${NC}"
    FAILED=$((FAILED + 1))
fi

if echo "$OLLAMA_MODELS" | grep -q "nomic-embed-text"; then
    echo -e "${GREEN}✅ nomic-embed-text model is available${NC}"
else
    echo -e "${RED}❌ nomic-embed-text model is NOT available${NC}"
    FAILED=$((FAILED + 1))
fi
echo ""

# Summary
echo "============================================================"
if [ $FAILED -eq 0 ]; then
    echo -e "${GREEN}✅ All checks passed! Full-stack setup is working correctly.${NC}"
    echo "============================================================"
    echo ""
    echo "Access your application:"
    echo -e "  🌐 Frontend:     ${GREEN}http://localhost:5173${NC}"
    echo -e "  🔧 Backend API:  ${GREEN}http://localhost:8000${NC}"
    echo -e "  📚 API Docs:     ${GREEN}http://localhost:8000/docs${NC}"
    echo -e "  🤖 Ollama:       ${GREEN}http://localhost:11434${NC}"
    echo ""
    exit 0
else
    echo -e "${RED}❌ $FAILED check(s) failed${NC}"
    echo "============================================================"
    echo ""
    echo "Troubleshooting:"
    echo "  1. Check logs: docker compose logs -f [SERVICE]"
    echo "  2. Verify all services started: docker compose ps"
    echo "  3. Re-run setup: ./scripts/quick-start.sh"
    echo ""
    exit 1
fi
