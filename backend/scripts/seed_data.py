"""
Seed script to initialize database with default data.

Creates:
- Default feature flags
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config.settings import settings
from app.helpers.postgres import postgres_helper
from app.models.postgres.feature_flag import FeatureFlag
from sqlalchemy import select


async def seed_feature_flags():
    """Create default feature flags."""
    print("Creating default feature flags...")

    flags_to_create = [
        {
            "key": "feature.vector_search",
            "name": "Vector Search",
            "enabled": settings.enable_pgvector,
            "description": "Enable vector similarity search using PGVector",
            "category": "feature",
            "config": {"requires": ["postgres", "pgvector"]},
        },
        {
            "key": "feature.graph_queries",
            "name": "Graph Queries",
            "enabled": settings.enable_neo4j,
            "description": "Enable graph database queries with Neo4j",
            "category": "feature",
            "config": {"requires": ["neo4j"]},
        },
        {
            "key": "feature.document_storage",
            "name": "Document Storage",
            "enabled": settings.enable_mongodb,
            "description": "Enable document storage with MongoDB",
            "category": "feature",
            "config": {"requires": ["mongodb"]},
        },
        {
            "key": "feature.background_tasks",
            "name": "Background Tasks",
            "enabled": settings.enable_celery_worker,
            "description": "Enable background task processing with Celery",
            "category": "feature",
            "config": {"requires": ["rabbitmq", "celery"]},
        },
        {
            "key": "llm.openai",
            "name": "OpenAI",
            "enabled": settings.enable_llm_openai,
            "description": "OpenAI GPT models integration",
            "category": "llm",
            "config": {"provider": "openai", "models": ["gpt-4", "gpt-3.5-turbo"]},
        },
        {
            "key": "llm.anthropic",
            "name": "Anthropic",
            "enabled": settings.enable_llm_anthropic,
            "description": "Anthropic Claude models integration",
            "category": "llm",
            "config": {"provider": "anthropic", "models": ["claude-3-opus", "claude-3-sonnet"]},
        },
        {
            "key": "llm.google",
            "name": "Google Gemini",
            "enabled": settings.enable_llm_google,
            "description": "Google Gemini models integration",
            "category": "llm",
            "config": {"provider": "google", "models": ["gemini-pro"]},
        },
        {
            "key": "llm.ollama",
            "name": "Ollama",
            "enabled": settings.enable_llm_ollama,
            "description": "Ollama local models integration",
            "category": "llm",
            "config": {"provider": "ollama", "local": True},
        },
        {
            "key": "database.postgres",
            "name": "PostgreSQL",
            "enabled": True,
            "description": "PostgreSQL primary database",
            "category": "database",
            "config": {"type": "relational", "required": True},
        },
        {
            "key": "database.redis",
            "name": "Redis",
            "enabled": True,
            "description": "Redis cache and session storage",
            "category": "database",
            "config": {"type": "cache", "required": True},
        },
        {
            "key": "database.mongodb",
            "name": "MongoDB",
            "enabled": settings.enable_mongodb,
            "description": "MongoDB document database",
            "category": "database",
            "config": {"type": "document"},
        },
        {
            "key": "database.neo4j",
            "name": "Neo4j",
            "enabled": settings.enable_neo4j,
            "description": "Neo4j graph database",
            "category": "database",
            "config": {"type": "graph"},
        },
    ]

    async with postgres_helper.get_session() as session:
        created_count = 0
        updated_count = 0

        for flag_data in flags_to_create:
            result = await session.execute(
                select(FeatureFlag).where(FeatureFlag.key == flag_data["key"])
            )
            existing_flag = result.scalar_one_or_none()

            if existing_flag:
                # Update existing flag
                existing_flag.enabled = flag_data["enabled"]
                existing_flag.name = flag_data["name"]
                existing_flag.description = flag_data["description"]
                existing_flag.category = flag_data["category"]
                existing_flag.config = flag_data.get("config")
                updated_count += 1
            else:
                # Create new flag
                flag = FeatureFlag(**flag_data)
                session.add(flag)
                created_count += 1

        await session.commit()
        print(f"  ✅ Created {created_count} feature flags")
        if updated_count:
            print(f"  ✅ Updated {updated_count} existing feature flags")


async def main():
    """Main seed function."""
    print("=" * 60)
    print("🌱 Seeding database...")
    print("=" * 60)

    try:
        # Initialize database connection
        await postgres_helper.initialize()

        # Seed data
        await seed_feature_flags()

        print("=" * 60)
        print("✅ Seeding completed successfully!")
        print("=" * 60)
        print("\nAccess the API at: http://localhost:8000")
        print("Access the API docs at: http://localhost:8000/docs")

    except Exception as e:
        print(f"\n❌ Error seeding database: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    finally:
        # Close database connection
        await postgres_helper.close()


if __name__ == "__main__":
    asyncio.run(main())
