"""
Prototype Enhancement Package

Modular prototype enhancement system that provides platform-specific enhancements
for production readiness, testing, and security.

This package replaces the monolithic PrototypeEnhancer class with a modular architecture
while maintaining backward compatibility.
"""

from .enhancer import PrototypeEnhancer
from .platform_configs import PlatformRegistry, PlatformConfig
from .file_generators import FileGenerator
from .enhancement_strategies import (
    EnhancementStrategy,
    ReplitEnhancementStrategy,
    LovableEnhancementStrategy,
    BoltEnhancementStrategy,
    EnhancementStrategyFactory,
)

__version__ = "2.0.0"
__author__ = "AutoPR Team"

# Main exports for backward compatibility
__all__ = [
    "PrototypeEnhancer",
    "PlatformRegistry",
    "PlatformConfig",
    "FileGenerator",
    "EnhancementStrategy",
    "ReplitEnhancementStrategy",
    "LovableEnhancementStrategy",
    "BoltEnhancementStrategy",
    "EnhancementStrategyFactory",
]

# Package metadata
SUPPORTED_PLATFORMS = ["replit", "lovable", "bolt", "same", "emergent"]
ENHANCEMENT_TYPES = ["production_ready", "testing", "security"]


def get_version() -> str:
    """Get the package version."""
    return __version__


def get_supported_platforms() -> list:
    """Get list of supported platforms."""
    return SUPPORTED_PLATFORMS.copy()


def get_enhancement_types() -> list:
    """Get list of supported enhancement types."""
    return ENHANCEMENT_TYPES.copy()
