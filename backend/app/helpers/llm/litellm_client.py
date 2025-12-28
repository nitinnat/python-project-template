"""
LiteLLM client for unified LLM API access.

Provides a single interface for all LLM providers:
- OpenAI (GPT-4, GPT-3.5)
- Anthropic (Claude 3 Opus, Sonnet, Haiku)
- Google (Gemini Pro)
- Ollama (local models)

Features:
- Automatic retries and fallbacks
- Cost tracking
- Streaming support
- Function calling
"""

from typing import Any, AsyncIterator, Dict, List, Optional

try:
    import litellm
    from litellm import acompletion, cost_per_token
    LITELLM_AVAILABLE = True
except ImportError:
    LITELLM_AVAILABLE = False

from app.config.settings import settings


class LiteLLMClient:
    """Unified LLM client using LiteLLM."""

    def __init__(self):
        self.enabled = settings.enable_llm_litellm and LITELLM_AVAILABLE
        if self.enabled:
            # Configure API keys
            if settings.enable_llm_openai and settings.openai_api_key:
                litellm.openai_key = settings.openai_api_key
            if settings.enable_llm_anthropic and settings.anthropic_api_key:
                litellm.anthropic_key = settings.anthropic_api_key
            if settings.enable_llm_google and settings.google_api_key:
                litellm.google_api_key = settings.google_api_key
            if settings.enable_llm_ollama and settings.ollama_host:
                litellm.ollama_host = settings.ollama_host

    async def complete(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate a completion from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier (e.g., 'gpt-4', 'claude-3-opus')
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters

        Returns:
            Response dict with 'content', 'model', 'usage', 'cost'
        """
        if not self.enabled:
            raise RuntimeError("LiteLLM is not enabled or not installed")

        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            **kwargs,
        )

        # Extract relevant information
        return {
            "content": response.choices[0].message.content,
            "model": response.model,
            "usage": {
                "prompt_tokens": response.usage.prompt_tokens,
                "completion_tokens": response.usage.completion_tokens,
                "total_tokens": response.usage.total_tokens,
            },
            "cost": self._calculate_cost(response),
            "finish_reason": response.choices[0].finish_reason,
        }

    async def stream(
        self,
        messages: List[Dict[str, str]],
        model: str = "gpt-3.5-turbo",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream completion tokens from the LLM.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model identifier
            temperature: Sampling temperature (0-2)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional model-specific parameters

        Yields:
            Content chunks as they arrive
        """
        if not self.enabled:
            raise RuntimeError("LiteLLM is not enabled or not installed")

        response = await acompletion(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
            **kwargs,
        )

        async for chunk in response:
            if chunk.choices[0].delta.content:
                yield chunk.choices[0].delta.content

    def _calculate_cost(self, response: Any) -> float:
        """Calculate the cost of the API call."""
        try:
            prompt_cost = cost_per_token(
                model=response.model,
                prompt_tokens=response.usage.prompt_tokens,
            )
            completion_cost = cost_per_token(
                model=response.model,
                completion_tokens=response.usage.completion_tokens,
            )
            return prompt_cost + completion_cost
        except Exception:
            return 0.0

    async def function_call(
        self,
        messages: List[Dict[str, str]],
        functions: List[Dict[str, Any]],
        model: str = "gpt-4",
        function_call: str = "auto",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Make a function call using the LLM.

        Args:
            messages: Conversation messages
            functions: List of function definitions
            model: Model identifier
            function_call: 'auto', 'none', or specific function name
            **kwargs: Additional parameters

        Returns:
            Response with function call details
        """
        if not self.enabled:
            raise RuntimeError("LiteLLM is not enabled or not installed")

        response = await acompletion(
            model=model,
            messages=messages,
            functions=functions,
            function_call=function_call,
            **kwargs,
        )

        message = response.choices[0].message

        if message.function_call:
            return {
                "type": "function_call",
                "name": message.function_call.name,
                "arguments": message.function_call.arguments,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "cost": self._calculate_cost(response),
            }
        else:
            return {
                "type": "text",
                "content": message.content,
                "usage": {
                    "prompt_tokens": response.usage.prompt_tokens,
                    "completion_tokens": response.usage.completion_tokens,
                    "total_tokens": response.usage.total_tokens,
                },
                "cost": self._calculate_cost(response),
            }


# Global instance
litellm_client = LiteLLMClient()
