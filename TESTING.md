# Testing Documentation

> Heads up: this guide still references auth endpoints, admin credentials, and containers (frontend/nginx) that are not present in the current backend. The backend only exposes `/health`, `/api/v1/documents/*` (requires MongoDB profile), and `/api/v1/graph/*` (requires Neo4j profile); auth flows will fail until reintroduced.

This document provides comprehensive testing information for the Python Project Template.

## Current Status

✅ **All Docker containers are running and healthy**
- Backend API: Operational
- PostgreSQL: Operational
- Redis: Operational
- Database migrations: Applied
- Seed data: Loaded

## Container Status

```bash
docker compose -f docker-compose.minimal.yml ps
```

| Container | Status | Ports |
|-----------|--------|-------|
| backend_minimal | Up (healthy) | 0.0.0.0:8000->8000/tcp |
| postgres_minimal | Up (healthy) | 0.0.0.0:5432->5432/tcp |
| redis_minimal | Up (healthy) | 0.0.0.0:6379->6379/tcp |

## Quick Start Commands

### Start Services
```bash
# Minimal setup (3 containers: backend, postgres, redis)
docker compose -f docker-compose.minimal.yml up -d

# Check status
docker compose -f docker-compose.minimal.yml ps

# View logs
docker compose -f docker-compose.minimal.yml logs -f backend
```

### Stop Services
```bash
docker compose -f docker-compose.minimal.yml down

# Stop and remove volumes (clean slate)
docker compose -f docker-compose.minimal.yml down -v
```

## Database Setup

### Migrations
```bash
# Generate new migration
docker compose -f docker-compose.minimal.yml exec backend alembic revision --autogenerate -m "Description"

# Apply migrations
docker compose -f docker-compose.minimal.yml exec backend alembic upgrade head

# Rollback migration
docker compose -f docker-compose.minimal.yml exec backend alembic downgrade -1
```

### Seed Data
```bash
# Seed the database with initial data
docker compose -f docker-compose.minimal.yml exec backend python scripts/seed_data.py
```

**Default Credentials:**
- Email: `admin@example.com`
- Password: `admin`

**Seeded Data:**
- 1 admin user
- 12 feature flags (covering databases, LLMs, features)

## API Testing

### Health Check
```bash
curl http://localhost:8000/health
```

**Expected Response:**
```json
{
  "status": "healthy",
  "service": "python-project-template",
  "version": "1.0.0"
}
```

### API Documentation
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### LLM Smoke Tests (Gemini + Ollama)
Note: after changing `.env`, recreate the backend container (`docker compose up -d --force-recreate backend`) so new keys are injected.

**Gemini (Google)**
```bash
docker compose exec backend python - <<'PY'
import asyncio
from app.helpers.llm.gemini_client import gemini_client
async def main():
    result = await gemini_client.generate_content("Say hello from the template.")
    print(result["content"])
asyncio.run(main())
PY
```

**Ollama (local)**
```bash
docker compose exec backend curl -s -X POST http://ollama:11434/api/generate \
  -d '{"model":"qwen2.5:7b","prompt":"Say hello"}'
```

### Authentication Flow

#### 1. Login
```bash
curl -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{
    "email": "admin@example.com",
    "password": "admin"
  }'
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "refresh_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### 2. Get Current User
```bash
# Replace {TOKEN} with actual access_token from login
curl -X GET 'http://localhost:8000/api/v1/users/me' \
  -H 'Authorization: Bearer {TOKEN}'
```

**Response:**
```json
{
  "email": "admin@example.com",
  "full_name": null,
  "id": 1,
  "role": "admin",
  "is_active": true,
  "is_verified": false,
  "created_at": "2025-12-28T01:17:03.020523Z",
  "updated_at": null
}
```

### Available Endpoints

#### Public Endpoints
- `GET /health` - Health check
- `GET /docs` - Swagger UI
- `GET /redoc` - ReDoc documentation
- `POST /api/v1/auth/login` - User login
- `POST /api/v1/auth/register` - User registration

#### Protected Endpoints (require authentication)
- `GET /api/v1/users/me` - Get current user
- `PUT /api/v1/users/me` - Update current user
- `GET /api/v1/users` - List users (admin only)
- `GET /api/v1/admin/feature-flags` - List feature flags (admin only)
- `PUT /api/v1/admin/feature-flags/{key}` - Update feature flag (admin only)

## Testing with curl

### Complete Test Flow
```bash
# 1. Health check
curl http://localhost:8000/health

# 2. Login and save token
curl -X POST 'http://localhost:8000/api/v1/auth/login' \
  -H 'Content-Type: application/json' \
  -d '{"email":"admin@example.com","password":"admin"}' \
  > /tmp/token.json

# 3. Extract token (requires jq or python)
TOKEN=$(python3 -c "import json; print(json.load(open('/tmp/token.json'))['access_token'])")

# 4. Get current user
curl -X GET 'http://localhost:8000/api/v1/users/me' \
  -H "Authorization: Bearer $TOKEN"

# 5. List feature flags (admin only)
curl -X GET 'http://localhost:8000/api/v1/admin/feature-flags' \
  -H "Authorization: Bearer $TOKEN"
```

## Database Access

### PostgreSQL
```bash
# Connect to PostgreSQL
docker compose -f docker-compose.minimal.yml exec postgres psql -U postgres -d app_db

# Run SQL query
docker compose -f docker-compose.minimal.yml exec postgres \
  psql -U postgres -d app_db -c "SELECT * FROM users;"
