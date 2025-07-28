"""
Artifacts Module

This module contains data models for various artifacts used in the AutoPR system.
"""

from dataclasses import dataclass
from enum import Enum
from typing import Any, Dict, List, Optional


class EnhancementType(str, Enum):
    """Types of enhancements that can be applied to a prototype."""

    PRODUCTION = "production"
    TESTING = "testing"
    SECURITY = "security"


@dataclass
class PrototypeEnhancerInputs:
    """Input model for the PrototypeEnhancer."""

    platform: str
    enhancement_type: "EnhancementType"
    project_path: str
    config: Optional[Dict[str, Any]] = None
    dry_run: bool = False


@dataclass
class PrototypeEnhancerOutputs:
    """Output model for the PrototypeEnhancer."""

    success: bool
    message: str
    generated_files: List[str]
    modified_files: List[str]
    next_steps: List[str]
    metadata: Optional[Dict[str, Any]] = None
