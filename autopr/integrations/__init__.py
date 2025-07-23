"""
AutoPR Engine Integrations
External service integrations for communication and project management
"""

# Import integration classes
from .axolo_integration import AxoloIntegration

# Integration registry
AVAILABLE_INTEGRATIONS = {
    "axolo": AxoloIntegration,
}

def get_integration(integration_name: str):
    """Get an integration class by name"""
    return AVAILABLE_INTEGRATIONS.get(integration_name)

def list_integrations():
    """List all available integrations"""
    return list(AVAILABLE_INTEGRATIONS.keys())

__all__ = [
    "AxoloIntegration",
    "get_integration",
    "list_integrations",
    "AVAILABLE_INTEGRATIONS"
] 