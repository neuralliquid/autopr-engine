"""
Mistral AI provider implementation.
"""

from typing import TYPE_CHECKING, Any, Dict, List

from ..base import BaseLLMProvider
from ..types import LLMResponse

if TYPE_CHECKING:
    from mistralai.models.chat_completion import ChatMessage  # type: ignore[import-not-found]


class MistralProvider(BaseLLMProvider):
    """Mistral AI provider."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        try:
            from mistralai.client import MistralClient

            self.client = MistralClient(api_key=self.api_key)
            self.available = True
        except ImportError:
            self.available = False

    def complete(self, request: Dict[str, Any]) -> LLMResponse:
        try:
            from mistralai.models.chat_completion import ChatMessage

            messages = request.get("messages", [])
            model = request.get("model", self.default_model) or "mistral-large-latest"
            max_tokens = request.get("max_tokens", 1024)
            temperature = request.get("temperature", 0.7)

            # Convert input messages to correct type
            mistral_messages: List[ChatMessage] = []
            for msg in messages:
                role = str(msg.get("role", "user"))
                content = str(msg.get("content", "")).strip()
                if not content:
                    continue

                mistral_messages.append(ChatMessage(role=role, content=content))

            # Defensive: check if chat method exists
            chat_method = getattr(self.client, "chat", None)
            if not callable(chat_method):
                raise AttributeError("MistralClient has no 'chat' method")

            response = chat_method(
                model=str(model),
                messages=mistral_messages,
                temperature=temperature,
                max_tokens=max_tokens,
            )

            # Defensive: ensure response has expected attributes
            content = ""
            finish_reason = "stop"
            if hasattr(response, "choices") and response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                if hasattr(choice, "message") and hasattr(choice.message, "content"):
                    content = str(choice.message.content or "")
                finish_reason = str(getattr(choice, "finish_reason", "stop") or "stop")

            # Extract usage information
            usage = None
            if hasattr(response, "usage") and response.usage is not None:
                if hasattr(response.usage, "dict"):
                    usage = response.usage.dict()
                else:
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
                f"Error calling Mistral API: {str(e)}",
                str(request.get("model") or "mistral-large-latest"),
            )

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)
