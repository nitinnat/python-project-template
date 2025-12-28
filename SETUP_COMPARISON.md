# Setup Comparison Guide

Choose the right setup for your needs.

## Quick Comparison

| Feature | Full Setup | Minimal Setup | Backend Only |
|---------|-----------|---------------|--------------|
| **Containers** | 6 | 3 | 3 |
| **Backend API** | ✅ | ✅ | ✅ |
| **Frontend UI** | ✅ (Docker) | ❌ (run locally) | ❌ |
| **PostgreSQL** | ✅ | ✅ | ✅ |
| **Redis** | ✅ | ✅ | ✅ |
| **Nginx** | ✅ | ❌ | ❌ |
| **MongoDB** | Optional | ❌ | ❌ |
| **Neo4j** | Optional | ❌ | ❌ |
| **RabbitMQ** | Optional | ❌ | ❌ |
| **Celery** | Optional | ❌ | ❌ |
| **Startup Time** | ~60s | ~20s | ~20s |
| **Memory Usage** | ~2-3 GB | ~500 MB | ~500 MB |
| **Best For** | Production simulation | Backend dev | API testing |

---

## Detailed Breakdown

### 1. Full Setup (Production-Like)

**What runs:**
- ✅ Backend (FastAPI)
- ✅ Frontend (React in Vite dev server)
- ✅ PostgreSQL
- ✅ Redis
- ✅ Nginx (reverse proxy)
- 🔄 MongoDB (if enabled)
- 🔄 Neo4j (if enabled)
- 🔄 RabbitMQ + Celery (if enabled)

**Command:**
```bash
./scripts/quick-start.sh
# or
make dev
# or
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Pros:**
- ✅ Complete production-like environment
- ✅ Test everything together
- ✅ Frontend and backend integrated
- ✅ Single URL (http://localhost:80)
- ✅ All features available

**Cons:**
- ❌ Slower startup
- ❌ More memory usage
- ❌ More containers to manage
- ❌ Overkill for simple API testing

**Use When:**
- Learning the full system
- Testing full-stack features
- Preparing for production deployment
- Demonstrating to stakeholders

---

### 2. Minimal Setup (Efficient Development)

**What runs:**
- ✅ Backend (FastAPI)
- ✅ PostgreSQL
- ✅ Redis

**Command:**
```bash
docker compose -f docker-compose.minimal.yml up
```

**Pros:**
- ✅ Fast startup (~20 seconds)
- ✅ Low memory usage (~500 MB)
- ✅ Simple to manage
- ✅ Perfect for backend development
- ✅ Can run frontend separately

**Cons:**
- ❌ No frontend in Docker
- ❌ No reverse proxy
- ❌ No optional services
- ❌ Frontend requires separate npm install

**Use When:**
- Developing backend features
- Testing API endpoints
- Running on limited hardware
- Just need database + API

**Frontend Options:**
```bash
# Option A: Run frontend locally
cd frontend
npm install
npm run dev
# Access at http://localhost:5173

