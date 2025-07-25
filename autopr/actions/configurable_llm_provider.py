"""
AutoPR Action: Configurable LLM Provider
Unified interface for multiple LLM providers (OpenAI, Anthropic, Mistral, Groq, Perplexity, etc.)
"""

import os
import json
from typing import Dict, Any, Optional, List, Union, Callable, Iterable
from pydantic import BaseModel
from abc import ABC, abstractmethod


class LLMMessage(BaseModel):
    role: str  # "system", "user", "assistant"
    content: str


class LLMRequest(BaseModel):
    messages: List[LLMMessage]
    model: Optional[str] = None
    temperature: float = 0.1
    max_tokens: Optional[int] = None
    stream: bool = False


class LLMResponse(BaseModel):
    content: str
    model: str
    usage: Dict[str, int] = {}
    finish_reason: Optional[str] = None
    error: Optional[str] = None


class BaseLLMProvider(ABC):
    """Abstract base class for LLM providers."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.config = config
        self.api_key = config.get("api_key") or os.getenv(config.get("api_key_env", ""))
        self.base_url = config.get("base_url")
        self.default_model = config.get("default_model")

    @abstractmethod
    def complete(self, request: LLMRequest) -> LLMResponse:
        """Complete a chat conversation."""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the provider is properly configured and available."""
        pass


