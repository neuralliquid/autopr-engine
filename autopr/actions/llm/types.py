"""
Base types, enums, and data classes for LLM providers.
"""

from typing import Dict, Any, Optional, List
from pydantic import BaseModel, Field
from enum import Enum
from dataclasses import dataclass


class MessageRole(str, Enum):
    """Role of a message in a chat conversation."""

    SYSTEM = "system"
    USER = "user"
    ASSISTANT = "assistant"
    TOOL = "tool"


class Message(BaseModel):
    """A message in a chat conversation."""

    role: MessageRole
    content: str
    name: Optional[str] = None
    tool_calls: Optional[List[Dict[str, Any]]] = None
    tool_call_id: Optional[str] = None


class LLMProviderType(str, Enum):
    """Supported LLM providers."""

    GROQ = "groq"
    MISTRAL = "mistral"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    PERPLEXITY = "perplexity"
    TOGETHER = "together"


class LLMConfig(BaseModel):
    """Configuration for an LLM provider."""

    provider: LLMProviderType
    model: str
    api_key: Optional[str] = None
    base_url: Optional[str] = None
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop: Optional[List[str]] = None


@dataclass
class LLMResponse:
    """Response from an LLM provider."""

    content: str
    model: str
    finish_reason: str
    usage: Optional[Dict[str, int]] = None
    error: Optional[str] = None

    @classmethod
    def from_error(cls, error: str, model: str = "unknown") -> "LLMResponse":
        """Create an error response."""
        return cls(content="", model=model, finish_reason="error", error=error)
