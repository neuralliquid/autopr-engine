"""
Platform Detection Package

Modular platform detection system for AutoPR.
"""

from .config import PlatformConfig
from .detector import (
    EnhancedPlatformDetector,
    EnhancedPlatformDetectorInputs,
    EnhancedPlatformDetectorOutputs,
)
from .file_analyzer import FileAnalyzer
from .scoring import PlatformScoringEngine

__all__ = [
    "EnhancedPlatformDetector",
    "EnhancedPlatformDetectorInputs",
    "EnhancedPlatformDetectorOutputs",
    "PlatformConfig",
    "FileAnalyzer",
    "PlatformScoringEngine",
]
