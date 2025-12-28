"""
Anthropic Claude direct API client.

Use this for Claude-specific features:
- Extended context windows (200K tokens)
- Claude 3 model family (Opus, Sonnet, Haiku)
- System prompts
- Streaming
"""

from typing import Any, AsyncIterator, Dict, List, Optional

try:
    from anthropic import AsyncAnthropic
    ANTHROPIC_AVAILABLE = True
except ImportError:
    ANTHROPIC_AVAILABLE = False

from app.config.settings import settings


class AnthropicClient:
    """Direct Anthropic Claude API client."""

    def __init__(self):
        self.enabled = settings.enable_llm_anthropic and ANTHROPIC_AVAILABLE
        self._client = None

    def _get_client(self) -> "AsyncAnthropic":
        """Get or create Anthropic client."""
        if not self.enabled:
            raise RuntimeError("Anthropic is not enabled or not installed")

        if not settings.anthropic_api_key:
            raise RuntimeError("Anthropic API key is not configured")

        if self._client is None:
            self._client = AsyncAnthropic(api_key=settings.anthropic_api_key)
        return self._client

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-sonnet-20240229",
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Create a message completion.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier (claude-3-opus, claude-3-sonnet, claude-3-haiku)
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature (0-1)
            **kwargs: Additional parameters

        Returns:
            Response dict with content and usage info
        """
        client = self._get_client()

        kwargs_clean = {"model": model, "messages": messages, "max_tokens": max_tokens}

        if system:
            kwargs_clean["system"] = system

        if temperature is not None:
            kwargs_clean["temperature"] = temperature

        kwargs_clean.update(kwargs)

        response = await client.messages.create(**kwargs_clean)

        return {
            "content": response.content[0].text,
            "model": response.model,
            "usage": {
                "input_tokens": response.usage.input_tokens,
                "output_tokens": response.usage.output_tokens,
            },
            "stop_reason": response.stop_reason,
        }

    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "claude-3-sonnet-20240229",
        system: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream message completion.

        Args:
            messages: List of message dicts
            model: Model identifier
            system: Optional system prompt
            max_tokens: Maximum tokens to generate
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Yields:
            Content chunks as they arrive
        """
        client = self._get_client()

        kwargs_clean = {
            "model": model,
            "messages": messages,
            "max_tokens": max_tokens,
            "stream": True,
        }

        if system:
            kwargs_clean["system"] = system

        if temperature is not None:
            kwargs_clean["temperature"] = temperature

        kwargs_clean.update(kwargs)

        async with client.messages.stream(**kwargs_clean) as stream:
            async for text in stream.text_stream:
                yield text

    async def count_tokens(self, text: str) -> int:
        """
        Count tokens in text (approximate).

        Args:
            text: Text to count tokens for

        Returns:
            Approximate token count
        """
        client = self._get_client()

        # Anthropic's token counting
        response = await client.messages.count_tokens(
            model="claude-3-sonnet-20240229",
            messages=[{"role": "user", "content": text}],
        )

        return response.input_tokens


# Global instance
anthropic_client = AnthropicClient()
