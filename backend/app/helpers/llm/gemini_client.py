"""
Google Gemini API client.

Features:
- Gemini Pro and Ultra models
- Multimodal support (text + images)
- Safety settings
- Streaming
"""

from typing import Any, AsyncIterator, Dict, List, Optional

try:
    import google.generativeai as genai
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

from app.config.settings import settings


class GeminiClient:
    """Google Gemini API client."""

    def __init__(self):
        self.enabled = settings.enable_llm_google and GEMINI_AVAILABLE
        if self.enabled and settings.google_api_key:
            genai.configure(api_key=settings.google_api_key)

    def _get_model(self, model_name: str = "gemini-flash-latest"):
        """Get Gemini model instance."""
        if not self.enabled:
            raise RuntimeError("Gemini is not enabled or not installed")

        if not settings.google_api_key:
            raise RuntimeError("Google API key is not configured")

        return genai.GenerativeModel(model_name)

    async def generate_content(
        self,
        prompt: str,
        model: str = "gemini-flash-latest",
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """
        Generate content from prompt.

        Args:
            prompt: Input prompt
            model: Model name (gemini-flash-latest, gemini-pro-latest)
            temperature: Sampling temperature (0-1)
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters

        Returns:
            Response dict with content and safety ratings
        """
        model_instance = self._get_model(model)

        generation_config = {
            "temperature": temperature,
        }
        if max_tokens:
            generation_config["max_output_tokens"] = max_tokens

        response = await model_instance.generate_content_async(
            prompt,
            generation_config=generation_config,
            **kwargs,
        )

        return {
            "content": response.text,
            "model": model,
            "safety_ratings": [
                {
                    "category": rating.category.name,
                    "probability": rating.probability.name,
                }
                for rating in response.candidates[0].safety_ratings
            ],
            "finish_reason": response.candidates[0].finish_reason.name,
        }

    async def chat(
        self,
        messages: List[Dict[str, str]],
        model: str = "gemini-flash-latest",
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
        model_instance = self._get_model(model)
        chat = model_instance.start_chat(history=[])

        # Convert messages to Gemini format
        for msg in messages[:-1]:
            if msg["role"] == "user":
                chat.history.append({"role": "user", "parts": [msg["content"]]})
            elif msg["role"] == "assistant":
                chat.history.append({"role": "model", "parts": [msg["content"]]})

        # Send last message
        last_message = messages[-1]["content"]

        generation_config = {"temperature": temperature}
        response = await chat.send_message_async(
            last_message,
            generation_config=generation_config,
            **kwargs,
        )

        return {
            "content": response.text,
            "model": model,
            "finish_reason": response.candidates[0].finish_reason.name,
        }

    async def stream_content(
        self,
        prompt: str,
        model: str = "gemini-flash-latest",
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
        model_instance = self._get_model(model)

        generation_config = {"temperature": temperature}

        response = await model_instance.generate_content_async(
            prompt,
            generation_config=generation_config,
            stream=True,
            **kwargs,
        )

        async for chunk in response:
            if chunk.text:
                yield chunk.text

    async def count_tokens(self, text: str, model: str = "gemini-flash-latest") -> int:
        """
        Count tokens in text.

        Args:
            text: Text to count tokens for
            model: Model name

        Returns:
            Token count
        """
        model_instance = self._get_model(model)
        result = await model_instance.count_tokens_async(text)
        return result.total_tokens


# Global instance
gemini_client = GeminiClient()
