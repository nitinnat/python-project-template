# Testing Guide

> Heads up: the login/auth/admin flows described below are not available in the current backend. Only `/health`, `/api/v1/documents/*` (needs MongoDB profile), and `/api/v1/graph/*` (needs Neo4j profile) are implemented today; adjust expectations before running the steps.

Quick guide to test the Python Full-Stack Project Template.

## Prerequisites

Ensure you have:
- ✅ Docker Desktop running
- ✅ Docker Compose installed
- ✅ Ports 80, 8000, 5432, 6379 available

## Step-by-Step Testing

### 1. Start the Application

```bash
# From the project root directory
make dev

# Or without make:
docker compose -f docker-compose.yml -f docker-compose.dev.yml up
```

**Expected Output:**
```
✔ Container postgres       Started
✔ Container redis          Started
✔ Container backend        Started
✔ Container frontend       Started
✔ Container nginx          Started
```

Wait for all services to be healthy. You should see:
- `backend_1    | INFO:     Application startup complete.`
- `frontend_1   | VITE ready in XXX ms`

### 2. Create Database Tables

In a **new terminal** (keep the first one running):

```bash
# Navigate to project directory
cd /Users/nitinnataraj/Documents/Projects/python-project-template

# Run migrations to create tables
docker compose exec backend alembic upgrade head
```

**Expected Output:**
```
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, initial tables
```

### 3. Seed Initial Data

```bash
# Create admin user and feature flags
docker compose exec backend python scripts/seed_data.py
```

**Expected Output:**
```
============================================================
🌱 Seeding database...
============================================================
Creating default users...
  ✅ Created admin user: admin@example.com / admin
Creating default feature flags...
  ✅ Created 12 feature flags
============================================================
✅ Seeding completed successfully!
============================================================

Default credentials:
  Email: admin@example.com
  Password: admin

Access the app at: http://localhost:80
Access the admin panel at: http://localhost:80/admin
```

### 4. Test the Frontend

Open your browser to: **http://localhost:80**

**Test Login:**
1. You should see a login page
2. Enter credentials:
   - Email: `admin@example.com`
   - Password: `admin`
3. Click "Sign In"
4. You should be redirected to the Dashboard

**Test Dashboard:**
- Should display "Welcome, admin@example.com!"
- Shows your role: "admin"
- Shows account status: "Active"

**Test Admin Panel:**
1. Click "Admin" in the navigation bar
2. You should see the Admin Panel with sidebar

**Test Feature Flags:**
1. Click "Feature Flags" in the sidebar
2. You should see feature flags grouped by category:
   - Database
   - Feature
   - LLM
3. Toggle a flag (e.g., `feature.vector_search`)
4. The flag should update in real-time

**Test Service Health:**
1. Click "Service Health" in the sidebar
2. You should see health cards for:
   - ✅ PostgreSQL (healthy)
   - ✅ Redis (healthy)
3. Each card shows:
   - Status
   - Latency
   - Connections

### 5. Test the Backend API

Open: **http://localhost:8000/docs**

You should see the **Swagger UI** with all API endpoints.

**Test Authentication:**
1. Expand `POST /api/v1/auth/login`
2. Click "Try it out"
3. Enter credentials:
   ```json
   {
     "username": "admin@example.com",
     "password": "admin"
   }
   ```
4. Click "Execute"
5. You should get a response with `access_token` and `refresh_token`

**Test Authenticated Endpoint:**
1. Copy the `access_token` from the login response
2. Click the "Authorize" button at the top
3. Enter: `Bearer <your_access_token>`
4. Click "Authorize"
5. Expand `GET /api/v1/auth/me`
6. Click "Try it out" → "Execute"
7. You should see your user details

**Test Admin Endpoints:**
1. Expand `GET /api/v1/admin/feature-flags`
2. Click "Try it out" → "Execute"
3. You should see the list of feature flags
4. Try `GET /api/v1/admin/health`
5. You should see service health status

### 6. Verify Database

```bash
# Connect to PostgreSQL
docker compose exec postgres psql -U postgres -d app_db

# List tables
\dt

# View users
SELECT id, email, role, is_active FROM users;

# View feature flags
SELECT key, enabled, category FROM feature_flags;

# Exit
\q
```

**Expected Tables:**
- `users`
- `feature_flags`
- `audit_logs`
- `alembic_version`

### 7. Check Logs

```bash
# Backend logs
docker compose logs backend

# Frontend logs
docker compose logs frontend

# All logs
docker compose logs
```

## Common Issues & Solutions

### Issue: "Port already in use"

**Solution:**
```bash
# Find process using the port (e.g., 8000)
lsof -i :8000

# Kill the process
kill -9 <PID>

# Or use different ports by editing docker-compose.dev.yml
```

### Issue: "Cannot connect to database"

**Solution:**
```bash
# Wait for PostgreSQL to fully start
docker compose logs postgres

# Should see: "database system is ready to accept connections"

# Restart backend
docker compose restart backend
```

### Issue: "Module not found" in backend

**Solution:**
```bash
# Rebuild backend
docker compose up --build backend
```

### Issue: Frontend showing blank page

**Solution:**
```bash
# Check frontend logs
docker compose logs frontend

# Rebuild frontend
docker compose up --build frontend

# Check browser console for errors (F12)
```

### Issue: "Unauthorized" when accessing admin endpoints

**Solution:**
1. Make sure you're logged in
2. Check that your user has `role: admin`
3. Verify the token is valid (not expired)
4. Re-login to get a fresh token

### Issue: Migrations fail

**Solution:**
```bash
# Drop all tables and start fresh
docker compose exec postgres psql -U postgres -d app_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"

# Run migrations again
docker compose exec backend alembic upgrade head

# Seed data again
docker compose exec backend python scripts/seed_data.py
```

## Testing Checklist

Use this checklist to verify everything is working:

- [ ] ✅ Docker services start successfully
- [ ] ✅ Backend responds at http://localhost:8000
- [ ] ✅ Frontend responds at http://localhost:80
- [ ] ✅ API docs accessible at http://localhost:8000/docs
- [ ] ✅ Database migrations run successfully
- [ ] ✅ Seed data script completes
- [ ] ✅ Can login with admin credentials
- [ ] ✅ Dashboard displays correctly
- [ ] ✅ Admin panel accessible
- [ ] ✅ Feature flags page shows flags
- [ ] ✅ Can toggle feature flags
- [ ] ✅ Service health page shows service status
- [ ] ✅ API authentication works
- [ ] ✅ Admin API endpoints work
- [ ] ✅ Database contains expected data
- [ ] ✅ No errors in backend logs
- [ ] ✅ No errors in frontend logs

## Next Steps After Testing

Once everything is working:

1. **Explore the Code**
   - Check `backend/app/` for backend code
   - Check `frontend/src/` for frontend code
   - Review `TECHNICAL_DESIGN.md` for architecture

2. **Customize**
   - Change admin password
   - Add your own models
   - Create new API endpoints
   - Add frontend pages

3. **Enable Optional Services**
   - Edit `features.env`
   - Enable MongoDB, Neo4j, RabbitMQ, etc.
   - Restart: `docker compose down && make dev`

4. **Deploy**
   - Review `docker-compose.prod.yml`
   - Set production environment variables
   - Deploy to your server

---

**Need Help?** Check the logs first, then review the README.md and TECHNICAL_DESIGN.md!
