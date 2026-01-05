import logging
from typing import Optional

import aiohttp

from app.config.settings import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(
        self,
        model: str = "nomic-embed-text",
        base_url: Optional[str] = None,
    ):
        self.model = model
        self.base_url = base_url or settings.ollama_host or "http://localhost:11434"

    async def embed_text(self, text: str) -> list[float]:
        if not text.strip():
            raise ValueError("Cannot embed empty text")

        url = f"{self.base_url}/api/embeddings"

        async with aiohttp.ClientSession() as session:
            async with session.post(
                url,
                json={
                    "model": self.model,
                    "prompt": text,
                },
            ) as response:
                response.raise_for_status()
                data = await response.json()
                return data["embedding"]

    async def embed_batch(
        self,
        texts: list[str],
        batch_size: int = 10,
    ) -> list[list[float]]:
        embeddings = []

        for i in range(0, len(texts), batch_size):
            batch = texts[i : i + batch_size]
            batch_embeddings = []

            for text in batch:
                try:
                    if text.strip():
                        embedding = await self.embed_text(text)
                        batch_embeddings.append(embedding)
                    else:
                        # Return zero vector for empty text
                        batch_embeddings.append([0.0] * 768)
                except Exception as e:
                    logger.error(f"Failed to embed text: {e}")
                    # Return zero vector on error
                    batch_embeddings.append([0.0] * 768)

            embeddings.extend(batch_embeddings)
            logger.debug(
                f"Embedded batch {i // batch_size + 1}, "
                f"total: {len(embeddings)}/{len(texts)}"
            )

        return embeddings

    async def is_available(self) -> bool:
        try:
            url = f"{self.base_url}/api/tags"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as response:
                    if response.status != 200:
                        return False
                    data = await response.json()
                    models = [m["name"] for m in data.get("models", [])]
                    # Check if our model is available (with or without :latest tag)
                    return any(
                        self.model in m or m.startswith(f"{self.model}:")
                        for m in models
                    )
        except Exception as e:
            logger.warning(f"Ollama embedding service not available: {e}")
            return False
