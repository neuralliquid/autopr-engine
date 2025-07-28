"""
Platform Configuration Schema

Defines the structure and validation for platform configuration files.

This module contains schemas for:
1. PlatformIndex: For platform collection files (e.g., cloud_platforms.json)
2. PlatformConfig: For individual platform configuration files (e.g., cloud/vercel.json)
"""

from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Literal, Optional, TypedDict, Union


class PlatformType(str, Enum):
    """Types of platforms we support."""

    IDE = "ide"
    CLOUD = "cloud"
    VCS = "vcs"
    CI_CD = "ci_cd"
    DEPLOYMENT = "deployment"
    MONITORING = "monitoring"
    SECURITY = "security"
    GENERAL = "general"


class PlatformSource(str, Enum):
    """Source of the platform configuration."""

    OFFICIAL = "official"
    COMMUNITY = "community"
    THIRD_PARTY = "third_party"


class PlatformStatus(str, Enum):
    """Status of the platform support."""

    ACTIVE = "active"
    BETA = "beta"
    DEPRECATED = "deprecated"
    EXPERIMENTAL = "experimental"


class DetectionRules(TypedDict, total=False):
    """Configuration for platform detection rules."""

    files: List[str]
    dependencies: List[str]
    folder_patterns: List[str]
    commit_patterns: List[str]
    content_patterns: List[str]
    package_scripts: List[str]
    confidence_weights: Dict[str, float]


class PlatformReference(TypedDict):
    """Minimal platform reference used in index files."""

    id: str
    name: str
    category: str
    description: str
    config_file: str
    is_active: bool
    priority: int


class PlatformIndex(TypedDict):
    """Schema for platform index files (e.g., cloud_platforms.json)."""

    version: str
    last_updated: str
    description: str
    platforms: List[PlatformReference]
    metadata: Dict[str, Any]


class ProjectConfig(TypedDict, total=False):
    """Configuration for project setup and deployment."""

    primary_language: str
    framework: str
    deployment_targets: List[str]
    common_files: List[str]
    features: List[str]
    configuration_files: List[str]


@dataclass
class PlatformConfig:
    """
    Platform configuration container with validation.

    This class represents the complete configuration for a platform that AutoPR can interact with.
    It includes metadata, detection rules, and project configuration.
    """

    # Required fields (must be in root)
    id: str
    name: str
    category: str
    description: str
    priority: str

    # Display information
    display_name: str = ""
    version: str = "1.0.0"
    last_updated: str = field(default_factory=lambda: datetime.utcnow().isoformat())

    # Status
    status: PlatformStatus = PlatformStatus.ACTIVE
    is_active: bool = True
    is_beta: bool = False
    is_deprecated: bool = False
    deprecation_message: Optional[str] = None

    # Categorization
    type: PlatformType = PlatformType.GENERAL
    subcategory: str = ""
    tags: List[str] = field(default_factory=list)

    # Integration
    supported_languages: List[str] = field(default_factory=list)
    supported_frameworks: List[str] = field(default_factory=list)
    integrations: List[str] = field(default_factory=list)

    # Documentation
    documentation_url: str = ""
    setup_guide: str = ""
    troubleshooting_guide: str = ""

    # Ownership
    maintainer: str = ""
    source: PlatformSource = PlatformSource.COMMUNITY
    license: str = "MIT"

    # Technical metadata
    min_autopr_version: str = "0.1.0"
    dependencies: Dict[str, str] = field(default_factory=dict)
    compatibility: Dict[str, Any] = field(default_factory=dict)

    # Nested configurations
    detection: DetectionRules = field(default_factory=lambda: {})
    project_config: ProjectConfig = field(default_factory=lambda: {})
    metadata: Dict[str, Any] = field(default_factory=dict)

    # Class variables
    _required_fields: ClassVar[list] = ["id", "name", "category", "description"]

    @classmethod
    def from_dict(cls, platform_id: str, data: dict) -> "PlatformConfig":
        """
        Create a PlatformConfig from a dictionary, with validation.

        Args:
            platform_id: The unique identifier for the platform
            data: Dictionary containing platform configuration

        Returns:
            A validated PlatformConfig instance

        Raises:
            ValueError: If required fields are missing or invalid
        """
        # Validate required fields
        missing_fields = [f for f in cls._required_fields if f not in data]
        if missing_fields:
            raise ValueError(f"Missing required fields: {', '.join(missing_fields)}")

        # Handle enums and special types
        status = PlatformStatus(data.get("status", "active")) if "status" in data else None
        platform_type = PlatformType(data["type"]) if "type" in data else None
        source = PlatformSource(data["source"]) if "source" in data else None

        # Create and return the config
        return cls(
            id=platform_id,
            name=data["name"],
            category=data["category"],
            description=data["description"],
            priority=data["priority"],
            # Display information
            display_name=data.get("display_name", data["name"]),
            version=data.get("version", "1.0.0"),
            last_updated=data.get("last_updated", datetime.utcnow().isoformat()),
            # Status
            status=status
            or (
                PlatformStatus.BETA
                if data.get("is_beta", False)
                else (
                    PlatformStatus.DEPRECATED
                    if data.get("is_deprecated", False)
                    else PlatformStatus.ACTIVE
                )
            ),
            is_active=data.get("is_active", True),
            is_beta=data.get("is_beta", False),
            is_deprecated=data.get("is_deprecated", False),
            deprecation_message=data.get("deprecation_message"),
            # Categorization
            type=platform_type or PlatformType.GENERAL,
            subcategory=data.get("subcategory", ""),
            tags=data.get("tags", []),
            # Integration
            supported_languages=data.get("supported_languages", []),
            supported_frameworks=data.get("supported_frameworks", []),
            integrations=data.get("integrations", []),
            # Documentation
            documentation_url=data.get("documentation_url", ""),
            setup_guide=data.get("setup_guide", ""),
            troubleshooting_guide=data.get("troubleshooting_guide", ""),
            # Ownership
            maintainer=data.get("maintainer", ""),
            source=source or PlatformSource.COMMUNITY,
            license=data.get("license", "MIT"),
            # Technical metadata
            min_autopr_version=data.get("min_autopr_version", "0.1.0"),
            dependencies=data.get("dependencies", {}),
            compatibility=data.get("compatibility", {}),
            # Nested configurations
            detection=data.get("detection", {}),
            project_config=data.get("project_config", {}),
            metadata=data.get("metadata", {}),
        )

    @classmethod
    def from_file(cls, file_path: Path) -> "PlatformConfig":
        """Load a platform configuration from a JSON file."""
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Use the filename (without .json) as the ID if not specified
            platform_id = data.get("id", file_path.stem)
            return cls.from_dict(platform_id, data)

        except (json.JSONDecodeError, IOError) as e:
            raise ValueError(f"Error loading platform config {file_path}: {e}")

    def to_dict(self) -> dict:
        """Convert the configuration to a dictionary."""
        result = {
            "id": self.id,
            "name": self.name,
            "category": self.category,
            "description": self.description,
            "is_active": self.is_active,
            "priority": self.priority,
        }

        # Add nested sections if they're not empty
        if self.detection:
            result["detection"] = self.detection
        if self.project_config:
            result["project_config"] = self.project_config
        if self.metadata:
            result["metadata"] = self.metadata

        return result

    def to_json(self, indent: int = 2) -> str:
        """Convert the configuration to a JSON string."""
        return json.dumps(self.to_dict(), indent=indent, ensure_ascii=False)
