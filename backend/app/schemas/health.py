"""
Pydantic schemas for health check endpoints.

Response models for service health monitoring.
"""

from typing import Any

from pydantic import BaseModel, Field


class ServiceHealth(BaseModel):
    """Health status for a single service."""

    status: str = Field(..., description="Service status (healthy, unhealthy, degraded)")
    latency_ms: float | None = Field(None, description="Response latency in milliseconds")
    connections: int | None = Field(None, description="Number of active connections")
    error: str | None = Field(None, description="Error message if unhealthy")
    details: dict[str, Any] | None = Field(None, description="Additional service details")


class SystemHealthResponse(BaseModel):
    """Overall system health response."""

    status: str = Field(..., description="Overall system status")
    services: dict[str, ServiceHealth] = Field(..., description="Individual service health")
    timestamp: str = Field(..., description="Health check timestamp")


class HealthCheckResponse(BaseModel):
    """Basic health check response."""

    status: str = Field(default="healthy", description="Service status")
    service: str = Field(..., description="Service name")
    version: str = Field(..., description="Service version")
