#!/usr/bin/env python3
"""
Template Models Module
=====================

Data models and structures for template discovery and browsing system.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List


@dataclass
class TemplateInfo:
    """Structured template information for discovery and comparison."""

    name: str
    description: str
    category: str
    platforms: List[str]
    file_path: str
    complexity: str = "medium"
    estimated_time: str = "unknown"
    use_cases: List[str] = field(default_factory=list)
    key_features: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    variants: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Ensure all fields are properly initialized
        if not isinstance(self.use_cases, list):
            self.use_cases = []
        if not isinstance(self.key_features, list):
            self.key_features = []
        if not isinstance(self.variables, dict):
            self.variables = {}
        if not isinstance(self.variants, dict):
            self.variants = {}
        if not isinstance(self.dependencies, list):
            self.dependencies = []


@dataclass
class PlatformRequirements:
    """Requirements for platform recommendation."""

    project_type: str
    team_size: str
    technical_expertise: str
    budget: str
    timeline: str
    features: List[str] = field(default_factory=list)

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if not isinstance(self.features, list):
            self.features = []


@dataclass
class PlatformRecommendation:
    """Platform recommendation with score and reasoning."""

    platform: str
    score: float
    reasoning: str
    confidence: float = 0.0

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        # Ensure score is within valid range
        self.score = max(0.0, min(10.0, self.score))
        self.confidence = max(0.0, min(1.0, self.confidence))


@dataclass
class TemplateCombination:
    """Recommended template combination for a use case."""

    platform: str
    main_template: str
    recommended_integrations: List[str] = field(default_factory=list)
    estimated_total_time: str = "unknown"
    complexity_score: int = 1

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if not isinstance(self.recommended_integrations, list):
            self.recommended_integrations = []
        # Ensure complexity score is within valid range
        self.complexity_score = max(1, min(5, self.complexity_score))


@dataclass
class TemplateReport:
    """Comprehensive template report structure."""

    summary: Dict[str, Any] = field(default_factory=dict)
    templates_by_category: Dict[str, List[Dict[str, Any]]] = field(default_factory=dict)
    platform_coverage: Dict[str, Dict[str, Any]] = field(default_factory=dict)
    recommendations: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        """Post-initialization processing."""
        if not isinstance(self.summary, dict):
            self.summary = {}
        if not isinstance(self.templates_by_category, dict):
            self.templates_by_category = {}
        if not isinstance(self.platform_coverage, dict):
            self.platform_coverage = {}
        if not isinstance(self.recommendations, dict):
            self.recommendations = {}
