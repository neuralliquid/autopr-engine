"""
AutoPR Configuration Module

Handles configuration loading, validation, and management.
"""

import os
import yaml
from typing import Dict, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field


@dataclass
class AutoPRConfig:
    """
    Main configuration class for AutoPR Engine.
    
    Handles loading configuration from environment variables,
    YAML files, and provides sensible defaults.
    """
    
    # GitHub configuration
    github_token: Optional[str] = None
    github_app_id: Optional[str] = None
    github_private_key: Optional[str] = None
    github_webhook_secret: Optional[str] = None
    
    # AI/LLM configuration
    openai_api_key: Optional[str] = None
    anthropic_api_key: Optional[str] = None
    default_llm_provider: str = "openai"
    
    # Engine configuration
    max_concurrent_workflows: int = 10
    workflow_timeout: int = 300  # seconds
    enable_debug_logging: bool = False
    
    # Database configuration
    database_url: Optional[str] = None
    redis_url: Optional[str] = None
    
    # Additional settings
    custom_settings: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self) -> None:
        """Load configuration from environment variables after initialization."""
        self._load_from_environment()
        self._load_from_file()
    
    def _load_from_environment(self) -> None:
        """Load configuration from environment variables."""
        env_mappings = {
            'GITHUB_TOKEN': 'github_token',
            'GITHUB_APP_ID': 'github_app_id', 
            'GITHUB_PRIVATE_KEY': 'github_private_key',
            'GITHUB_WEBHOOK_SECRET': 'github_webhook_secret',
            'OPENAI_API_KEY': 'openai_api_key',
            'ANTHROPIC_API_KEY': 'anthropic_api_key',
            'DEFAULT_LLM_PROVIDER': 'default_llm_provider',
            'DATABASE_URL': 'database_url',
            'REDIS_URL': 'redis_url',
            'MAX_CONCURRENT_WORKFLOWS': 'max_concurrent_workflows',
            'WORKFLOW_TIMEOUT': 'workflow_timeout',
            'ENABLE_DEBUG_LOGGING': 'enable_debug_logging'
        }
        
        for env_var, attr_name in env_mappings.items():
            env_value = os.getenv(env_var)
            if env_value is not None:
                # Handle type conversion
                if attr_name in ['max_concurrent_workflows', 'workflow_timeout']:
                    setattr(self, attr_name, int(env_value))
                elif attr_name == 'enable_debug_logging':
                    setattr(self, attr_name, env_value.lower() in ('true', '1', 'yes', 'on'))
                else:
                    setattr(self, attr_name, env_value)
    
    def _load_from_file(self, config_path: Optional[str] = None) -> None:
        """Load configuration from YAML file."""
        if config_path is None:
            # Look for config file in common locations
            possible_paths = [
                'autopr.yaml',
                'autopr.yml', 
                '.autopr.yaml',
                '.autopr.yml',
                os.path.expanduser('~/.autopr.yaml'),
                os.path.expanduser('~/.autopr.yml')
            ]
            
            for path in possible_paths:
                if os.path.exists(path):
                    config_path = path
                    break
        
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config_data = yaml.safe_load(f)
                    
                if config_data:
                    for key, value in config_data.items():
                        if hasattr(self, key):
                            setattr(self, key, value)
                        else:
                            self.custom_settings[key] = value
            except Exception as e:
                # Don't fail if config file is malformed, just log and continue
                import logging
                logging.warning(f"Failed to load config from {config_path}: {e}")
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration to dictionary."""
        result = {}
        for field_name in self.__dataclass_fields__:
            value = getattr(self, field_name)
            # Don't include sensitive information in dict representation
            if 'key' in field_name.lower() or 'token' in field_name.lower() or 'secret' in field_name.lower():
                result[field_name] = '***' if value else None
            else:
                result[field_name] = value
        return result
    
    def validate(self) -> bool:
        """
        Validate the configuration.
        
        Returns:
            True if configuration is valid, False otherwise
        """
        # Basic validation - ensure we have at least one way to authenticate with GitHub
        if not any([self.github_token, self.github_app_id]):
            return False
            
        # Ensure we have at least one LLM provider configured
        if not any([self.openai_api_key, self.anthropic_api_key]):
            return False
            
        return True
    
    @classmethod
    def from_file(cls, config_path: str) -> 'AutoPRConfig':
        """
        Create configuration instance from file.
        
        Args:
            config_path: Path to configuration file
            
        Returns:
            AutoPRConfig instance
        """
        config = cls()
        config._load_from_file(config_path)
        return config
