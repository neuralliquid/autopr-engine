"""
AutoPR Engine - Core Engine Implementation

The main AutoPR engine that orchestrates AI-powered GitHub automation.
"""

import logging
from typing import Dict, Any, Optional, List
from pathlib import Path

from .config import AutoPRConfig
from .exceptions import AutoPRException
from .workflows.engine import WorkflowEngine
from .actions.registry import ActionRegistry
from .integrations.registry import IntegrationRegistry
from .ai.providers.manager import LLMProviderManager

logger = logging.getLogger(__name__)


class AutoPREngine:
    """
    Main AutoPR Engine class that coordinates all automation activities.

    This class serves as the central orchestrator for:
    - Workflow execution
    - Action processing
    - Integration management
    - AI/LLM provider coordination
    """

    def __init__(self, config: Optional[AutoPRConfig] = None):
        """
        Initialize the AutoPR Engine.

        Args:
            config: Configuration object. If None, loads default config.
        """
        self.config = config or AutoPRConfig()
        self.workflow_engine = WorkflowEngine(self.config)
        self.action_registry: ActionRegistry = ActionRegistry()
        self.integration_registry = IntegrationRegistry()
        self.llm_manager = LLMProviderManager(self.config)

        logger.info("AutoPR Engine initialized successfully")

    async def start(self) -> None:
        """Start the AutoPR Engine and initialize all components."""
        try:
            await self.workflow_engine.start()
            await self.integration_registry.initialize()
            await self.llm_manager.initialize()
            logger.info("AutoPR Engine started successfully")
        except Exception as e:
            logger.error(f"Failed to start AutoPR Engine: {e}")
            raise AutoPRException(f"Engine startup failed: {e}")

    async def stop(self) -> None:
        """Stop the AutoPR Engine and cleanup resources."""
        try:
            await self.workflow_engine.stop()
            await self.integration_registry.cleanup()
            await self.llm_manager.cleanup()
            logger.info("AutoPR Engine stopped successfully")
        except Exception as e:
            logger.error(f"Error during engine shutdown: {e}")
            raise AutoPRException(f"Engine shutdown failed: {e}")

    async def process_event(self, event_type: str, event_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an incoming event through the workflow engine.

        Args:
            event_type: Type of event (e.g., 'pull_request', 'issue', 'push')
            event_data: Event payload data

        Returns:
            Processing result dictionary
        """
        try:
            result = await self.workflow_engine.process_event(event_type, event_data)
            logger.info(f"Successfully processed {event_type} event")
            return result
        except Exception as e:
            logger.error(f"Failed to process {event_type} event: {e}")
            raise AutoPRException(f"Event processing failed: {e}")

    def get_status(self) -> Dict[str, Any]:
        """
        Get the current status of the AutoPR Engine.

        Returns:
            Status dictionary with component information
        """
        return {
            "engine": "running",
            "workflow_engine": self.workflow_engine.get_status(),
            "actions": len(self.action_registry.get_all_actions()),
            "integrations": len(self.integration_registry.get_all_integrations()),
            "llm_providers": len(self.llm_manager.get_available_providers()),
            "config": self.config.to_dict(),
        }

    def get_version(self) -> str:
        """Get the AutoPR Engine version."""
        from . import __version__

        return __version__
