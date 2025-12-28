"""
OpenAI direct API client.

Use this for OpenAI-specific features not available through LiteLLM:
- Fine-tuned models
- Assistants API
- Advanced streaming
- Image generation (DALL-E)
- Speech-to-text (Whisper)
"""

from typing import Any, AsyncIterator, Dict, List, Optional

try:
    from openai import AsyncOpenAI
    OPENAI_AVAILABLE = True
except ImportError:
    OPENAI_AVAILABLE = False

from app.config.settings import settings


class OpenAIClient:
    """Direct OpenAI API client."""

    def __init__(self):
        self.enabled = settings.enable_llm_openai and OPENAI_AVAILABLE
        self._client = None

    def _get_client(self) -> "AsyncOpenAI":
        """Get or create OpenAI client."""
        if not self.enabled:
            raise RuntimeError("OpenAI is not enabled or not installed")

        if not settings.openai_api_key:
            raise RuntimeError("OpenAI API key is not configured")

        if self._client is None:
            self._client = AsyncOpenAI(api_key=settings.openai_api_key)
        return self._client

    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a chat completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier (gpt-4, gpt-3.5-turbo, etc.)
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Response dict with content and usage info
        """
        client = self._get_client()

        response = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        return {
            "content": response.choices[0].message.content,
            "role": response.choices[0].message.role,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "finish_reason": response.choices[0].finish_reason,
        }

    async def stream_completion(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream chat completion tokens.

        Args:
            messages: List of message dicts
            model: Model identifier
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Yields:
            Content chunks as they arrive
        """
        client = self._get_client()

        stream = await client.chat.completions.create(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in stream:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    async def create_embedding(
        self,
        text: str,
        model: str = "text-embedding-3-small",
    ) -> List[float]:
        """
        Create text embedding.

        Args:
            text: Text to embed
            model: Embedding model (text-embedding-3-small, text-embedding-ada-002)

        Returns:
            Embedding vector
        """
        client = self._get_client()

        response = await client.embeddings.create(
            model=model,
            input=text,
        )

        return response.data[0].embedding

    async def create_embeddings(
        self,
        texts: List[str],
        model: str = "text-embedding-3-small",
    ) -> List[List[float]]:
        """
        Create embeddings for multiple texts.

        Args:
            texts: List of texts to embed
            model: Embedding model

        Returns:
            List of embedding vectors
        """
        client = self._get_client()

        response = await client.embeddings.create(
            model=model,
            input=texts,
        )

        return [item.embedding for item in response.data]

    async def generate_image(
        self,
        prompt: str,
        model: str = "dall-e-3",
        size: str = "1024x1024",
        quality: str = "standard",
        n: int = 1,
    ) -> List[str]:
        """
        Generate images using DALL-E.

        Args:
            prompt: Image description
            model: dall-e-3 or dall-e-2
            size: Image size (1024x1024, 1792x1024, 1024x1792)
            quality: standard or hd
            n: Number of images to generate

        Returns:
            List of image URLs
        """
        client = self._get_client()

        response = await client.images.generate(
            model=model,
            prompt=prompt,
            size=size,
            quality=quality,
            n=n,
        )

        return [image.url for image in response.data]


# Global instance
openai_client = OpenAIClient()
