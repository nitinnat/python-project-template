"""
Main FastAPI application entry point.

Features:
- CORS middleware for frontend integration
- Exception handlers for standardized error responses
- Health check endpoints
- OpenTelemetry instrumentation
- API versioning (v1)
- Automatic OpenAPI documentation
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.config.settings import settings
from app.core.logging import get_logger, setup_logging
from app.core.telemetry import setup_telemetry

# Setup logging
setup_logging()
logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan manager.

    Handles startup and shutdown events for:
    - Database connections
    - Redis connections
    - Background tasks
    - Telemetry
    """
    # Startup
    logger.info(f"Starting {settings.app_name} v{settings.app_version}")
    logger.info(f"Environment: {settings.app_env}")

    # Initialize telemetry
    setup_telemetry()

    # Initialize database connections
    await initialize_services()

    logger.info("Application startup complete")

    yield

    # Shutdown
    logger.info("Shutting down application")
    await shutdown_services()
    logger.info("Application shutdown complete")


async def initialize_services():
    """Initialize all enabled services based on feature flags."""
    from app.config.settings import settings

    # Always initialize core services
    if settings.enable_postgres:
        try:
            from app.helpers.postgres import postgres_helper

            await postgres_helper.initialize()
            logger.info("PostgreSQL initialized")
        except Exception as e:
            logger.error(f"Failed to initialize PostgreSQL: {e}")

    if settings.enable_redis:
        try:
            from app.helpers.redis_helper import redis_helper

            await redis_helper.initialize()
            logger.info("Redis initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Redis: {e}")

    # Optional services
    if settings.enable_mongodb:
        try:
            from app.helpers.mongodb import mongodb_helper

            await mongodb_helper.initialize()
            logger.info("MongoDB initialized")
        except Exception as e:
            logger.error(f"Failed to initialize MongoDB: {e}")

    if settings.enable_neo4j:
        try:
            from app.helpers.neo4j_helper import neo4j_helper

            await neo4j_helper.initialize()
            logger.info("Neo4j initialized")
        except Exception as e:
            logger.error(f"Failed to initialize Neo4j: {e}")

    if settings.enable_rabbitmq:
        try:
            from app.helpers.rabbitmq import rabbitmq_helper

            await rabbitmq_helper.initialize()
            logger.info("RabbitMQ initialized")
        except Exception as e:
            logger.error(f"Failed to initialize RabbitMQ: {e}")


async def shutdown_services():
    """Shutdown all initialized services."""
    from app.config.settings import settings

    if settings.enable_postgres:
        try:
            from app.helpers.postgres import postgres_helper

            await postgres_helper.close()
            logger.info("PostgreSQL connection closed")
        except Exception as e:
            logger.error(f"Error closing PostgreSQL: {e}")

    if settings.enable_redis:
        try:
            from app.helpers.redis_helper import redis_helper

            await redis_helper.close()
            logger.info("Redis connection closed")
        except Exception as e:
            logger.error(f"Error closing Redis: {e}")

    if settings.enable_mongodb:
        try:
            from app.helpers.mongodb import mongodb_helper

            await mongodb_helper.close()
            logger.info("MongoDB connection closed")
        except Exception as e:
            logger.error(f"Error closing MongoDB: {e}")

    if settings.enable_neo4j:
        try:
            from app.helpers.neo4j_helper import neo4j_helper

            await neo4j_helper.close()
            logger.info("Neo4j connection closed")
        except Exception as e:
            logger.error(f"Error closing Neo4j: {e}")


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="One-Stop RAG with FastAPI, React, and vector-enabled data services",
    docs_url="/docs" if settings.app_debug else None,
    redoc_url="/redoc" if settings.app_debug else None,
    openapi_url="/openapi.json" if settings.app_debug else None,
    lifespan=lifespan,
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=settings.cors_allow_credentials,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Handle validation errors with detailed error messages."""
    errors = []
    for error in exc.errors():
        errors.append(
            {
                "field": " -> ".join(str(loc) for loc in error["loc"]),
                "message": error["msg"],
                "type": error["type"],
            }
        )

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={"detail": "Validation error", "errors": errors},
    )


@app.exception_handler(Exception)
async def general_exception_handler(request: Request, exc: Exception):
    """Handle all other exceptions."""
    logger.error(f"Unhandled exception: {exc}", exc_info=True)

    if settings.app_env == "production":
        # Don't leak stack traces in production
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )
    else:
        # Show detailed errors in development
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={
                "detail": "Internal server error",
                "error": str(exc),
                "type": type(exc).__name__,
            },
        )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.app_env,
        "docs": "/docs" if settings.app_debug else "disabled",
    }


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Basic health check endpoint."""
    return {
        "status": "healthy",
        "service": settings.app_name,
        "version": settings.app_version,
    }


# Include API routers
from app.api.v1.router import api_router

app.include_router(api_router, prefix=settings.api_v1_prefix)
