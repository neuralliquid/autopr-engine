"""
Configuration and template loading utilities for the AutoPR prototype enhancement system.

This module provides utilities to load externalized configuration files and templates
from the organized configs/ and templates/ directories.
"""

import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional
from functools import lru_cache
import logging

logger = logging.getLogger(__name__)

# Base paths for configurations and templates
CONFIG_BASE_PATH = Path(__file__).parent.parent.parent.parent / "configs"
TEMPLATE_BASE_PATH = Path(__file__).parent.parent.parent.parent / "templates"


class ConfigLoader:
    """Utility class for loading configuration files and templates."""
    
    @staticmethod
    @lru_cache(maxsize=32)
    def load_platform_config(platform_name: str) -> Dict[str, Any]:
        """Load platform configuration from JSON file.
        
        Args:
            platform_name: Name of the platform (e.g., 'replit', 'lovable', 'bolt')
            
        Returns:
            Dictionary containing platform configuration
            
        Raises:
            FileNotFoundError: If platform config file doesn't exist
            json.JSONDecodeError: If config file is invalid JSON
        """
        config_path = CONFIG_BASE_PATH / "platforms" / f"{platform_name}.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Platform config not found: {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"Loaded platform config for {platform_name}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in platform config {config_path}: {e}")
            raise
    
    @staticmethod
    @lru_cache(maxsize=16)
    def load_package_dependencies(category: str) -> Dict[str, Any]:
        """Load package dependencies configuration from JSON file.
        
        Args:
            category: Package category (e.g., 'security', 'testing', 'performance')
            
        Returns:
            Dictionary containing package dependencies
        """
        config_path = CONFIG_BASE_PATH / "packages" / f"{category}.json"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Package config not found: {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            logger.debug(f"Loaded package dependencies for {category}")
            return config
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in package config {config_path}: {e}")
            raise
    
    @staticmethod
    @lru_cache(maxsize=64)
    def load_template(category: str, template_name: str) -> str:
        """Load template file content.
        
        Args:
            category: Template category (e.g., 'docker', 'typescript', 'build')
            template_name: Name of the template file
            
        Returns:
            String content of the template file
        """
        template_path = TEMPLATE_BASE_PATH / category / template_name
        
        if not template_path.exists():
            raise FileNotFoundError(f"Template not found: {template_path}")
            
        try:
            with open(template_path, 'r', encoding='utf-8') as f:
                content = f.read()
            logger.debug(f"Loaded template {category}/{template_name}")
            return content
        except Exception as e:
            logger.error(f"Error loading template {template_path}: {e}")
            raise
    
    @staticmethod
    @lru_cache(maxsize=32)
    def load_workflow_config(workflow_name: str) -> Dict[str, Any]:
        """Load workflow configuration from YAML file.
        
        Args:
            workflow_name: Name of the workflow (without .yaml extension)
            
        Returns:
            Dictionary containing workflow configuration
        """
        config_path = CONFIG_BASE_PATH / "workflows" / f"{workflow_name}.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Workflow config not found: {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.debug(f"Loaded workflow config for {workflow_name}")
            return config or {}
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in workflow config {config_path}: {e}")
            raise
    
    @staticmethod
    @lru_cache(maxsize=8)
    def load_triggers_config() -> Dict[str, Any]:
        """Load main triggers configuration.
        
        Returns:
            Dictionary containing triggers configuration
        """
        config_path = CONFIG_BASE_PATH / "triggers" / "main-triggers.yaml"
        
        if not config_path.exists():
            raise FileNotFoundError(f"Triggers config not found: {config_path}")
            
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = yaml.safe_load(f)
            logger.debug("Loaded triggers configuration")
            return config or {}
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in triggers config {config_path}: {e}")
            raise
    
    @staticmethod
    def get_available_platforms() -> list[str]:
        """Get list of available platform configurations.
        
        Returns:
            List of platform names
        """
        platforms_dir = CONFIG_BASE_PATH / "platforms"
        if not platforms_dir.exists():
            return []
            
        platforms = []
        for config_file in platforms_dir.glob("*.json"):
            platforms.append(config_file.stem)
        
        return sorted(platforms)
    
    @staticmethod
    def get_available_package_categories() -> list[str]:
        """Get list of available package categories.
        
        Returns:
            List of package category names
        """
        packages_dir = CONFIG_BASE_PATH / "packages"
        if not packages_dir.exists():
            return []
            
        categories = []
        for config_file in packages_dir.glob("*.json"):
            categories.append(config_file.stem)
        
        return sorted(categories)
    
    @staticmethod
    def get_available_templates(category: Optional[str] = None) -> Dict[str, list[str]]:
        """Get list of available templates, optionally filtered by category.
        
        Args:
            category: Optional category to filter by
            
        Returns:
            Dictionary mapping category names to lists of template names
        """
        if not TEMPLATE_BASE_PATH.exists():
            return {}
            
        templates = {}
        
        if category:
            # Get templates for specific category
            category_dir = TEMPLATE_BASE_PATH / category
            if category_dir.exists() and category_dir.is_dir():
                template_files = []
                for template_file in category_dir.iterdir():
                    if template_file.is_file():
                        template_files.append(template_file.name)
                templates[category] = sorted(template_files)
        else:
            # Get all templates organized by category
            for category_dir in TEMPLATE_BASE_PATH.iterdir():
                if category_dir.is_dir():
                    template_files = []
                    for template_file in category_dir.iterdir():
                        if template_file.is_file():
                            template_files.append(template_file.name)
                    templates[category_dir.name] = sorted(template_files)
        
        return templates


# Convenience functions for backward compatibility
def load_platform_config(platform_name: str) -> Dict[str, Any]:
    """Load platform configuration (convenience function)."""
    return ConfigLoader.load_platform_config(platform_name)


def load_package_dependencies(category: str) -> Dict[str, Any]:
    """Load package dependencies (convenience function)."""
    return ConfigLoader.load_package_dependencies(category)


def load_template(category: str, template_name: str) -> str:
    """Load template content (convenience function)."""
    return ConfigLoader.load_template(category, template_name)


def load_workflow_config(workflow_name: str) -> Dict[str, Any]:
    """Load workflow configuration (convenience function)."""
    return ConfigLoader.load_workflow_config(workflow_name)
