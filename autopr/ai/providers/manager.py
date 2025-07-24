"""
AutoPR LLM Provider Manager

Manages multiple LLM providers and provides unified access.
"""

import logging
from typing import Dict, List, Optional, Type
from ..base import LLMProvider, LLMMessage, LLMResponse, OpenAIProvider, AnthropicProvider

logger = logging.getLogger(__name__)


class LLMProviderManager:
    """
    Manager for LLM providers.
    
    Handles registration, initialization, and routing of LLM requests
    to appropriate providers.
    """
    
    def __init__(self, config):
        """
        Initialize the LLM provider manager.
        
        Args:
            config: AutoPR configuration object
        """
        self.config = config
        self.providers: Dict[str, LLMProvider] = {}
        self.default_provider: Optional[str] = None
        
        # Register built-in providers
        self._register_builtin_providers()
        
        logger.info("LLM provider manager initialized")
    
    def _register_builtin_providers(self) -> None:
        """Register built-in LLM providers."""
        try:
            # Register OpenAI provider
            openai_provider = OpenAIProvider()
            self.providers[openai_provider.name] = openai_provider
            
            # Register Anthropic provider
            anthropic_provider = AnthropicProvider()
            self.providers[anthropic_provider.name] = anthropic_provider
            
            logger.info("Built-in LLM providers registered")
            
        except Exception as e:
            logger.error(f"Failed to register built-in providers: {e}")
    
    async def initialize(self) -> None:
        """Initialize all configured LLM providers."""
        # Initialize OpenAI if configured
        if hasattr(self.config, 'openai_api_key') and self.config.openai_api_key:
            try:
                await self.providers["openai"].initialize({
                    "api_key": self.config.openai_api_key
                })
                if not self.default_provider:
                    self.default_provider = "openai"
                logger.info("OpenAI provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI provider: {e}")
        
        # Initialize Anthropic if configured
        if hasattr(self.config, 'anthropic_api_key') and self.config.anthropic_api_key:
            try:
                await self.providers["anthropic"].initialize({
                    "api_key": self.config.anthropic_api_key
                })
                if not self.default_provider:
                    self.default_provider = "anthropic"
                logger.info("Anthropic provider initialized")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic provider: {e}")
        
        # Set default provider from config
        if hasattr(self.config, 'default_llm_provider') and self.config.default_llm_provider:
            if self.config.default_llm_provider in self.providers:
                provider = self.providers[self.config.default_llm_provider]
                if provider.is_initialized:
                    self.default_provider = self.config.default_llm_provider
    
    async def cleanup(self) -> None:
        """Clean up all LLM providers."""
        for provider_name, provider in self.providers.items():
            try:
                await provider.cleanup()
                logger.info(f"Cleaned up LLM provider: {provider_name}")
            except Exception as e:
                logger.error(f"Error cleaning up provider '{provider_name}': {e}")
    
    def register_provider(self, provider: LLMProvider) -> None:
        """
        Register a custom LLM provider.
        
        Args:
            provider: LLM provider instance
        """
        self.providers[provider.name] = provider
        logger.info(f"Registered custom LLM provider: {provider.name}")
    
    def get_provider(self, provider_name: Optional[str] = None) -> Optional[LLMProvider]:
        """
        Get an LLM provider by name.
        
        Args:
            provider_name: Name of provider to get (uses default if None)
            
        Returns:
            LLM provider instance or None
        """
        if provider_name is None:
            provider_name = self.default_provider
        
        if provider_name is None:
            logger.warning("No default LLM provider configured")
            return None
        
        if provider_name not in self.providers:
            logger.warning(f"LLM provider not found: {provider_name}")
            return None
        
        provider = self.providers[provider_name]
        if not provider.is_initialized:
            logger.warning(f"LLM provider not initialized: {provider_name}")
            return None
        
        return provider
    
    async def generate_completion(
        self,
        messages: List[LLMMessage],
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ) -> Optional[LLMResponse]:
        """
        Generate a completion using the specified or default provider.
        
        Args:
            messages: List of conversation messages
            provider_name: Provider to use (defaults to configured default)
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Returns:
            LLM response or None if failed
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return None
        
        try:
            response = await provider.generate_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            )
            logger.info(f"Generated completion using provider: {provider.name}")
            return response
            
        except Exception as e:
            logger.error(f"Failed to generate completion with provider '{provider.name}': {e}")
            return None
    
    async def generate_stream_completion(
        self,
        messages: List[LLMMessage],
        provider_name: Optional[str] = None,
        model: Optional[str] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000,
        **kwargs
    ):
        """
        Generate a streaming completion using the specified or default provider.
        
        Args:
            messages: List of conversation messages
            provider_name: Provider to use (defaults to configured default)
            model: Model name to use
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional provider-specific parameters
            
        Yields:
            Partial LLM responses
        """
        provider = self.get_provider(provider_name)
        if not provider:
            return
        
        try:
            async for response in provider.generate_stream_completion(
                messages=messages,
                model=model,
                temperature=temperature,
                max_tokens=max_tokens,
                **kwargs
            ):
                yield response
                
        except Exception as e:
            logger.error(f"Failed to generate streaming completion with provider '{provider.name}': {e}")
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available (initialized) providers.
        
        Returns:
            List of provider names
        """
        return [
            name for name, provider in self.providers.items()
            if provider.is_initialized
        ]
    
    def get_all_providers(self) -> List[str]:
        """
        Get list of all registered providers.
        
        Returns:
            List of provider names
        """
        return list(self.providers.keys())
    
    async def health_check_all(self) -> Dict[str, Dict]:
        """
        Perform health check on all providers.
        
        Returns:
            Dictionary mapping provider names to health status
        """
        health_status = {}
        
        for provider_name, provider in self.providers.items():
            try:
                status = await provider.health_check()
                health_status[provider_name] = status
            except Exception as e:
                health_status[provider_name] = {
                    "status": "error",
                    "message": f"Health check failed: {e}"
                }
        
        return health_status
    
    def get_manager_stats(self) -> Dict[str, any]:
        """
        Get manager statistics.
        
        Returns:
            Dictionary with manager statistics
        """
        return {
            "total_providers": len(self.providers),
            "initialized_providers": len(self.get_available_providers()),
            "default_provider": self.default_provider,
            "providers": {
                name: provider.get_metadata()
                for name, provider in self.providers.items()
            }
        }
