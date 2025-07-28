"""
Enhanced Configuration Management for AutoPR Engine

This module provides a comprehensive configuration system with:
- Environment-specific configurations
- Validation and type checking
- Secure secret handling
- Configuration inheritance
- Hot reloading capabilities
"""

import json
import logging
import os
from dataclasses import dataclass, field, fields
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional, Type, Union

import yaml
from pydantic import BaseModel, Field, SecretStr, validator

try:
    # Pydantic 2.0+ (preferred)
    from pydantic_settings import BaseSettings
except ImportError:
    try:
        # Pydantic 1.x fallback
        from pydantic.env_settings import BaseSettings
    except ImportError:
        # Final fallback - create a basic BaseSettings class
        from pydantic import BaseModel

        class BaseSettings(BaseModel):
            """Fallback BaseSettings implementation for compatibility."""

            class Config:
                env_file = ".env"
                env_file_encoding = "utf-8"
                case_sensitive = False


class Environment(str, Enum):
    """Environment types."""

    DEVELOPMENT = "development"
    TESTING = "testing"
    STAGING = "staging"
    PRODUCTION = "production"


class LogLevel(str, Enum):
    """Logging levels."""

    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LLMProvider(str, Enum):
    """Supported LLM providers."""

    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    GROQ = "groq"
    PERPLEXITY = "perplexity"
    TOGETHER = "together"


class GitHubConfig(BaseModel):
    """GitHub integration configuration."""

    token: Optional[SecretStr] = Field(None, env="GITHUB_TOKEN")
    app_id: Optional[str] = Field(None, env="GITHUB_APP_ID")
    private_key: Optional[SecretStr] = Field(None, env="GITHUB_PRIVATE_KEY")
    webhook_secret: Optional[SecretStr] = Field(None, env="GITHUB_WEBHOOK_SECRET")
    base_url: str = Field("https://api.github.com", env="GITHUB_BASE_URL")
    timeout: int = Field(30, env="GITHUB_TIMEOUT")
    max_retries: int = Field(3, env="GITHUB_MAX_RETRIES")

    @validator("timeout")
    def validate_timeout(cls, v):
        if v <= 0:
            raise ValueError("timeout must be positive")
        return v


class LLMConfig(BaseModel):
    """LLM provider configuration."""

    default_provider: LLMProvider = Field(LLMProvider.OPENAI, env="DEFAULT_LLM_PROVIDER")
    fallback_order: List[LLMProvider] = Field(
        default_factory=lambda: [LLMProvider.OPENAI, LLMProvider.ANTHROPIC, LLMProvider.MISTRAL]
    )

    # Provider-specific configurations
    openai_api_key: Optional[SecretStr] = Field(None, env="OPENAI_API_KEY")
    openai_base_url: Optional[str] = Field(None, env="OPENAI_BASE_URL")
    openai_default_model: str = Field("gpt-4", env="OPENAI_DEFAULT_MODEL")

    anthropic_api_key: Optional[SecretStr] = Field(None, env="ANTHROPIC_API_KEY")
    anthropic_base_url: Optional[str] = Field(None, env="ANTHROPIC_BASE_URL")
    anthropic_default_model: str = Field("claude-3-sonnet-20240229", env="ANTHROPIC_DEFAULT_MODEL")

    mistral_api_key: Optional[SecretStr] = Field(None, env="MISTRAL_API_KEY")
    mistral_base_url: Optional[str] = Field(None, env="MISTRAL_BASE_URL")
    mistral_default_model: str = Field("mistral-large-latest", env="MISTRAL_DEFAULT_MODEL")

    groq_api_key: Optional[SecretStr] = Field(None, env="GROQ_API_KEY")
    groq_base_url: Optional[str] = Field(None, env="GROQ_BASE_URL")
    groq_default_model: str = Field("mixtral-8x7b-32768", env="GROQ_DEFAULT_MODEL")

    perplexity_api_key: Optional[SecretStr] = Field(None, env="PERPLEXITY_API_KEY")
    perplexity_base_url: Optional[str] = Field(None, env="PERPLEXITY_BASE_URL")
    perplexity_default_model: str = Field(
        "llama-3.1-sonar-large-128k-online", env="PERPLEXITY_DEFAULT_MODEL"
    )

    together_api_key: Optional[SecretStr] = Field(None, env="TOGETHER_API_KEY")
    together_base_url: Optional[str] = Field(None, env="TOGETHER_BASE_URL")
    together_default_model: str = Field(
        "meta-llama/Llama-2-70b-chat-hf", env="TOGETHER_DEFAULT_MODEL"
    )

    # General LLM settings
    max_tokens: int = Field(4000, env="LLM_MAX_TOKENS")
    temperature: float = Field(0.7, env="LLM_TEMPERATURE")
    timeout: int = Field(60, env="LLM_TIMEOUT")
    max_retries: int = Field(3, env="LLM_MAX_RETRIES")

    @validator("temperature")
    def validate_temperature(cls, v):
        if not 0 <= v <= 2:
            raise ValueError("temperature must be between 0 and 2")
        return v