# Option B: Use API docs only
# Access at http://localhost:8000/docs
```

---

### 3. Backend-Only (API Testing)

**What runs:**
- Same as Minimal (Backend + PostgreSQL + Redis)

**No Frontend:**
- Test via Swagger UI
- Use curl/Postman
- Import OpenAPI spec

**Command:**
```bash
docker compose -f docker-compose.minimal.yml up
```

**Pros:**
- ✅ Fastest testing
- ✅ Perfect for API development
- ✅ No frontend complexity
- ✅ Great for CI/CD testing

**Cons:**
- ❌ No UI to visualize
- ❌ Manual API testing required
- ❌ Harder for non-technical users

**Use When:**
- Developing API endpoints
- Writing backend tests
- Learning FastAPI
- Debugging backend issues

**Test via:**
- **Swagger UI**: http://localhost:8000/docs
- **curl**: See examples in SIMPLIFIED_TESTING.md
- **Postman**: Import http://localhost:8000/openapi.json

---

## Why Not One Container?

### The "All-in-One" Myth

Some developers ask: "Can't we put everything in one container?"

**Technically: Yes** (with significant effort)
**Should you: No**

### Problems with One Container:

1. **Process Management**
   - Docker designed for "one process per container"
   - Need supervisord/systemd to manage multiple processes
   - Logs become messy and hard to debug

2. **Architecture**
   ```
   One Container:
   ┌─────────────────────────┐
   │  PostgreSQL             │
   │  Redis                  │  ← All competing for resources
   │  Backend                │  ← Can't scale independently
   │  Frontend               │  ← Single point of failure
   │  Nginx                  │
   └─────────────────────────┘

   Multiple Containers:
   ┌─────────┐  ┌─────────┐  ┌─────────┐
   │ Backend │  │   DB    │  │Frontend │  ← Each scalable
   └─────────┘  └─────────┘  └─────────┘  ← Isolated failures
   ```

3. **Scalability**
   - Can't scale backend without scaling database
   - Can't replace PostgreSQL with managed service
   - Can't deploy frontend to CDN

4. **Development**
   - Restart one service = restart all
   - Build time increases
   - Hot-reload doesn't work well
   - Harder to debug

5. **Production**
   - Industry standard uses microservices
   - Cloud platforms expect separate services
   - Monitoring/logging becomes complex

### If You Want Simpler Than Docker...

Use **SQLite + Single FastAPI Server:**

```bash
# No Docker needed!
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
```

This gives you:
- ✅ Zero containers
- ✅ SQLite instead of PostgreSQL
- ✅ No Redis (optional)
- ✅ FastAPI serves frontend static files

But you lose:
- ❌ Production-ready architecture
- ❌ Scalability
- ❌ Feature flags
- ❌ Multiple databases
- ❌ Background tasks

---

## Resource Usage Comparison

Measured on MacBook Pro M1:

| Setup | RAM | CPU | Startup | Containers |
|-------|-----|-----|---------|-----------|
| **Full** | 2.5 GB | 30% | 60s | 6 |
| **Minimal** | 500 MB | 10% | 20s | 3 |
| **Local** | 300 MB | 5% | 5s | 0 |

---

## Recommendations

### For Your Use Case

**Just Learning?**
→ Start with **Minimal Setup**
→ Add complexity as needed

**Building a Real Project?**
→ Use **Full Setup**
→ Learn production patterns early

**Testing APIs Only?**
→ Use **Backend-Only**
→ Swagger UI is your friend

**Limited Hardware?**
→ Use **Minimal Setup**
→ Or run locally without Docker

**Preparing for Production?**
→ Use **Full Setup**
→ Mirror production architecture

---

## Migration Path

Start simple, grow as needed:

```
Week 1: Backend-Only
  ↓ (Add frontend)
Week 2: Minimal Setup + Local Frontend
  ↓ (Containerize frontend)
Week 3: Full Setup
  ↓ (Add optional services)
Week 4: Full Setup + MongoDB + Neo4j + Celery
```

---

## Quick Decision Tree

```
Do you need the frontend UI?
├─ YES → Do you want it in Docker?
│        ├─ YES → Full Setup
│        └─ NO  → Minimal Setup + npm run dev
└─ NO  → Backend-Only (Minimal Setup + Swagger)

Do you have limited RAM (<4GB)?
└─ YES → Minimal Setup

Are you learning the full system?
└─ YES → Full Setup

Just testing APIs?
└─ YES → Backend-Only
```

---

## Commands Quick Reference

```bash
# Full Setup
./scripts/quick-start.sh
# or
make dev

# Minimal Setup
docker compose -f docker-compose.minimal.yml up
docker compose -f docker-compose.minimal.yml exec backend alembic upgrade head
docker compose -f docker-compose.minimal.yml exec backend python scripts/seed_data.py

# Local Frontend (with Minimal)
cd frontend && npm install && npm run dev

# Stop Everything
docker compose down                                      # Full
docker compose -f docker-compose.minimal.yml down        # Minimal

# Clean Everything
docker compose down -v                                   # Full
docker compose -f docker-compose.minimal.yml down -v     # Minimal
```

---

**Choose what works for you now. You can always switch later!** 🚀
