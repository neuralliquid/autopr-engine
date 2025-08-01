"""
Dependency Injection container for the Quality Engine.
"""

from typing import Any, Dict, List, Type

from dependency_injector import containers, providers

from .handler_base import Handler
from .handlers.lint_handler import LintHandler
from .handlers.lint_issue import LintIssue

# Import registry at the module level to avoid circular imports
from .tools.registry import registry as tool_registry_instance


class HandlerContainer(containers.DeclarativeContainer):
    """Container for result handlers."""

    # Configure handlers
    lint_handler = providers.Factory(LintHandler)
    # Add more handlers as needed
    # security_handler = providers.Factory(SecurityHandler)
    # test_handler = providers.Factory(TestHandler)


class ToolRegistryContainer(containers.DeclarativeContainer):
    """Container for tool registry."""

    # Provide the tool registry as a singleton
    registry = providers.Singleton(lambda: tool_registry_instance)


class HandlerRegistryContainer(containers.DeclarativeContainer):
    """Container for handler registry."""

    # Dependencies
    handlers = providers.DependenciesContainer()

    # Create a handler mapping
    handler_mapping = providers.Dict(
        {
            LintIssue: providers.Callable(
                lambda handlers: handlers.lint_handler(), handlers=handlers
            )
            # Add more mappings as needed
        }
    )

    # Create the handler registry with the mapping
    from .handler_registry import HandlerRegistry

    registry = providers.Singleton(HandlerRegistry, handler_map=handler_mapping)


class QualityEngineContainer(containers.DeclarativeContainer):
    """Main container for the Quality Engine."""

    # Configuration
    config_path = providers.Configuration("config_path")
    config_path.from_env("QUALITY_ENGINE_CONFIG_PATH", "pyproject.toml")

    # Container for handlers
    handlers = providers.Container(HandlerContainer)

    # Container for tool registry
    tools = providers.Container(ToolRegistryContainer)

    # Container for handler registry
    handler_registry = providers.Container(HandlerRegistryContainer, handlers=handlers)

    # Import here to avoid circular dependencies
    from .config import load_config

    config = providers.Callable(load_config, config_path=config_path)

    # The main QualityEngine class
    from .engine import QualityEngine

    engine = providers.Singleton(
        QualityEngine,
        config_path=config_path,
        tool_registry=tools.registry,
        handler_registry=handler_registry.registry,
        config=config,
    )


# Create a global container instance
container = QualityEngineContainer()


# Helper function to get the engine instance
def get_engine():
    """Get the configured QualityEngine instance."""
    return container.engine()
