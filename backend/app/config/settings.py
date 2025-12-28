"""
Application Settings using Pydantic Settings.
"""

from functools import lru_cache
from pydantic import AliasChoices, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Main application settings."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="allow",
    )

    # App
    app_name: str = Field(default="python-project-template")
    app_version: str = Field(default="1.0.0")
    app_env: str = Field(default="development")
    app_debug: bool = Field(default=True)
    secret_key: str = Field(default="change-this-in-production")
    log_level: str = Field(default="INFO")
    api_v1_prefix: str = Field(default="/api/v1")

    # PostgreSQL
    postgres_host: str = Field(default="postgres")
    postgres_port: int = Field(default=5432)
    postgres_user: str = Field(default="postgres")
    postgres_password: str = Field(default="postgres")
    postgres_db: str = Field(default="app_db")

    # Redis
    redis_host: str = Field(default="redis")
    redis_port: int = Field(default=6379)
    redis_db: int = Field(default=0)

    # MongoDB
    mongodb_host: str = Field(default="mongodb")
    mongodb_port: int = Field(default=27017)
    mongodb_user: str = Field(default="mongo")
    mongodb_password: str = Field(default="mongo")
    mongodb_db: str = Field(default="app_db")

    # Neo4j
    neo4j_host: str = Field(default="neo4j")
    neo4j_port: int = Field(default=7687)
    neo4j_user: str = Field(default="neo4j")
    neo4j_password: str = Field(default="password")

    # RabbitMQ
    rabbitmq_host: str = Field(default="rabbitmq")
    rabbitmq_port: int = Field(default=5672)
    rabbitmq_user: str = Field(default="guest")
    rabbitmq_password: str = Field(default="guest")

    # Celery
    celery_broker_url: str = Field(default="amqp://guest:guest@rabbitmq:5672//")
    celery_result_backend: str = Field(default="redis://redis:6379/0")

    # CORS
    cors_origins: str = Field(default="http://localhost:3000,http://localhost:5173,http://localhost:80")
    cors_allow_credentials: bool = Field(default=True)
    cors_allow_methods: str = Field(default="*")
    cors_allow_headers: str = Field(default="*")

    # Feature Flags (build-time)
    enable_postgres: bool = Field(default=True)
    enable_redis: bool = Field(default=True)
    enable_pgvector: bool = Field(default=True)
    enable_mongodb: bool = Field(default=False)
    enable_neo4j: bool = Field(default=False)
    enable_rabbitmq: bool = Field(default=False)
    enable_celery_worker: bool = Field(default=False)
    enable_frontend: bool = Field(default=True)
    enable_nginx: bool = Field(default=True)

    # LLM Providers
    enable_llm_openai: bool = Field(default=False)
    enable_llm_anthropic: bool = Field(default=False)
    enable_llm_google: bool = Field(default=False)
    enable_llm_ollama: bool = Field(default=False)
    enable_llm_litellm: bool = Field(default=False)
    enable_llm_langchain: bool = Field(default=False)

    openai_api_key: str | None = Field(default=None)
    anthropic_api_key: str | None = Field(default=None)
    google_api_key: str | None = Field(
        default=None, validation_alias=AliasChoices("GOOGLE_API_KEY", "GEMINI_API_KEY")
    )
    ollama_host: str = Field(default="http://host.docker.internal:11434")

    # Observability
    otel_enabled: bool = Field(default=False)
    otel_service_name: str = Field(default="python-project-template")

    @property
    def database_url(self) -> str:
        """Async PostgreSQL URL."""
        return f"postgresql+asyncpg://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def database_url_sync(self) -> str:
        """Sync PostgreSQL URL for Alembic."""
        return f"postgresql://{self.postgres_user}:{self.postgres_password}@{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"

    @property
    def redis_url(self) -> str:
        """Redis URL."""
        return f"redis://{self.redis_host}:{self.redis_port}/{self.redis_db}"

    @property
    def rabbitmq_url(self) -> str:
        """RabbitMQ URL."""
        return f"amqp://{self.rabbitmq_user}:{self.rabbitmq_password}@{self.rabbitmq_host}:{self.rabbitmq_port}//"

    @property
    def mongodb_url(self) -> str:
        """MongoDB URL."""
        auth_params = "?authSource=admin" if self.mongodb_user else ""
        return (
            f"mongodb://{self.mongodb_user}:{self.mongodb_password}"
            f"@{self.mongodb_host}:{self.mongodb_port}/{self.mongodb_db}{auth_params}"
        )

    @property
    def neo4j_url(self) -> str:
        """Neo4j URL."""
        return f"bolt://{self.neo4j_host}:{self.neo4j_port}"

    @property
    def cors_origins_list(self) -> list[str]:
        """Parse CORS origins into list."""
        return [origin.strip() for origin in self.cors_origins.split(",")]


@lru_cache
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


settings = get_settings()
