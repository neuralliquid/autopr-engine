"""
AutoPR Action: Configurable LLM Provider
Unified interface for multiple LLM providers (OpenAI, Anthropic, Mistral, Groq, Perplexity, etc.)

This file has been refactored into a modular structure under autopr.actions.llm.
This module maintains backward compatibility by re-exporting the modular components.
"""

# Re-export everything from the modular LLM package for backward compatibility
from .llm import (
    # Types
    MessageRole,
    Message,
    LLMProviderType,
    LLMConfig,
    LLMResponse,
    # Base classes
    BaseLLMProvider,
    # Manager
    LLMProviderManager,
    # Providers
    OpenAIProvider,
    AnthropicProvider,
    MistralProvider,
    GroqProvider,
    PerplexityProvider,
    TogetherAIProvider,
    # Factory functions
    get_llm_provider_manager,
    complete_chat,
)

# Maintain the same public API
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
    "MistralProvider",
    "GroqProvider",
    "PerplexityProvider",
    "TogetherAIProvider",
    # Factory functions
    "get_llm_provider_manager",
    "complete_chat",
]
