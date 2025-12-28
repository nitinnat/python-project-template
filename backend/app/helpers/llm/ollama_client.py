"""
Ollama client for local LLM inference.

Features:
- Local LLM deployment (llama2, mistral, codellama, etc.)
- No API costs
- Privacy-focused
- Custom model support
"""

from typing import Any, AsyncIterator, Dict, List, Optional

try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from app.config.settings import settings


class OllamaClient:
    """Ollama local LLM client."""

    def __init__(self):
        self.enabled = settings.enable_llm_ollama and AIOHTTP_AVAILABLE
        self.base_url = settings.ollama_host or "http://localhost:11434"

    async def _make_request(
        self,
        endpoint: str,
        data: Dict[str, Any],
        stream: bool = False,
    ) -> Any:
        """Make HTTP request to Ollama API."""
        if not self.enabled:
            raise RuntimeError("Ollama is not enabled or aiohttp not installed")

        url = f"{self.base_url}/api/{endpoint}"

        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                if stream:
                    return response
                else:
                    response.raise_for_status()
                    return await response.json()

    async def generate(
        self,
        prompt: str,
        model: str = "llama2",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        system: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate completion from prompt.

        Args:
            prompt: Input prompt
            model: Model name (llama2, mistral, codellama, etc.)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            system: Optional system prompt
            **kwargs: Additional parameters

        Returns:
            Response dict with content
        """
        data = {
            "model": model,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
            },
            "stream": False,
        }

        if max_tokens:
            data["options"]["num_predict"] = max_tokens

        if system:
            data["system"] = system

        data.update(kwargs)

        response = await self._make_request("generate", data)

        return {
            "content": response["response"],
            "model": response["model"],
            "done": response["done"],
            "context": response.get("context", []),
            "total_duration": response.get("total_duration"),
            "load_duration": response.get("load_duration"),
            "prompt_eval_count": response.get("prompt_eval_count"),
            "eval_count": response.get("eval_count"),
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "llama2",
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Multi-turn chat conversation.

        Args:
            messages: List of message dicts with 'role' and 'content'
            model: Model name
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Returns:
            Response dict
        """
        data = {
            "model": model,
            "messages": messages,
            "options": {
                "temperature": temperature,
            },
            "stream": False,
        }

        data.update(kwargs)

        response = await self._make_request("chat", data)

        return {
            "content": response["message"]["content"],
            "role": response["message"]["role"],
            "model": response["model"],
            "done": response["done"],
            "total_duration": response.get("total_duration"),
            "eval_count": response.get("eval_count"),
        }

    async def stream_generate(
        self,
        prompt: str,
        model: str = "llama2",
        temperature: float = 0.7,
        **kwargs: Any,
    ) -> AsyncIterator[str]:
        """
        Stream generated content.

        Args:
            prompt: Input prompt
            model: Model name
            temperature: Sampling temperature
            **kwargs: Additional parameters

        Yields:
            Content chunks as they arrive
        """
        data = {
            "model": model,
            "prompt": prompt,
            "options": {
                "temperature": temperature,
            },
            "stream": True,
        }

        data.update(kwargs)

        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/generate"
            async with session.post(url, json=data) as response:
                response.raise_for_status()
                async for line in response.content:
                    if line:
                        import json
                        chunk = json.loads(line)
                        if chunk.get("response"):
                            yield chunk["response"]

    async def list_models(self) -> List[Dict[str, Any]]:
        """
        List available local models.

        Returns:
            List of model info dicts
        """
        if not self.enabled:
            raise RuntimeError("Ollama is not enabled")

        async with aiohttp.ClientSession() as session:
            url = f"{self.base_url}/api/tags"
            async with session.get(url) as response:
                response.raise_for_status()
                data = await response.json()
                return data.get("models", [])

    async def pull_model(self, model: str) -> bool:
        """
        Pull/download a model from Ollama registry.

        Args:
            model: Model name to pull

        Returns:
            True if successful
        """
        data = {"name": model, "stream": False}

        try:
            await self._make_request("pull", data)
            return True
        except Exception:
            return False


# Global instance
ollama_client = OllamaClient()
