# Simplified Testing Guide

If the full Docker setup feels overwhelming, here are simpler alternatives.

## Option 1: Minimal Docker (3 Containers)

**What runs**: Backend + PostgreSQL + Redis only
**What's excluded**: Frontend, Nginx, MongoDB, Neo4j, RabbitMQ

### Start Minimal Setup

```bash
# Start just the backend and required databases
docker compose -f docker-compose.minimal.yml up

# In a new terminal, run migrations
docker compose -f docker-compose.minimal.yml exec backend alembic upgrade head

# Seed data
docker compose -f docker-compose.minimal.yml exec backend python scripts/seed_data.py
```

### Test the Backend API

1. **API Docs**: http://localhost:8000/docs
2. **Health Check**: http://localhost:8000/health
3. **Login**: POST to http://localhost:8000/api/v1/auth/login

### Run Frontend Locally (Optional)

```bash
# Navigate to frontend
cd frontend

# Install dependencies (first time only)
npm install

# Start dev server
npm run dev
```

Frontend will be at: http://localhost:5173

---

## Option 2: Backend-Only (No Frontend)

**What runs**: Just Backend + PostgreSQL + Redis
**Test via**: API docs (Swagger UI) or curl/Postman

### Start Services

```bash
docker compose -f docker-compose.minimal.yml up
```

### Test Everything via API

**1. Login**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@example.com&password=admin"
```

**2. Get User Info**
```bash
# Use the token from step 1
curl -X GET http://localhost:8000/api/v1/auth/me \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**3. Get Feature Flags (Admin)**
```bash
curl -X GET http://localhost:8000/api/v1/admin/feature-flags \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**4. Check Service Health**
```bash
curl -X GET http://localhost:8000/api/v1/admin/health \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

---

## Option 3: Use API Client (Postman/Insomnia)

1. Import OpenAPI spec: http://localhost:8000/openapi.json
2. Set base URL: http://localhost:8000/api/v1
3. Test all endpoints visually

---

## Container Count Comparison

| Setup | Containers | Use Case |
|-------|-----------|----------|
| **Full** | 6 | Production-like testing with frontend |
| **Minimal** | 3 | Backend API development |
| **Backend + Local Frontend** | 3 + npm | Full-stack with less Docker |
| **Backend Only** | 3 | Pure API testing |

---

## Why Not ONE Container?

### Technical Challenges

1. **Process Management**: Docker expects one main process. Running Postgres + Redis + Backend + Frontend requires a process manager like supervisord
2. **Port Conflicts**: All services need different ports
3. **Logs**: Mixed logs from all services = harder to debug
4. **Updates**: Changing one service requires rebuilding everything
5. **Resource Limits**: Can't set different limits per service

### If You REALLY Want One Container...

You'd need to:
- Use SQLite instead of PostgreSQL (single file database)
- Remove Redis (or use in-memory alternative)
- Build frontend and serve static files from backend
- Remove Nginx

This would defeat the purpose of the template (production-ready architecture).

---

## Recommended Approach for You

Based on your question, I recommend:

### **For Quick Testing**
```bash
# Minimal setup (3 containers)
docker compose -f docker-compose.minimal.yml up

# Test via Swagger UI
open http://localhost:8000/docs
```

### **For Full-Stack Development**
```bash
# Backend in Docker
docker compose -f docker-compose.minimal.yml up

# Frontend on your machine
cd frontend
npm install
npm run dev

# Access at http://localhost:5173
```

### **For Learning the Full System**
```bash
# Full setup (6 containers)
./scripts/quick-start.sh

# Explore all features
```

---

## Summary

- ❌ **One container for everything**: Technically possible but defeats the purpose
- ✅ **Minimal setup (3 containers)**: Best for backend testing
- ✅ **Full setup (6 containers)**: Best for learning/production simulation
- ✅ **Hybrid (Docker backend + local frontend)**: Best for frontend development

**Choose the approach that fits your current goal!**