class OpenAIProvider(BaseLLMProvider):
    """OpenAI GPT provider."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        try:
            import openai

            self.client = openai.OpenAI(api_key=self.api_key, base_url=self.base_url)
            self.available = True
        except ImportError:
            self.available = False

    def complete(self, request: LLMRequest) -> LLMResponse:
        try:
            # Ensure all messages have non-empty content (additional robustness)
            filtered_messages = [msg for msg in request.messages if msg.content.strip()]
            response = self.client.chat.completions.create(
                model=request.model or self.default_model or "gpt-4",
                messages=[msg.dict() for msg in filtered_messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                stream=request.stream,
            )

            # Defensive: ensure response is not a stream
            if hasattr(response, "choices") and hasattr(response, "model"):
                content = getattr(response.choices[0].message, "content", "")
                model = getattr(
                    response, "model", request.model or self.default_model or "gpt-4"
                )
                usage: Dict[str, int] = {}
                if (
                    hasattr(response, "usage")
                    and getattr(response, "usage", None) is not None
                ):
                    usage = response.usage.dict()
                finish_reason = getattr(response.choices[0], "finish_reason", None)
            else:
                content = ""
                model = request.model or self.default_model or "gpt-4"
                usage = {}
                finish_reason = None

            return LLMResponse(
                content=str(content),
                model=str(model),
                usage=usage,
                finish_reason=finish_reason,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=request.model or self.default_model or "gpt-4",
                error=str(e),
            )

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class AnthropicProvider(BaseLLMProvider):
    """Anthropic Claude provider."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        try:
            import anthropic

            self.client = anthropic.Anthropic(
                api_key=self.api_key, base_url=self.base_url
            )
            self.available = True
        except ImportError:
            self.available = False

    def complete(self, request: LLMRequest) -> LLMResponse:
        try:
            # Convert messages to Anthropic format
            system_message = ""
            messages: List[Dict[str, str]] = []

            for msg in request.messages:
                if msg.role == "system":
                    system_message = msg.content
                else:
                    messages.append({"role": msg.role, "content": msg.content})

            response = self.client.messages.create(
                model=request.model or self.default_model or "claude-3-sonnet-20240229",
                max_tokens=request.max_tokens or 4096,
                temperature=request.temperature,
                system=system_message,
                messages=messages,
            )

            # Defensive: extract first block with .text attribute
            content = ""
            if hasattr(response, "content") and isinstance(response.content, list):
                for block in response.content:
                    if hasattr(block, "text"):
                        content = getattr(block, "text", "")
                        break
            model = getattr(
                response,
                "model",
                request.model or self.default_model or "claude-3-sonnet-20240229",
            )
            usage: Dict[str, int] = (
                response.usage.dict()
                if hasattr(response, "usage")
                and getattr(response, "usage", None) is not None
                else {}
            )
            finish_reason = getattr(response, "stop_reason", None)
            return LLMResponse(
                content=str(content),
                model=str(model),
                usage=usage,
                finish_reason=finish_reason,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=request.model or self.default_model or "claude-3-sonnet-20240229",
                error=str(e),
            )

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


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

    def complete(self, request: LLMRequest) -> LLMResponse:
        try:
            from mistralai.models.chat_completion import ChatMessage

            # Convert input messages to correct type
            messages: List[ChatMessage] = [
                ChatMessage(role=msg.role, content=msg.content)
                for msg in request.messages
            ]

            # Defensive: check if chat method exists
            chat_method = getattr(self.client, "chat", None)
            if not callable(chat_method):
                raise AttributeError("MistralClient has no 'chat' method")

            response = self.client.chat(
                model=request.model or self.default_model or "mistral-large-latest",
                messages=messages,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            # Defensive: ensure response has expected attributes
            if hasattr(response, "choices") and hasattr(response, "model"):
                content = getattr(response.choices[0].message, "content", "")
                model = getattr(
                    response,
                    "model",
                    request.model or self.default_model or "mistral-large-latest",
                )
                usage: Dict[str, int] = {}
                if (
                    hasattr(response, "usage")
                    and getattr(response, "usage", None) is not None
                ):
                    usage = response.usage.dict()
                finish_reason = getattr(response.choices[0], "finish_reason", None)
            else:
                content = ""
                model = request.model or self.default_model or "mistral-large-latest"
                usage = {}
                finish_reason = None

            return LLMResponse(
                content=str(content),
                model=str(model),
                usage=usage,
                finish_reason=finish_reason,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=request.model or self.default_model or "mistral-large-latest",
                error=str(e),
            )

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class GroqProvider(BaseLLMProvider):
    """Groq provider for fast inference."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        try:
            import groq

            self.client = groq.Groq(api_key=self.api_key)
            self.available = True
        except ImportError:
            self.available = False

    def complete(self, request: LLMRequest) -> LLMResponse:
        try:
            # Robustness: filter out empty-content messages
            filtered_messages = [msg for msg in request.messages if msg.content.strip()]
            response = self.client.chat.completions.create(
                model=request.model or self.default_model or "mixtral-8x7b-32768",
                messages=[msg.dict() for msg in filtered_messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            # Defensive: ensure response has expected attributes
            if hasattr(response, "choices") and hasattr(response, "model"):
                content = getattr(response.choices[0].message, "content", "")
                model = getattr(
                    response,
                    "model",
                    request.model or self.default_model or "mixtral-8x7b-32768",
                )
                usage: Dict[str, int] = {}
                if (
                    hasattr(response, "usage")
                    and getattr(response, "usage", None) is not None
                ):
                    usage = response.usage.dict()
                finish_reason = getattr(response.choices[0], "finish_reason", None)
            else:
                content = ""
                model = request.model or self.default_model or "mixtral-8x7b-32768"
                usage = {}
                finish_reason = None

            return LLMResponse(
                content=str(content),
                model=str(model),
                usage=usage,
                finish_reason=finish_reason,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=request.model or self.default_model or "mixtral-8x7b-32768",
                error=str(e),
            )

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class PerplexityProvider(BaseLLMProvider):
    """Perplexity AI provider."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        try:
            import openai  # Perplexity uses OpenAI-compatible API

            self.client = openai.OpenAI(
                api_key=self.api_key, base_url="https://api.perplexity.ai"
            )
            self.available = True
        except ImportError:
            self.available = False

    def complete(self, request: LLMRequest) -> LLMResponse:
        try:
            response = self.client.chat.completions.create(
                model=request.model
                or self.default_model
                or "llama-3.1-sonar-large-128k-online",
                messages=[msg.dict() for msg in request.messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            content = (
                getattr(response.choices[0].message, "content", "")
                if hasattr(response, "choices") and len(response.choices) > 0
                else ""
            )
            model = getattr(
                response,
                "model",
                request.model
                or self.default_model
                or "llama-3.1-sonar-large-128k-online",
            )
            usage: Dict[str, int] = (
                response.usage.dict()
                if hasattr(response, "usage")
                and getattr(response, "usage", None) is not None
                else {}
            )
            finish_reason = (
                getattr(response.choices[0], "finish_reason", None)
                if hasattr(response, "choices") and len(response.choices) > 0
                else None
            )
            return LLMResponse(
                content=str(content) if content is not None else "",
                model=(
                    str(model)
                    if model is not None
                    else str(
                        request.model
                        or self.default_model
                        or "llama-3.1-sonar-large-128k-online"
                    )
                ),
                usage=usage,
                finish_reason=finish_reason,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=request.model
                or self.default_model
                or "llama-3.1-sonar-large-128k-online",
                error=str(e),
            )

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class TogetherAIProvider(BaseLLMProvider):
    """Together AI provider for open source models."""

    def __init__(self, config: Dict[str, Any]) -> None:
        super().__init__(config)
        try:
            import openai  # Together uses OpenAI-compatible API

            self.client = openai.OpenAI(
                api_key=self.api_key, base_url="https://api.together.xyz/v1"
            )
            self.available = True
        except ImportError:
            self.available = False

    def complete(self, request: LLMRequest) -> LLMResponse:
        try:
            # Robustness: filter out empty-content messages
            filtered_messages = [msg for msg in request.messages if msg.content.strip()]
            response = self.client.chat.completions.create(
                model=request.model
                or self.default_model
                or "meta-llama/Llama-2-70b-chat-hf",
                messages=[msg.dict() for msg in filtered_messages],
                temperature=request.temperature,
                max_tokens=request.max_tokens,
            )

            usage: Dict[str, int] = {}
            if (
                hasattr(response, "usage")
                and getattr(response, "usage", None) is not None
            ):
                usage = response.usage.dict()
            content = (
                getattr(response.choices[0].message, "content", "")
                if hasattr(response, "choices") and len(response.choices) > 0
                else ""
            )
            model = getattr(
                response,
                "model",
                request.model or self.default_model or "meta-llama/Llama-2-70b-chat-hf",
            )
            finish_reason = (
                getattr(response.choices[0], "finish_reason", None)
                if hasattr(response, "choices") and len(response.choices) > 0
                else None
            )
            return LLMResponse(
                content=str(content) if content is not None else "",
                model=(
                    str(model)
                    if model is not None
                    else str(
                        request.model
                        or self.default_model
                        or "meta-llama/Llama-2-70b-chat-hf"
                    )
                ),
                usage=usage,
                finish_reason=finish_reason,
            )
        except Exception as e:
            return LLMResponse(
                content="",
                model=request.model
                or self.default_model
                or "meta-llama/Llama-2-70b-chat-hf",
                error=str(e),
            )

    def is_available(self) -> bool:
        return self.available and bool(self.api_key)


class LLMProviderManager:
    """Manages multiple LLM providers with fallback support."""

    def __init__(self, config: Dict[str, Any]) -> None:
        self.providers: Dict[str, BaseLLMProvider] = {}
        self.fallback_order: List[str] = config.get(
            "fallback_order", ["openai", "anthropic", "mistral"]
        )
        self.default_provider: str = config.get("default_provider", "openai")

        # Initialize providers based on configuration
        provider_configs: Dict[str, Dict[str, Any]] = config.get("providers", {})

        # Default provider configurations
        default_configs: Dict[str, Dict[str, Any]] = {
            "openai": {
                "api_key_env": "OPENAI_API_KEY",
                "default_model": "gpt-4",
                "base_url": None,
            },
            "anthropic": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "default_model": "claude-3-sonnet-20240229",
                "base_url": None,
            },
            "mistral": {
                "api_key_env": "MISTRAL_API_KEY",
                "default_model": "mistral-large-latest",
                "base_url": None,
            },
            "groq": {
                "api_key_env": "GROQ_API_KEY",
                "default_model": "mixtral-8x7b-32768",
                "base_url": None,
            },
            "perplexity": {
                "api_key_env": "PERPLEXITY_API_KEY",
                "default_model": "llama-3.1-sonar-large-128k-online",
                "base_url": None,
            },
            "together": {
                "api_key_env": "TOGETHER_API_KEY",
                "default_model": "meta-llama/Llama-2-70b-chat-hf",
                "base_url": None,
            },
        }

        # Merge user configs with defaults
        for provider_name, default_config in default_configs.items():
            user_config: Dict[str, Any] = provider_configs.get(provider_name, {})
            merged_config: Dict[str, Any] = {**default_config, **user_config}

            # Initialize provider
            try:
                if provider_name == "openai":
                    self.providers[provider_name] = OpenAIProvider(merged_config)
                elif provider_name == "anthropic":
                    self.providers[provider_name] = AnthropicProvider(merged_config)
                elif provider_name == "mistral":
                    self.providers[provider_name] = MistralProvider(merged_config)
                elif provider_name == "groq":
                    self.providers[provider_name] = GroqProvider(merged_config)
                elif provider_name == "perplexity":
                    self.providers[provider_name] = PerplexityProvider(merged_config)
                elif provider_name == "together":
                    self.providers[provider_name] = TogetherAIProvider(merged_config)
            except Exception as e:
                print(f"Failed to initialize {provider_name} provider: {e}")

    def complete(
        self, request: LLMRequest, provider: Optional[str] = None
    ) -> LLMResponse:
        """Complete a request using the specified provider or fallback chain."""

        # Determine which providers to try
        providers_to_try: List[str] = []

        if provider and provider in self.providers:
            providers_to_try.append(provider)
        elif self.default_provider in self.providers:
            providers_to_try.append(self.default_provider)

        # Add fallback providers
        for fallback in self.fallback_order:
            if fallback not in providers_to_try and fallback in self.providers:
                providers_to_try.append(fallback)

        # Try each provider in order
        last_error: Optional[str] = None
        for provider_name in providers_to_try:
            provider_instance: BaseLLMProvider = self.providers[provider_name]

            if not provider_instance.is_available():
                continue

            try:
                response: LLMResponse = provider_instance.complete(request)
                if not response.error:
                    return response
                last_error = response.error
            except Exception as e:
                last_error = str(e)
                continue

        # If all providers failed
        return LLMResponse(
            content="",
            model="unknown",
            error=f"All providers failed. Last error: {last_error}",
        )

    def get_available_providers(self) -> List[str]:
        """Get list of available providers."""
        return [
            name for name, provider in self.providers.items() if provider.is_available()
        ]

    def get_provider_info(self) -> Dict[str, Dict[str, Any]]:
        """Get information about all providers."""
        info: Dict[str, Dict[str, Any]] = {}
        for name, provider in self.providers.items():
            info[name] = {
                "available": provider.is_available(),
                "default_model": provider.default_model,
                "base_url": provider.base_url,
            }
        return info


# Global provider manager instance
_provider_manager: Optional[LLMProviderManager] = None


def get_llm_provider_manager() -> LLMProviderManager:
    """Get or create the global LLM provider manager."""
    global _provider_manager

    if _provider_manager is None:
        # Load configuration from environment
        config: Dict[str, Any] = {
            "default_provider": os.getenv("AUTOPR_DEFAULT_LLM_PROVIDER", "openai"),
            "fallback_order": os.getenv(
                "AUTOPR_LLM_FALLBACK_ORDER", "openai,anthropic,mistral"
            ).split(","),
            "providers": {
                "openai": {"default_model": os.getenv("AUTOPR_OPENAI_MODEL", "gpt-4")},
                "anthropic": {
                    "default_model": os.getenv(
                        "AUTOPR_ANTHROPIC_MODEL", "claude-3-sonnet-20240229"
                    )
                },
                "mistral": {
                    "default_model": os.getenv(
                        "AUTOPR_MISTRAL_MODEL", "mistral-large-latest"
                    )
                },
                "groq": {
                    "default_model": os.getenv(
                        "AUTOPR_GROQ_MODEL", "mixtral-8x7b-32768"
                    )
                },
                "perplexity": {
                    "default_model": os.getenv(
                        "AUTOPR_PERPLEXITY_MODEL", "llama-3.1-sonar-large-128k-online"
                    )
                },
                "together": {
                    "default_model": os.getenv(
                        "AUTOPR_TOGETHER_MODEL", "meta-llama/Llama-2-70b-chat-hf"
                    )
                },
            },
        }

        _provider_manager = LLMProviderManager(config)

    return _provider_manager


def complete_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    provider: Optional[str] = None,
    **kwargs: Any,
) -> LLMResponse:
    """Convenience function for chat completion."""
    llm_messages: List[LLMMessage] = [
        LLMMessage(role=msg["role"], content=msg["content"]) for msg in messages
    ]
    request: LLMRequest = LLMRequest(messages=llm_messages, model=model, **kwargs)

    manager: LLMProviderManager = get_llm_provider_manager()
    return manager.complete(request, provider=provider)
