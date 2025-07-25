"""
AutoPR Engine Integrations
External service integrations for communication and project management
"""

from typing import Optional, Type, List, Any
from .base import Integration

# Import integration classes with error handling
AxoloIntegration: Optional[Type[Any]] = None
_axolo_available = False
try:
    from .axolo_integration import AxoloIntegration

    _axolo_available = True
except ImportError:
    pass

# Registry of available integrations
AVAILABLE_INTEGRATIONS = {}
if _axolo_available and AxoloIntegration is not None:
    AVAILABLE_INTEGRATIONS["axolo"] = AxoloIntegration


def get_integration(integration_name: str) -> Optional[Type[Integration]]:
    """Get an integration class by name"""
    return AVAILABLE_INTEGRATIONS.get(integration_name)


def list_integrations() -> List[str]:
    """List all available integrations"""
    return list(AVAILABLE_INTEGRATIONS.keys())


__all__ = [
    "AxoloIntegration",
    "get_integration",
    "list_integrations",
    "AVAILABLE_INTEGRATIONS",
]
