"""
Base Generator Module

Provides the BaseGenerator class that all specialized generators inherit from.
"""

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

from autopr.actions.prototype_enhancement.platform_configs import PlatformConfig

T = TypeVar("T")


class BaseGenerator(ABC):
    """Base class for all file generators.

    Provides common functionality and interface for generating files.
    """

    def __init__(
        self, template_manager: "TemplateManager", platform_config: Optional[PlatformConfig] = None
    ):
        """Initialize the base generator.

        Args:
            template_manager: The template manager instance to use for rendering templates
            platform_config: Optional platform configuration
        """
        self.template_manager = template_manager
        self.platform_config = platform_config

    @abstractmethod
    def generate(self, output_dir: str, **kwargs) -> List[str]:
        """Generate files in the specified output directory.

        Args:
            output_dir: The directory to generate files in
            **kwargs: Additional arguments specific to the generator

        Returns:
            List of paths to generated files
        """
        pass

    def _write_file(self, file_path: str, content: str) -> None:
        """Write content to a file, creating parent directories if needed.

        Args:
            file_path: Path to the file to write
            content: Content to write to the file
        """
        path = Path(file_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(content, encoding="utf-8")

    def _render_template(
        self,
        template_key: str,
        variables: Optional[Dict[str, Any]] = None,
        variants: Optional[List[str]] = None,
    ) -> Optional[str]:
        """Render a template using the template manager.

        Args:
            template_key: Key identifying the template
            variables: Variables to pass to the template
            variants: List of template variants to apply
        Returns:
            Rendered template content, or None if template not found
        """
        return self.template_manager.render(template_key, variables, variants)

    def _get_platform_variables(self) -> Dict[str, Any]:
        """Get platform-specific variables for template rendering.

        Returns:
            Dictionary of platform variables
        """
        if not self.platform_config:
            return {}

        return {
            "platform": self.platform_config.name,
            "platform_config": self.platform_config.dict(),
            "platform_vars": self.platform_config.variables or {},
        }
