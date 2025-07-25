"""
AutoPR Action Registry

Registry for managing and discovering actions.
"""

import logging
from typing import Dict, List, Optional, Type, Any
from .base import Action

logger = logging.getLogger(__name__)


class ActionRegistry:
    """
    Registry for managing AutoPR actions.

    Provides registration, discovery, and instantiation of actions.
    """

    def __init__(self) -> None:
        """Initialize the action registry."""
        self._actions: Dict[str, Type[Action[Any, Any]]] = {}
        self._instances: Dict[str, Action[Any, Any]] = {}

        # Auto-register built-in actions
        self._register_builtin_actions()

        logger.info("Action registry initialized")

    def register_action(self, action_cls: Type[Action[Any, Any]]) -> None:
        """
        Register an action class.

        Args:
            action_cls: Action class to register
        """
        # Create a temporary instance to get the name
        temp_instance = action_cls("temp", "temp")
        action_name = temp_instance.name

        self._actions[action_name] = action_cls
        logger.info(f"Registered action: {action_name}")

    def unregister_action(self, action_name: str) -> None:
        """
        Unregister an action.

        Args:
            action_name: Name of action to unregister
        """
        if action_name in self._actions:
            del self._actions[action_name]

        if action_name in self._instances:
            del self._instances[action_name]

        logger.info(f"Unregistered action: {action_name}")

    def get_action(self, action_name: str) -> Optional[Action[Any, Any]]:
        """
        Get an action instance by name.

        Args:
            action_name: Name of action to get

        Returns:
            Action instance or None if not found
        """
        if action_name not in self._actions:
            logger.warning(f"Action not found: {action_name}")
            return None

        # Return cached instance if available
        if action_name in self._instances:
            return self._instances[action_name]

        # Create new instance
        try:
            action_cls = self._actions[action_name]
            instance = action_cls(action_name, f"Instance of {action_name}")
            self._instances[action_name] = instance
            return instance
        except Exception as e:
            logger.error(f"Failed to create action instance '{action_name}': {e}")
            return None

    def get_all_actions(self) -> List[str]:
        """
        Get list of all registered action names.

        Returns:
            List of action names
        """
        return list(self._actions.keys())

    def get_actions_by_platform(self, platform: str) -> List[str]:
        """
        Get actions that support a specific platform.

        Args:
            platform: Platform name

        Returns:
            List of action names that support the platform
        """
        supported_actions = []

        for action_name in self._actions:
            action = self.get_action(action_name)
            if action and action.supports_platform(platform):
                supported_actions.append(action_name)

        return supported_actions

    def get_actions_metadata(self) -> Dict[str, Dict]:
        """
        Get metadata for all registered actions.

        Returns:
            Dictionary mapping action names to their metadata
        """
        metadata = {}

        for action_name in self._actions:
            action = self.get_action(action_name)
            if action:
                metadata[action_name] = action.get_metadata()

        return metadata

    def search_actions(self, query: str) -> List[str]:
        """
        Search for actions by name or description.

        Args:
            query: Search query

        Returns:
            List of matching action names
        """
        query_lower = query.lower()
        matching_actions = []

        for action_name in self._actions:
            action = self.get_action(action_name)
            if action:
                if (
                    query_lower in action.name.lower()
                    or query_lower in action.description.lower()
                ):
                    matching_actions.append(action_name)

        return matching_actions

    def _register_builtin_actions(self) -> None:
        """Register built-in actions."""
        try:
            # Import and register built-in actions
            from .post_comment import PostComment
            from .label_pr import LabelPR
            from .create_or_update_issue import CreateOrUpdateIssue

            # Register basic actions
            self.register_action(PostComment)
            self.register_action(LabelPR)
            self.register_action(CreateOrUpdateIssue)

            logger.info("Built-in actions registered successfully")

        except ImportError as e:
            logger.warning(f"Some built-in actions could not be imported: {e}")
        except Exception as e:
            logger.error(f"Failed to register built-in actions: {e}")

    def validate_action_inputs(self, action_name: str, inputs: Dict) -> bool:
        """
        Validate inputs for a specific action.

        Args:
            action_name: Name of action
            inputs: Input data to validate

        Returns:
            True if inputs are valid
        """
        action = self.get_action(action_name)
        if not action:
            return False

        try:
            # TODO: Implement JSON schema validation
            return True
        except Exception as e:
            logger.error(f"Input validation failed for action '{action_name}': {e}")
            return False

    def get_registry_stats(self) -> Dict[str, int]:
        """
        Get registry statistics.

        Returns:
            Dictionary with registry statistics
        """
        return {
            "total_actions": len(self._actions),
            "instantiated_actions": len(self._instances),
            "github_actions": len(self.get_actions_by_platform("github")),
            "gitlab_actions": len(self.get_actions_by_platform("gitlab")),
        }
