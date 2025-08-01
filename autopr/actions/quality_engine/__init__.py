"""
Quality Engine package.

A modular system for running code quality tools and handling their results.
"""

# Version information
__version__ = "1.0.0"

from .di import container, get_engine

# Import main classes for easy access from the package root
from .engine import QualityEngine, QualityInputs, QualityMode, QualityOutputs
from .handler_base import Handler
from .tools.tool_base import Tool

__all__ = [
    "QualityEngine",
    "QualityInputs",
    "QualityOutputs",
    "QualityMode",
    "Handler",
    "Tool",
    "container",
    "get_engine",
]
