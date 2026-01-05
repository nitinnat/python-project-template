# Makefile for One-Stop RAG
.PHONY: help quickstart configure dev prod down clean logs test lint format migrate migrate-create shell db-shell

# Default target
help:
	@echo "One-Stop RAG - Available Commands:"
	@echo ""
	@echo "  make quickstart [PROFILE] - Interactive quick start (or use preset: fullstack, minimal, ai-local)"
	@echo "  make dev          - Start development environment (requires .env)"
	@echo "  make prod         - Start production environment (requires .env)"
	@echo "  make down         - Stop all services"
	@echo "  make clean        - Stop services and remove volumes"
	@echo "  make logs         - View logs (add SERVICE=backend to filter)"
	@echo "  make test         - Run backend tests"
	@echo "  make lint         - Run linters (backend and frontend)"
	@echo "  make format       - Format code (backend and frontend)"
	@echo "  make migrate      - Run database migrations"
	@echo "  make migrate-create MSG=\"message\" - Create new migration"
	@echo "  make shell        - Open backend shell"
	@echo "  make db-shell     - Open PostgreSQL shell"
	@echo ""

# Quick start with optional preset
quickstart:
	@chmod +x scripts/quick-start.sh
	@if [ -n "$(PROFILE)" ]; then \
		./scripts/quick-start.sh --preset $(PROFILE) --no-interactive; \
	else \
		./scripts/quick-start.sh; \
	fi

# Generate Docker Compose profiles based on .env
configure:
	@echo "Generating Docker Compose profiles from .env..."
	@chmod +x scripts/generate-profiles.sh
	@echo "Configuration ready!"

# Start development environment
dev: configure
	@echo "Starting development environment..."
	@PROFILES=$$(./scripts/generate-profiles.sh); \
	docker compose -f docker-compose.yml -f docker-compose.dev.yml $$PROFILES up

# Start development environment in background
dev-bg: configure
	@echo "Starting development environment in background..."
	@PROFILES=$$(./scripts/generate-profiles.sh); \
	docker compose -f docker-compose.yml -f docker-compose.dev.yml $$PROFILES up -d

# Start production environment
prod: configure
	@echo "Starting production environment..."
	@PROFILES=$$(./scripts/generate-profiles.sh); \
	docker compose -f docker-compose.yml -f docker-compose.prod.yml $$PROFILES up -d

# Stop all services
down:
	@echo "Stopping all services..."
	@docker compose --profile '*' down

# Stop all services and remove volumes
clean:
	@echo "Stopping all services and removing volumes..."
	@docker compose --profile '*' down -v
	@echo "Cleaning Python cache..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@echo "Cleaning node_modules..."
	@find . -type d -name "node_modules" -prune -exec rm -rf {} + 2>/dev/null || true

# View logs
logs:
	@if [ -z "$(SERVICE)" ]; then \
		docker compose logs -f; \
	else \
		docker compose logs -f $(SERVICE); \
	fi

# Run backend tests
test:
	@echo "Running backend tests..."
	@docker compose exec backend pytest -v

# Run backend tests with coverage
test-cov:
	@echo "Running backend tests with coverage..."
	@docker compose exec backend pytest --cov=app --cov-report=html --cov-report=term

# Run linters
lint:
	@echo "Running backend linter (ruff)..."
	@docker compose exec backend ruff check .
	@echo "Running backend type checker (mypy)..."
	@docker compose exec backend mypy app
	@echo "Running frontend linter (eslint)..."
	@cd frontend && npm run lint

# Format code
format:
	@echo "Formatting backend code (black + ruff)..."
	@docker compose exec backend black .
	@docker compose exec backend ruff check --fix .
	@echo "Formatting frontend code (prettier)..."
	@cd frontend && npm run format

# Run database migrations
migrate:
	@echo "Running database migrations..."
	@docker compose exec backend alembic upgrade head

# Create new migration
migrate-create:
	@if [ -z "$(MSG)" ]; then \
		echo "Error: MSG is required. Usage: make migrate-create MSG=\"your message\""; \
		exit 1; \
	fi
	@echo "Creating new migration: $(MSG)"
	@docker compose exec backend alembic revision --autogenerate -m "$(MSG)"

# Rollback migration
migrate-rollback:
	@echo "Rolling back last migration..."
	@docker compose exec backend alembic downgrade -1

# Open backend shell
shell:
	@docker compose exec backend /bin/bash

# Open PostgreSQL shell
db-shell:
	@docker compose exec postgres psql -U postgres -d app_db

# Open Python REPL with app context
python-shell:
	@docker compose exec backend python

# Rebuild services
rebuild:
	@echo "Rebuilding services..."
	@PROFILES=$$(./scripts/generate-profiles.sh); \
	docker compose -f docker-compose.yml -f docker-compose.dev.yml $$PROFILES build

# Restart specific service
restart:
	@if [ -z "$(SERVICE)" ]; then \
		echo "Error: SERVICE is required. Usage: make restart SERVICE=backend"; \
		exit 1; \
	fi
	@echo "Restarting $(SERVICE)..."
	@docker compose restart $(SERVICE)

# View running containers
ps:
	@docker compose ps

# Initialize database with seed data
seed:
	@echo "Seeding database..."
	@docker compose exec backend python scripts/seed_data.py

# Initialize feature flags
seed-flags:
	@echo "Initializing feature flags..."
	@docker compose exec backend python scripts/seed_feature_flags.py

# Install backend dependencies
install-backend:
	@echo "Installing backend dependencies..."
	@docker compose exec backend poetry install

# Install frontend dependencies
install-frontend:
	@echo "Installing frontend dependencies..."
	@docker compose exec frontend npm install

# Build frontend for production
build-frontend:
	@echo "Building frontend for production..."
	@docker compose exec frontend npm run build

# Check service health
health:
	@echo "Checking service health..."
	@curl -s http://localhost:8000/health | jq '.' || echo "Backend not responding"
	@curl -s http://localhost:8000/api/v1/admin/health | jq '.' || echo "Health endpoint requires authentication"

# Setup pre-commit hooks
setup-hooks:
	@echo "Setting up pre-commit hooks..."
	@pip install pre-commit
	@pre-commit install
	@echo "Pre-commit hooks installed!"

# View resource usage
stats:
	@docker stats --no-stream

# Prune Docker resources
prune:
	@echo "Pruning unused Docker resources..."
	@docker system prune -f
	@docker volume prune -f
