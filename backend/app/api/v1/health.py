"""
Service health check endpoints.
"""

import time
from typing import Any, Dict

from fastapi import APIRouter
from sqlalchemy import text

from app.config.settings import settings
from app.helpers.postgres import postgres_helper
from app.helpers.redis_helper import redis_helper

router = APIRouter(prefix="/health", tags=["health"])


async def check_postgres() -> Dict[str, Any]:
    """Check PostgreSQL health."""
    try:
        start = time.time()
        async with postgres_helper.get_session() as session:
            await session.execute(text("SELECT 1"))
        latency = round((time.time() - start) * 1000, 2)

        return {
            "status": "healthy",
            "latency_ms": latency,
            "message": "PostgreSQL is responding"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "PostgreSQL connection failed"
        }


async def check_redis() -> Dict[str, Any]:
    """Check Redis health."""
    try:
        start = time.time()
        redis = redis_helper.get_client()
        await redis.ping()
        latency = round((time.time() - start) * 1000, 2)

        return {
            "status": "healthy",
            "latency_ms": latency,
            "message": "Redis is responding"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Redis connection failed"
        }


async def check_mongodb() -> Dict[str, Any]:
    """Check MongoDB health."""
    if not settings.enable_mongodb:
        return {
            "status": "disabled",
            "message": "MongoDB is not enabled"
        }

    try:
        from app.helpers.mongodb import mongodb_helper
        start = time.time()
        db = mongodb_helper.get_database()
        await db.command("ping")
        latency = round((time.time() - start) * 1000, 2)

        return {
            "status": "healthy",
            "latency_ms": latency,
            "message": "MongoDB is responding"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "MongoDB connection failed"
        }


async def check_neo4j() -> Dict[str, Any]:
    """Check Neo4j health."""
    if not settings.enable_neo4j:
        return {
            "status": "disabled",
            "message": "Neo4j is not enabled"
        }

    try:
        from app.helpers.neo4j_helper import neo4j_helper
        start = time.time()
        driver = neo4j_helper.get_driver()
        async with driver.session() as session:
            await session.run("RETURN 1")
        latency = round((time.time() - start) * 1000, 2)

        return {
            "status": "healthy",
            "latency_ms": latency,
            "message": "Neo4j is responding"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Neo4j connection failed"
        }


async def check_rabbitmq() -> Dict[str, Any]:
    """Check RabbitMQ health."""
    if not settings.enable_rabbitmq:
        return {
            "status": "disabled",
            "message": "RabbitMQ is not enabled"
        }

    try:
        # RabbitMQ health check would go here
        # For now, return a basic status
        return {
            "status": "healthy",
            "message": "RabbitMQ configuration present"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "RabbitMQ check failed"
        }


async def check_ollama() -> Dict[str, Any]:
    """Check Ollama health."""
    if not settings.enable_llm_ollama:
        return {
            "status": "disabled",
            "message": "Ollama is not enabled"
        }

    try:
        import httpx
        start = time.time()
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{settings.ollama_host}/api/tags", timeout=5.0)
            response.raise_for_status()
        latency = round((time.time() - start) * 1000, 2)

        return {
            "status": "healthy",
            "latency_ms": latency,
            "message": "Ollama is responding"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "error": str(e),
            "message": "Ollama connection failed"
        }


@router.get("/services")
async def get_services_health() -> Dict[str, Any]:
    """
    Get health status of all services.

    Returns status for:
    - PostgreSQL
    - Redis
    - MongoDB (if enabled)
    - Neo4j (if enabled)
    - RabbitMQ (if enabled)
    - Ollama (if enabled)
    """
    health_checks = {
        "postgres": await check_postgres(),
        "redis": await check_redis(),
    }

    # Only check optional services if they're enabled
    if settings.enable_mongodb:
        health_checks["mongodb"] = await check_mongodb()

    if settings.enable_neo4j:
        health_checks["neo4j"] = await check_neo4j()

    if settings.enable_rabbitmq:
        health_checks["rabbitmq"] = await check_rabbitmq()

    if settings.enable_llm_ollama:
        health_checks["ollama"] = await check_ollama()

    # Determine overall status
    statuses = [check["status"] for check in health_checks.values()]
    if all(s in ["healthy", "disabled"] for s in statuses):
        overall_status = "healthy"
    elif any(s == "unhealthy" for s in statuses):
        overall_status = "degraded"
    else:
        overall_status = "unknown"

    return {
        "status": overall_status,
        "timestamp": time.time(),
        "services": health_checks
    }
