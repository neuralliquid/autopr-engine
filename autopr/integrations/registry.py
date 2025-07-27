"""
AutoPR Integration Registry

Registry for managing and discovering integrations.
"""

import logging
from typing import Any, Dict, List, Optional, Type

from .base import Integration

logger = logging.getLogger(__name__)


class IntegrationRegistry:
    """
    Registry for managing AutoPR integrations.

    Provides registration, discovery, and management of integrations.
    """

    def __init__(self) -> None:
        """Initialize the integration registry."""
        self._integrations: Dict[str, Type[Integration]] = {}
        self._instances: Dict[str, Integration] = {}

        logger.info("Integration registry initialized")

    def register_integration(self, integration_class: Type[Integration]) -> None:
        """
        Register an integration class.

        Args:
            integration_class: Integration class to register
        """
        # Create a temporary instance to get the name
        temp_instance = integration_class("temp", "temp")
        integration_name = temp_instance.name

        self._integrations[integration_name] = integration_class
        logger.info(f"Registered integration: {integration_name}")

    def unregister_integration(self, integration_name: str) -> None:
        """
        Unregister an integration.

        Args:
            integration_name: Name of integration to unregister
        """
        if integration_name in self._integrations:
            del self._integrations[integration_name]

        if integration_name in self._instances:
            # Clean up instance
            instance = self._instances[integration_name]
            try:
                # Note: This is synchronous, but cleanup might be async
                # In a real implementation, you'd want to handle this properly
                pass
            except Exception as e:
                logger.error(f"Error cleaning up integration '{integration_name}': {e}")

            del self._instances[integration_name]

        logger.info(f"Unregistered integration: {integration_name}")

    async def get_integration(
        self, integration_name: str, config: Optional[Dict[str, Any]] = None
    ) -> Optional[Integration]:
        """
        Get an integration instance by name.

        Args:
            integration_name: Name of integration to get
            config: Configuration for the integration

        Returns:
            Integration instance or None if not found
        """
        if integration_name not in self._integrations:
            logger.warning(f"Integration not found: {integration_name}")
            return None

        # Return cached instance if available and initialized
        if integration_name in self._instances:
            instance = self._instances[integration_name]
            if instance.is_initialized:
                return instance

        # Create new instance
        try:
            integration_class = self._integrations[integration_name]
            instance = integration_class(integration_name, f"Instance of {integration_name}")

            # Initialize if config provided
            if config:
                await instance.initialize(config)

            self._instances[integration_name] = instance
            return instance

        except Exception as e:
            logger.error(f"Failed to create integration instance '{integration_name}': {e}")
            return None

    async def initialize(self, configs: Optional[Dict[str, Dict[str, Any]]] = None) -> None:
        """
        Initialize all registered integrations.

        Args:
            configs: Dictionary mapping integration names to their configs
        """
        if not configs:
            configs = {}

        for integration_name in self._integrations:
            if integration_name in configs:
                try:
                    await self.get_integration(integration_name, configs[integration_name])
                    logger.info(f"Initialized integration: {integration_name}")
                except Exception as e:
                    logger.error(f"Failed to initialize integration '{integration_name}': {e}")

    async def cleanup(self) -> None:
        """Clean up all integration instances."""
        for integration_name, instance in self._instances.items():
            try:
                await instance.cleanup()
                logger.info(f"Cleaned up integration: {integration_name}")
            except Exception as e:
                logger.error(f"Error cleaning up integration '{integration_name}': {e}")

        self._instances.clear()

    def get_all_integrations(self) -> List[str]:
        """
        Get list of all registered integration names.

        Returns:
            List of integration names
        """
        return list(self._integrations.keys())

    def get_initialized_integrations(self) -> List[str]:
        """
        Get list of initialized integration names.

        Returns:
            List of initialized integration names
        """
        return [name for name, instance in self._instances.items() if instance.is_initialized]

    def get_integrations_metadata(self) -> Dict[str, Dict]:
        """
        Get metadata for all registered integrations.

        Returns:
            Dictionary mapping integration names to their metadata
        """
        metadata = {}

        for integration_name in self._integrations:
            if integration_name in self._instances:
                instance = self._instances[integration_name]
                metadata[integration_name] = instance.get_metadata()
            else:
                # Create temporary instance for metadata
                try:
                    integration_class = self._integrations[integration_name]
                    temp_instance = integration_class(integration_name, "Temporary")
                    metadata[integration_name] = temp_instance.get_metadata()
                except Exception as e:
                    logger.error(f"Failed to get metadata for '{integration_name}': {e}")
                    metadata[integration_name] = {"error": str(e)}

        return metadata

    async def health_check_all(self) -> Dict[str, Dict]:
        """
        Perform health check on all initialized integrations.

        Returns:
            Dictionary mapping integration names to health status
        """
        health_status = {}

        for integration_name, instance in self._instances.items():
            try:
                status = await instance.health_check()
                health_status[integration_name] = status
            except Exception as e:
                health_status[integration_name] = {
                    "status": "error",
                    "message": f"Health check failed: {e}",
                }

        return health_status

    def search_integrations(self, query: str) -> List[str]:
        """
        Search for integrations by name or description.

        Args:
            query: Search query

        Returns:
            List of matching integration names
        """
        query_lower = query.lower()
        matching_integrations = []

        for integration_name in self._integrations:
            if integration_name in self._instances:
                instance = self._instances[integration_name]
                if (
                    query_lower in instance.name.lower()
                    or query_lower in instance.description.lower()
                ):
                    matching_integrations.append(integration_name)
            else:
                # Check class name
                if query_lower in integration_name.lower():
                    matching_integrations.append(integration_name)

        return matching_integrations

    def get_registry_stats(self) -> Dict[str, int]:
        """
        Get registry statistics.

        Returns:
            Dictionary with registry statistics
        """
        return {
            "total_integrations": len(self._integrations),
            "initialized_integrations": len(
                [instance for instance in self._instances.values() if instance.is_initialized]
            ),
            "total_instances": len(self._instances),
        }