```

### Redis
```bash
# Connect to Redis CLI
docker compose -f docker-compose.minimal.yml exec redis redis-cli

# Common commands
> PING
> KEYS *
> GET key_name
```

## Troubleshooting

### Container Issues

**Container won't start:**
```bash
# Check logs
docker compose -f docker-compose.minimal.yml logs backend

# Rebuild container
docker compose -f docker-compose.minimal.yml build backend --no-cache
docker compose -f docker-compose.minimal.yml up -d backend
```

**Port already in use:**
```bash
# Find process using port 8000
lsof -i :8000

# Stop conflicting containers
docker ps -a
docker stop <container_id>
```

### Database Issues

**Reset database:**
```bash
# Stop services and remove volumes
docker compose -f docker-compose.minimal.yml down -v

# Start fresh
docker compose -f docker-compose.minimal.yml up -d

# Wait for containers to be healthy
sleep 10

# Run migrations
docker compose -f docker-compose.minimal.yml exec backend alembic upgrade head

# Seed data
docker compose -f docker-compose.minimal.yml exec backend python scripts/seed_data.py
```

**Migration conflicts:**
```bash
# List migrations
docker compose -f docker-compose.minimal.yml exec backend alembic history

# Stamp database to specific revision
docker compose -f docker-compose.minimal.yml exec backend alembic stamp head
```

## Known Issues and Fixes

### Issue: Bcrypt password hashing error
**Fixed:** Switched from passlib to direct bcrypt usage in [security.py](backend/app/core/security.py:10-60)

### Issue: SQLAlchemy reserved name 'metadata'
**Fixed:** Renamed FeatureFlag.metadata to FeatureFlag.config in [feature_flag.py](backend/app/models/postgres/feature_flag.py:53)

### Issue: Missing settings fields
**Fixed:** Added all required settings to [settings.py](backend/app/config/settings.py:20-101):
- `app_version`
- `api_v1_prefix`
- `log_level`
- `enable_redis`
- `cors_allow_credentials`
- `cors_allow_methods`
- `cors_allow_headers`
- `otel_enabled`
- `otel_service_name`

### Issue: Poetry lock file not found during build
**Fixed:** Modified [Dockerfile](backend/Dockerfile:24-30) to generate lock file during build

### Issue: PostgreSQL "SELECT 1" not executable
**Fixed:** Added `text()` wrapper in [postgres.py](backend/app/helpers/postgres.py:77)

## Development Workflow

### Making Code Changes

1. **Edit code** in your IDE
2. **Container auto-reloads** (uvicorn with --reload in dev mode)
3. **Test changes** via API endpoints
4. **Check logs** if issues occur

### Adding New Dependencies

```bash
# Add to pyproject.toml
cd backend
poetry add package-name

# Rebuild container
cd ..
docker compose -f docker-compose.minimal.yml build backend
docker compose -f docker-compose.minimal.yml up -d backend
```

### Creating Database Migrations

```bash
# 1. Modify models in backend/app/models/postgres/
# 2. Generate migration
docker compose -f docker-compose.minimal.yml exec backend \
  alembic revision --autogenerate -m "Add new field to users"

# 3. Review migration file in backend/alembic/versions/
# 4. Apply migration
docker compose -f docker-compose.minimal.yml exec backend alembic upgrade head
```

## Testing Checklist

- [ ] All containers are healthy
- [ ] Health endpoint returns 200
- [ ] Swagger UI loads at /docs
- [ ] Login with admin credentials succeeds
- [ ] JWT token is returned
- [ ] Protected endpoints work with valid token
- [ ] Database has users and feature_flags tables
- [ ] Seed data is present in database

## Next Steps

After confirming the minimal setup works:

1. **Run full setup** with all services:
   ```bash
   ./scripts/quick-start.sh
   ```

2. **Add frontend** to test full-stack integration

3. **Enable optional services** in [features.env](features.env):
   - MongoDB
   - Neo4j
   - RabbitMQ + Celery
   - LLM providers

4. **Write tests** using pytest framework

5. **Set up CI/CD** for automated testing

## Configuration Files

### Key Files Modified
- [backend/Dockerfile](backend/Dockerfile) - Poetry lock file generation
- [backend/app/config/settings.py](backend/app/config/settings.py) - All settings consolidated
- [backend/app/core/security.py](backend/app/core/security.py) - Direct bcrypt usage
- [backend/app/helpers/postgres.py](backend/app/helpers/postgres.py) - SQL text() wrapper
- [backend/app/models/postgres/feature_flag.py](backend/app/models/postgres/feature_flag.py) - Config field
- [backend/pyproject.toml](backend/pyproject.toml) - Email validator added
- [backend/scripts/seed_data.py](backend/scripts/seed_data.py) - Updated schema
- [docker-compose.minimal.yml](docker-compose.minimal.yml) - 3-container setup

### Environment Files
- `.env` - Main environment variables
- `features.env` - Feature flags for optional services
- `backend/.env` - Backend-specific settings

## Performance Notes

- **Startup time**: ~20 seconds for minimal setup
- **Memory usage**: ~500 MB total
- **Rebuild time**: ~8 minutes (first build), ~2 minutes (cached)
- **Health check**: 30s interval, 40s start period

## References

- [SETUP_COMPARISON.md](SETUP_COMPARISON.md) - Comparison of different setups
- [TECHNICAL_DESIGN.md](TECHNICAL_DESIGN.md) - Full technical design
- [IMPLEMENTATION_LOG.md](IMPLEMENTATION_LOG.md) - Implementation progress
- [README.md](README.md) - Project overview