class DatabaseConfig(BaseModel):
    """Database configuration."""

    url: Optional[str] = Field(None, env="DATABASE_URL")
    pool_size: int = Field(10, env="DATABASE_POOL_SIZE")
    max_overflow: int = Field(20, env="DATABASE_MAX_OVERFLOW")
    pool_timeout: int = Field(30, env="DATABASE_POOL_TIMEOUT")
    pool_recycle: int = Field(3600, env="DATABASE_POOL_RECYCLE")
    echo: bool = Field(False, env="DATABASE_ECHO")


class RedisConfig(BaseModel):
    """Redis configuration."""

    url: Optional[str] = Field(None, env="REDIS_URL")
    host: str = Field("localhost", env="REDIS_HOST")
    port: int = Field(6379, env="REDIS_PORT")
    db: int = Field(0, env="REDIS_DB")
    password: Optional[SecretStr] = Field(None, env="REDIS_PASSWORD")
    ssl: bool = Field(False, env="REDIS_SSL")
    timeout: int = Field(5, env="REDIS_TIMEOUT")
    max_connections: int = Field(50, env="REDIS_MAX_CONNECTIONS")


class WorkflowConfig(BaseModel):
    """Workflow execution configuration."""

    max_concurrent: int = Field(10, env="MAX_CONCURRENT_WORKFLOWS")
    timeout: int = Field(300, env="WORKFLOW_TIMEOUT")
    retry_attempts: int = Field(3, env="WORKFLOW_RETRY_ATTEMPTS")
    retry_delay: int = Field(5, env="WORKFLOW_RETRY_DELAY")
    enable_parallel_execution: bool = Field(True, env="ENABLE_PARALLEL_EXECUTION")


class MonitoringConfig(BaseModel):
    """Monitoring and observability configuration."""

    enable_metrics: bool = Field(True, env="ENABLE_METRICS")
    metrics_port: int = Field(8000, env="METRICS_PORT")
    enable_tracing: bool = Field(False, env="ENABLE_TRACING")
    jaeger_endpoint: Optional[str] = Field(None, env="JAEGER_ENDPOINT")
    sentry_dsn: Optional[SecretStr] = Field(None, env="SENTRY_DSN")
    log_level: LogLevel = Field(LogLevel.INFO, env="LOG_LEVEL")
    structured_logging: bool = Field(True, env="STRUCTURED_LOGGING")


class SecurityConfig(BaseModel):
    """Security configuration."""

    secret_key: Optional[SecretStr] = Field(None, env="SECRET_KEY")
    jwt_secret: Optional[SecretStr] = Field(None, env="JWT_SECRET")
    jwt_expiry: int = Field(3600, env="JWT_EXPIRY")  # seconds
    rate_limit_per_minute: int = Field(60, env="RATE_LIMIT_PER_MINUTE")
    enable_cors: bool = Field(True, env="ENABLE_CORS")
    allowed_origins: List[str] = Field(default_factory=list, env="ALLOWED_ORIGINS")
    enable_csrf_protection: bool = Field(True, env="ENABLE_CSRF_PROTECTION")


