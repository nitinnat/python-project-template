"""
Base SQLAlchemy model for PostgreSQL.

Provides common functionality for all database models.
"""

from datetime import datetime

from sqlalchemy import DateTime, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.sql import func

# Naming convention for constraints
# This ensures consistent constraint names across databases
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

metadata = MetaData(naming_convention=convention)


class Base(DeclarativeBase):
    """
    Base class for all SQLAlchemy models.

    Provides common columns and functionality:
    - Metadata with naming conventions
    - Common repr method
    """

    metadata = metadata

    def __repr__(self) -> str:
        """
        String representation of model.

        Returns model name and primary key values.
        """
        cols = []
        for col in self.__table__.columns:
            if col.primary_key:
                cols.append(f"{col.name}={getattr(self, col.name)}")
        return f"<{self.__class__.__name__}({', '.join(cols)})>"


class TimestampMixin:
    """
    Mixin to add created_at and updated_at timestamps.

    Usage:
        class MyModel(Base, TimestampMixin):
            __tablename__ = "my_table"
            ...
    """

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    updated_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        onupdate=func.now(),
        nullable=True,
    )
