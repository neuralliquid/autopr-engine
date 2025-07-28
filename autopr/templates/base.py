"""
Base classes for template providers.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional, Union


@dataclass
class TemplateMetadata:
    """Metadata for a template."""

    template_id: str
    title: str
    description: str
    version: str
    author: str
    tags: List[str]
    category: str
    platforms: List[str]
    variables: Dict[str, Any]
    variants: Dict[str, Dict[str, Any]] = None
    documentation: str = ""
    discovery: Dict[str, Any] = None


class TemplateProvider(ABC):
    """Base class for template providers."""

    @abstractmethod
    def get_template(self, template_id: str) -> Optional[TemplateMetadata]:
        """Get template metadata by ID."""
        pass

    @abstractmethod
    def get_all_templates(self) -> List[TemplateMetadata]:
        """Get all available templates."""
        pass

    @abstractmethod
    def search_templates(self, query: str) -> List[TemplateMetadata]:
        """Search for templates matching the query."""
        pass

    @abstractmethod
    def render_template(
        self, template_id: str, context: Dict[str, Any], variant: Optional[str] = None
    ) -> str:
        """Render a template with the given context and optional variant."""
        pass

    @abstractmethod
    def render_to_file(
        self,
        template_id: str,
        output_path: Union[str, Path],
        context: Dict[str, Any],
        variant: Optional[str] = None,
        **kwargs,
    ) -> None:
        """Render a template to a file."""
        pass