class AutoPRSettings(BaseSettings):
    """
    Main settings class for AutoPR Engine.

    This class combines all configuration sections and provides
    environment-specific loading, validation, and management.
    """

    # Environment and basic settings
    environment: Environment = Field(Environment.DEVELOPMENT, env="AUTOPR_ENVIRONMENT")
    debug: bool = Field(False, env="DEBUG")
    version: str = Field("1.0.0", env="AUTOPR_VERSION")

    # Configuration sections
    github: GitHubConfig = Field(default_factory=GitHubConfig)
    llm: LLMConfig = Field(default_factory=LLMConfig)
    database: DatabaseConfig = Field(default_factory=DatabaseConfig)
    redis: RedisConfig = Field(default_factory=RedisConfig)
    workflow: WorkflowConfig = Field(default_factory=WorkflowConfig)
    monitoring: MonitoringConfig = Field(default_factory=MonitoringConfig)
    security: SecurityConfig = Field(default_factory=SecurityConfig)

    # Custom settings for extensions
    custom: Dict[str, Any] = Field(default_factory=dict)

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        validate_assignment = True
        extra = "allow"  # Allow additional fields for custom settings

    def __init__(self, **kwargs):
        """Initialize settings with environment-specific overrides."""
        super().__init__(**kwargs)
        self._load_environment_specific_config()
        self._load_custom_config()

    def _load_environment_specific_config(self) -> None:
        """Load environment-specific configuration overrides."""
        config_dir = Path(__file__).parent / "environments"
        env_config_file = config_dir / f"{self.environment.value}.yaml"

        if env_config_file.exists():
            try:
                with open(env_config_file, "r", encoding="utf-8") as f:
                    env_config = yaml.safe_load(f)

                if env_config:
                    self._apply_config_overrides(env_config)
            except Exception as e:
                logging.warning(f"Failed to load environment config from {env_config_file}: {e}")

    def _load_custom_config(self) -> None:
        """Load custom configuration from various sources."""
        config_paths = [
            Path.cwd() / "autopr.yaml",
            Path.cwd() / "autopr.yml",
            Path.cwd() / ".autopr.yaml",
            Path.cwd() / ".autopr.yml",
            Path.home() / ".autopr.yaml",
            Path.home() / ".autopr.yml",
        ]

        for config_path in config_paths:
            if config_path.exists():
                try:
                    with open(config_path, "r", encoding="utf-8") as f:
                        custom_config = yaml.safe_load(f)

                    if custom_config:
                        self._apply_config_overrides(custom_config)
                        break
                except Exception as e:
                    logging.warning(f"Failed to load custom config from {config_path}: {e}")

    def _apply_config_overrides(self, overrides: Dict[str, Any]) -> None:
        """Apply configuration overrides."""
        for key, value in overrides.items():
            if hasattr(self, key):
                if isinstance(getattr(self, key), BaseModel):
                    # Handle nested configuration objects
                    current_config = getattr(self, key)
                    if isinstance(value, dict):
                        for nested_key, nested_value in value.items():
                            if hasattr(current_config, nested_key):
                                setattr(current_config, nested_key, nested_value)
                else:
                    setattr(self, key, value)
            else:
                # Store in custom settings
                self.custom[key] = value

    def validate_configuration(self) -> List[str]:
        """
        Validate the complete configuration.

        Returns:
            List of validation errors (empty if valid)
        """
        errors = []

        # GitHub validation
        if not self.github.token and not self.github.app_id:
            errors.append(
                "GitHub authentication required: provide either GITHUB_TOKEN or GITHUB_APP_ID"
            )

        # LLM validation
        llm_keys = [
            self.llm.openai_api_key,
            self.llm.anthropic_api_key,
            self.llm.mistral_api_key,
            self.llm.groq_api_key,
            self.llm.perplexity_api_key,
            self.llm.together_api_key,
        ]
        if not any(key for key in llm_keys):
            errors.append("At least one LLM provider API key is required")

        # Production-specific validations
        if self.environment == Environment.PRODUCTION:
            if not self.security.secret_key:
                errors.append("SECRET_KEY is required in production")
            if self.debug:
                errors.append("DEBUG should be False in production")
            if self.monitoring.log_level == LogLevel.DEBUG:
                errors.append("LOG_LEVEL should not be DEBUG in production")

        return errors

    def get_provider_config(self, provider: LLMProvider) -> Dict[str, Any]:
        """Get configuration for a specific LLM provider."""
        provider_configs = {
            LLMProvider.OPENAI: {
                "api_key": self.llm.openai_api_key,
                "base_url": self.llm.openai_base_url,
                "default_model": self.llm.openai_default_model,
            },
            LLMProvider.ANTHROPIC: {
                "api_key": self.llm.anthropic_api_key,
                "base_url": self.llm.anthropic_base_url,
                "default_model": self.llm.anthropic_default_model,
            },
            LLMProvider.MISTRAL: {
                "api_key": self.llm.mistral_api_key,
                "base_url": self.llm.mistral_base_url,
                "default_model": self.llm.mistral_default_model,
            },
            LLMProvider.GROQ: {
                "api_key": self.llm.groq_api_key,
                "base_url": self.llm.groq_base_url,
                "default_model": self.llm.groq_default_model,
            },
            LLMProvider.PERPLEXITY: {
                "api_key": self.llm.perplexity_api_key,
                "base_url": self.llm.perplexity_base_url,
                "default_model": self.llm.perplexity_default_model,
            },
            LLMProvider.TOGETHER: {
                "api_key": self.llm.together_api_key,
                "base_url": self.llm.together_base_url,
                "default_model": self.llm.together_default_model,
            },
        }

        config = provider_configs.get(provider, {})
        # Add common settings
        config.update(
            {
                "max_tokens": self.llm.max_tokens,
                "temperature": self.llm.temperature,
                "timeout": self.llm.timeout,
                "max_retries": self.llm.max_retries,
            }
        )

        return config

    def to_safe_dict(self) -> Dict[str, Any]:
        """
        Convert settings to dictionary with sensitive data masked.

        Returns:
            Dictionary representation with secrets masked
        """

        def mask_secrets(obj):
            if isinstance(obj, SecretStr):
                return "***" if obj else None
            elif isinstance(obj, BaseModel):
                return {k: mask_secrets(v) for k, v in obj.dict().items()}
            elif isinstance(obj, dict):
                return {k: mask_secrets(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [mask_secrets(item) for item in obj]
            else:
                return obj

        return mask_secrets(self.dict())

    def reload(self) -> None:
        """Reload configuration from all sources."""
        self._load_environment_specific_config()
        self._load_custom_config()

    @classmethod
    def from_file(cls, config_path: Union[str, Path]) -> "AutoPRSettings":
        """
        Create settings instance from configuration file.

        Args:
            config_path: Path to configuration file

        Returns:
            AutoPRSettings instance
        """
        config_path = Path(config_path)
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")

        with open(config_path, "r", encoding="utf-8") as f:
            if config_path.suffix.lower() in [".yaml", ".yml"]:
                config_data = yaml.safe_load(f)
            elif config_path.suffix.lower() == ".json":
                config_data = json.load(f)
            else:
                raise ValueError(f"Unsupported configuration file format: {config_path.suffix}")

        return cls(**config_data)


# Global settings instance
_settings: Optional[AutoPRSettings] = None


def get_settings() -> AutoPRSettings:
    """
    Get the global settings instance.

    Returns:
        AutoPRSettings instance
    """
    global _settings
    if _settings is None:
        _settings = AutoPRSettings()
    return _settings


def reload_settings() -> AutoPRSettings:
    """
    Reload the global settings instance.

    Returns:
        Reloaded AutoPRSettings instance
    """
    global _settings
    _settings = None
    return get_settings()


def set_settings(settings: AutoPRSettings) -> None:
    """
    Set the global settings instance.

    Args:
        settings: AutoPRSettings instance to set as global
    """
    global _settings
    _settings = settings
