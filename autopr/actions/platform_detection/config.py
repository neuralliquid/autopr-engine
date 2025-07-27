"""
Platform Configuration Module

Loads and manages platform configurations from JSON files using the new schema.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, ClassVar, Dict, List, Optional, Type, TypeVar

from .schema import PlatformConfig, PlatformSource, PlatformStatus, PlatformType

# Set up logging
logger = logging.getLogger(__name__)

T = TypeVar("T", bound="PlatformConfigManager")


class PlatformConfigManager:
    """Manages platform configurations with the new schema."""

    _instance: ClassVar[Optional["PlatformConfigManager"]] = None
    _configs_loaded: bool = False
    _platforms: Dict[str, PlatformConfig] = {}
    _platforms_by_category: Dict[str, List[str]] = {}
    _platforms_by_type: Dict[PlatformType, List[str]] = {}

    # Default configuration directories
    _BASE_CONFIG_DIR = Path(__file__).parent / "configs"
    _CATEGORY_FILES = {
        "core": "core_platforms.json",
        "ai": "ai_platforms.json",
        "cloud": "cloud_platforms.json",
    }

    def __new__(cls: Type[T]) -> T:
        """Singleton pattern implementation."""
        if cls._instance is None:
            cls._instance = super(PlatformConfigManager, cls).__new__(cls)
            cls._instance._initialize()
        return cls._instance

    def _initialize(self) -> None:
        """Initialize the configuration manager."""
        self._platforms = {}
        self._platforms_by_category = {}
        self._platforms_by_type = {}
        self._load_config_files()
        self._configs_loaded = True

    @classmethod
    def _load_platform_file(cls, file_path: Path) -> Optional[PlatformConfig]:
        """
        Load a single platform configuration file.

        Args:
            file_path: Path to the platform configuration file

        Returns:
            PlatformConfig instance if successful, None otherwise
        """
        try:
            if not file_path.exists():
                logger.warning(f"Platform config file not found: {file_path}")
                return None

            platform_id = file_path.stem
            return PlatformConfig.from_file(file_path)

        except (json.JSONDecodeError, IOError, ValueError) as e:
            logger.error(f"Error loading platform config {file_path}: {e}", exc_info=True)
            return None

    def _load_platforms_from_category(self, category: str) -> Dict[str, PlatformConfig]:
        """
        Load all platforms from a category directory.

        Args:
            category: Category name (core, ai, cloud, etc.)

        Returns:
            Dictionary of platform_id -> PlatformConfig
        """
        category_dir = self._BASE_CONFIG_DIR / category
        if not category_dir.exists() or not category_dir.is_dir():
            logger.warning("Category directory not found: %s", category_dir)
            return {}

        platforms = {}

        # Load all JSON files in the category directory
        for config_file in category_dir.glob("*.json"):
            if config_file.name in self._CATEGORY_FILES.values():
                # Skip category index files
                continue

            platform = self._load_platform_file(config_file)
            if platform:
                platforms[platform.id] = platform

                # Update indexes
                self._platforms_by_category.setdefault(category, []).append(platform.id)
                self._platforms_by_type.setdefault(platform.type, []).append(platform.id)

        return platforms

    def _load_config_files(self) -> None:
        """
        Load all platform configurations from the config directory.

        Raises:
            Exception: If an error occurs while loading configurations
        """
        # Ensure config directory exists
        self._BASE_CONFIG_DIR.mkdir(parents=True, exist_ok=True)

        # Load each category
        for category in self._CATEGORY_FILES.keys():
            platforms = self._load_platforms_from_category(category)
            self._platforms.update(platforms)

        logger.info("Loaded %d platform configurations", len(self._platforms))

        # Load category index files for backward compatibility
        self._load_category_index_files()

    def _load_category_index_files(self) -> None:
        """Load category index files for backward compatibility."""
        for category, filename in self._CATEGORY_FILES.items():
            category_file = self._BASE_CONFIG_DIR / filename
            if not category_file.exists():
                continue

            try:
                with open(category_file, "r", encoding="utf-8") as f:
                    data = json.load(f)

                if isinstance(data, dict):
                    # Old format: {platform_id: path}
                    for platform_id, path in data.items():
                        if platform_id not in self._platforms:
                            logger.warning(f"Referenced platform not found: {platform_id}")

            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading category file {category_file}: {e}")

    def get_platform(self, platform_id: str) -> Optional[PlatformConfig]:
        """
        Get a platform configuration by ID.

        Args:
            platform_id: The platform ID to look up

        Returns:
            PlatformConfig if found, None otherwise
        """
        if not self._configs_loaded:
            self._load_config_files()
        return self._platforms.get(platform_id)

    def get_platforms_by_category(self, category: str) -> Dict[str, PlatformConfig]:
        """
        Get all platforms in a category.

        Args:
            category: The category name (core, ai, cloud, etc.)

        Returns:
            Dictionary of platform_id -> PlatformConfig
        """
        if not self._configs_loaded:
            self._load_config_files()

        platform_ids = self._platforms_by_category.get(category, [])
        return {pid: self._platforms[pid] for pid in platform_ids if pid in self._platforms}

    def get_platforms_by_type(self, platform_type: PlatformType) -> Dict[str, PlatformConfig]:
        """
        Get all platforms of a specific type.

        Args:
            platform_type: The platform type to filter by

        Returns:
            Dictionary of platform_id -> PlatformConfig
        """
        if not self._configs_loaded:
            self._load_config_files()

        platform_ids = self._platforms_by_type.get(platform_type, [])
        return {pid: self._platforms[pid] for pid in platform_ids if pid in self._platforms}

    def get_all_platforms(self) -> Dict[str, PlatformConfig]:
        """
        Get all platform configurations.

        Returns:
            Dictionary of platform_id -> PlatformConfig
        """
        if not self._configs_loaded:
            self._load_config_files()
        return self._platforms.copy()

    def get_active_platforms(self) -> Dict[str, PlatformConfig]:
        """
        Get all active platform configurations.

        Returns:
            Dictionary of platform_id -> PlatformConfig
        """
        if not self._configs_loaded:
            self._load_config_files()
        return {pid: p for pid, p in self._platforms.items() if p.is_active}

    def find_platforms(self, **filters) -> Dict[str, PlatformConfig]:
        """
        Find platforms matching the given filters.

        Args:
            **filters: Field names and values to filter by

        Returns:
            Dictionary of platform_id -> PlatformConfig that match all filters
        """
        if not self._configs_loaded:
            self._load_config_files()

        result = {}
        for platform_id, platform in self._platforms.items():
            match = True
            for field, value in filters.items():
                if not hasattr(platform, field):
                    match = False
                    break

                if getattr(platform, field) != value:
                    match = False
                    break

            if match:
                result[platform_id] = platform

        return result

    def get_platform_categories(self) -> Dict[str, List[str]]:
        """
        Get platform categories with their associated platform IDs.

        Returns:
            Dictionary mapping category names to lists of platform IDs
        """
        if not self._configs_loaded:
            self._load_config_files()

        return {
            category: platform_ids.copy()
            for category, platform_ids in self._platforms_by_category.items()
        }


# For backward compatibility
PlatformConfig = PlatformConfigManager
