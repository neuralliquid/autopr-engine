"""
Groq provider implementation for fast inference.
"""

from typing import Dict, Any, List, TYPE_CHECKING
import asyncio

from ..base import BaseLLMProvider
from ..types import LLMResponse

if TYPE_CHECKING:
    from groq import Groq  # type: ignore[import-not-found]


class GroqProvider(BaseLLMProvider):
    """Groq provider for fast inference."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        try:
            from groq import Groq

            self.client = Groq(api_key=self.api_key)
            self.available = True
        except ImportError:
            self.available = False

    def _convert_to_provider_messages(
        self, messages: List[Dict[str, Any]], provider: str
    ) -> List[Dict[str, Any]]:
        """Convert messages to provider-specific format."""
        return [
            {
                "role": str(msg.get("role", "user")),
                "content": str(msg.get("content", "")),
                **({k: v for k, v in msg.items() if k not in ("role", "content")}),
            }
            for msg in messages
            if msg.get("content", "").strip()
        ]

    async def _call_groq_api(self, messages: List[Dict[str, Any]], **kwargs: Any) -> Any:
        """Call Groq API with proper type handling."""
        groq_messages = self._convert_to_provider_messages(messages, "groq")
        response = self.client.chat.completions.create(messages=groq_messages, **kwargs)
        return response

    def complete(self, request: Dict[str, Any]) -> LLMResponse:
        try:
            messages = request.get("messages", [])
            model = request.get("model", self.default_model) or "mixtral-8x7b-32768"
            max_tokens = request.get("max_tokens", 1024)
            temperature = request.get("temperature", 0.7)

            # Filter out empty messages and convert to Groq format
            filtered_messages = [
                {"role": m.get("role", "user"), "content": m.get("content", "")}
                for m in messages
                if m.get("content")
            ]

            # Call the API synchronously
            response = self.client.chat.completions.create(
                model=str(model),
                messages=filtered_messages,
                max_tokens=max_tokens,
                temperature=temperature,
            )

            # Extract content and finish reason
            content = ""
            finish_reason = "stop"
            if hasattr(response, "choices") and response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    content = choice.message.content or ""
                finish_reason = getattr(choice, "finish_reason", "stop") or "stop"

            # Extract usage information
            usage = None
            if hasattr(response, "usage") and response.usage:
                usage = {
                    "prompt_tokens": getattr(response.usage, "prompt_tokens", 0),
                    "completion_tokens": getattr(response.usage, "completion_tokens", 0),
                    "total_tokens": getattr(response.usage, "total_tokens", 0),
                }

            return LLMResponse(
                content=content,
                model=str(model),
                finish_reason=finish_reason,
                usage=usage,
            )

        except Exception as e:
            return LLMResponse.from_error(
                f"Error calling Groq API: {str(e)}",
                str(request.get("model") or "mixtral-8x7b-32768"),
            )

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)
