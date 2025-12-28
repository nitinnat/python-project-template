"""
OpenTelemetry instrumentation setup.

Provides distributed tracing for monitoring application performance.
"""

from app.config.settings import settings
from app.core.logging import get_logger

logger = get_logger(__name__)


def setup_telemetry() -> None:
    """
    Initialize OpenTelemetry instrumentation.

    Sets up tracing for:
    - FastAPI application
    - Database queries (SQLAlchemy)
    - HTTP requests
    - External API calls
    """
    if not settings.otel_enabled:
        logger.info("OpenTelemetry is disabled")
        return

    try:
        from opentelemetry import trace
        from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import (
            OTLPSpanExporter,
        )
        from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
        from opentelemetry.instrumentation.httpx import HTTPXClientInstrumentor
        from opentelemetry.instrumentation.sqlalchemy import SQLAlchemyInstrumentor
        from opentelemetry.sdk.resources import Resource
        from opentelemetry.sdk.trace import TracerProvider
        from opentelemetry.sdk.trace.export import BatchSpanProcessor

        # Create resource with service name
        resource = Resource(attributes={"service.name": settings.otel_service_name})

        # Set up tracer provider
        tracer_provider = TracerProvider(resource=resource)
        trace.set_tracer_provider(tracer_provider)

        # Add OTLP exporter
        otlp_exporter = OTLPSpanExporter()
        span_processor = BatchSpanProcessor(otlp_exporter)
        tracer_provider.add_span_processor(span_processor)

        # Instrument libraries
        FastAPIInstrumentor.instrument()
        HTTPXClientInstrumentor().instrument()
        SQLAlchemyInstrumentor().instrument()

        logger.info(
            f"OpenTelemetry initialized for service: {settings.otel_service_name}"
        )

    except ImportError:
        logger.warning(
            "OpenTelemetry packages not installed. Install with: "
            "pip install opentelemetry-api opentelemetry-sdk "
            "opentelemetry-instrumentation-fastapi opentelemetry-exporter-otlp"
        )
    except Exception as e:
        logger.error(f"Failed to initialize OpenTelemetry: {e}")
