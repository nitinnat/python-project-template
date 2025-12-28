"""
Feature flag model for runtime feature toggling.

Stores feature flags in database for dynamic control.
"""

from sqlalchemy import Boolean, Integer, JSON, String
from sqlalchemy.orm import Mapped, mapped_column

from app.models.postgres.base import Base, TimestampMixin


class FeatureFlag(Base, TimestampMixin):
    """
    Runtime feature flag model.

    Attributes:
        id: Primary key
        key: Unique feature flag key (e.g., "feature.vector_search")
        enabled: Whether feature is enabled
        name: Human-readable feature name
        description: Feature description
        category: Feature category (database, llm, feature, integration)
        config: Additional configuration as JSON
        created_at: Flag creation timestamp (from TimestampMixin)
        updated_at: Last update timestamp (from TimestampMixin)
    """

    __tablename__ = "feature_flags"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)

    key: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        index=True,
        nullable=False,
    )

    enabled: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    name: Mapped[str] = mapped_column(String(255), nullable=False)

    description: Mapped[str | None] = mapped_column(String(500), nullable=True)

    category: Mapped[str] = mapped_column(
        String(50),
        default="feature",
        nullable=False,
        index=True,
    )

    config: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    def __repr__(self) -> str:
        return f"<FeatureFlag(key={self.key}, enabled={self.enabled}, category={self.category})>"
