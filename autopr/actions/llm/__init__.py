"""
AutoPR LLM Package - Modular LLM provider system.

This package provides a unified interface for multiple LLM providers including:
- OpenAI GPT models
- Anthropic Claude models
- Mistral AI models
- Groq models
- Perplexity AI models
- Together AI models

Usage:
    from autopr.actions.llm import get_llm_provider_manager, complete_chat

    # Get a manager instance
    manager = get_llm_provider_manager()

    # Complete a chat
    response = complete_chat([
        {"role": "user", "content": "Hello!"}
    ], provider="openai")
"""

import os
from typing import Dict, Any, Optional, List

# Export types
from .types import MessageRole, Message, LLMProviderType, LLMConfig, LLMResponse

# Export base classes
from .base import BaseLLMProvider

# Export manager
from .manager import LLMProviderManager

# Export providers
from .providers import (
    OpenAIProvider,
    AnthropicProvider,
    GroqProvider,
    MistralProvider,
    PerplexityProvider,
    TogetherAIProvider,
)

# Global provider manager instance
_provider_manager: Optional[LLMProviderManager] = None


def get_llm_provider_manager() -> LLMProviderManager:
    """
    Get or create the global LLM provider manager with configuration from environment variables.

    Returns:
        LLMProviderManager: A configured instance of LLMProviderManager
    """
    global _provider_manager

    if _provider_manager is not None:
        return _provider_manager

    # Load configuration from environment
    config: Dict[str, Any] = {
        "default_provider": os.getenv("AUTOPR_DEFAULT_LLM_PROVIDER", "openai"),
        "fallback_order": os.getenv("AUTOPR_LLM_FALLBACK_ORDER", "openai,anthropic,mistral").split(
            ","
        ),
        "providers": {
            "openai": {
                "api_key_env": "OPENAI_API_KEY",
                "default_model": os.getenv("AUTOPR_OPENAI_MODEL", "gpt-4"),
                "base_url": os.getenv("OPENAI_API_BASE"),
            },
            "anthropic": {
                "api_key_env": "ANTHROPIC_API_KEY",
                "default_model": os.getenv("AUTOPR_ANTHROPIC_MODEL", "claude-3-sonnet-20240229"),
            },
            "mistral": {
                "api_key_env": "MISTRAL_API_KEY",
                "default_model": os.getenv("AUTOPR_MISTRAL_MODEL", "mistral-large-latest"),
            },
            "groq": {
                "api_key_env": "GROQ_API_KEY",
                "default_model": os.getenv("AUTOPR_GROQ_MODEL", "mixtral-8x7b-32768"),
            },
            "perplexity": {
                "api_key_env": "PERPLEXITY_API_KEY",
                "default_model": os.getenv(
                    "AUTOPR_PERPLEXITY_MODEL", "llama-3.1-sonar-large-128k-online"
                ),
            },
            "together": {
                "api_key_env": "TOGETHER_API_KEY",
                "default_model": os.getenv(
                    "AUTOPR_TOGETHER_MODEL", "meta-llama/Llama-2-70b-chat-hf"
                ),
                "base_url": "https://api.together.xyz/v1",
            },
        },
    }

    # Initialize the provider manager with the configuration
    _provider_manager = LLMProviderManager(config)
    return _provider_manager


def complete_chat(
    messages: List[Dict[str, str]],
    model: Optional[str] = None,
    provider: Optional[str] = None,
    **kwargs: Any,
) -> LLMResponse:
    """
    Convenience function for chat completion.

    Args:
        messages: List of message dictionaries with 'role' and 'content' keys
        model: Optional model name to use for completion
        provider: Optional provider name to use (e.g., 'openai', 'anthropic', etc.)
        **kwargs: Additional arguments to pass to the provider's complete method

    Returns:
        LLMResponse: The completion response from the LLM provider
    """
    request: Dict[str, Any] = {
        "messages": messages,
        "model": model,
        **kwargs,
    }

    manager: LLMProviderManager = get_llm_provider_manager()

    # If a specific provider is requested, get it directly from the manager
    if provider is not None:
        provider_instance = manager.get_provider(provider)
        if provider_instance is None:
            return LLMResponse.from_error(f"Provider '{provider}' not found", model or "unknown")
        return provider_instance.complete(request)

    # Otherwise, use the manager's complete method which handles fallback
    return manager.complete(request)


# Export all public components
__all__ = [
    # Types
    "MessageRole",
    "Message",
    "LLMProviderType",
    "LLMConfig",
    "LLMResponse",
    # Base classes
    "BaseLLMProvider",
    # Manager
    "LLMProviderManager",
    # Providers
    "OpenAIProvider",
    "AnthropicProvider",
    "GroqProvider",
    "MistralProvider",
    "PerplexityProvider",
    "TogetherAIProvider",
    # Factory functions
    "get_llm_provider_manager",
    "complete_chat",
]
