"""
YAML-based HTML Template Loader for structured HTML templates.

This module provides functionality to load and render HTML templates
that follow the YAML template format structure, similar to the existing
YAML templates but for HTML generation.
"""

import yaml
from pathlib import Path
from typing import Dict, Any, Optional, List, Match
import re


class YAMLHTMLTemplateLoader:
    """Loads and renders HTML templates from YAML format files."""

    def __init__(self, templates_path: Optional[Path] = None):
        """Initialize the template loader with templates directory path."""
        if templates_path is None:
            templates_path = Path(__file__).parent.parent.parent / "html"
        self.templates_path = Path(templates_path)

    def load_template(self, template_name: str) -> Dict[str, Any]:
        """Load a YAML HTML template by name."""
        template_file = self.templates_path / f"{template_name}.yml"

        if not template_file.exists():
            # Fallback to .yaml extension
            template_file = self.templates_path / f"{template_name}.yaml"

        if not template_file.exists():
            raise FileNotFoundError(
                f"Template '{template_name}' not found in {self.templates_path}"
            )

        try:
            with open(template_file, "r", encoding="utf-8") as f:
                template_data: Dict[str, Any] = yaml.safe_load(f) or {}

            return template_data
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML template '{template_name}': {e}")

    def render_template(self, template_name: str, **variables: Any) -> str:
        """Render a YAML HTML template with the provided variables."""
        template_data = self.load_template(template_name)

        # Get the HTML content from template_content field
        html_content = template_data.get("template_content", "")

        if not html_content:
            raise ValueError(f"Template '{template_name}' has no 'template_content' field")

        # Merge template variables with provided variables
        template_vars = template_data.get("variables", {})
        render_context = self._prepare_render_context(template_data, template_vars, variables)

        # Render the template with variables
        rendered_html = self._render_template_content(html_content, render_context)

        return rendered_html

    def _prepare_render_context(
        self,
        template_data: Dict[str, Any],
        template_vars: Dict[str, Any],
        provided_vars: Dict[str, Any],
    ) -> Dict[str, Any]:
        """Prepare the rendering context with defaults and provided variables."""
        context = {}

        # Add template metadata to context
        context.update(
            {
                "template_name": template_data.get("name", ""),
                "template_version": template_data.get("version", ""),
                "template_author": template_data.get("author", ""),
            }
        )

        # Add styling information if available
        if "styling" in template_data:
            context["styling"] = template_data["styling"]

        # Add features if available
        if "features" in template_data:
            context["features"] = template_data["features"]

        # Process template variables with defaults
        for var_name, var_config in template_vars.items():
            if var_name in provided_vars:
                context[var_name] = provided_vars[var_name]
            else:
                # Use default value if provided and variable is not required
                default_value = var_config.get("default", "")
                if var_config.get("required", False) and var_name not in provided_vars:
                    raise ValueError(f"Required variable '{var_name}' not provided for template")
                context[var_name] = default_value

        # Add any additional provided variables
        for var_name, value in provided_vars.items():
            if var_name not in context:
                context[var_name] = value

        return context

    def _render_template_content(self, content: str, context: Dict[str, Any]) -> str:
        """Render template content with variable substitution."""
        rendered = content

        # Handle simple variable substitution {{ variable_name }}
        def replace_variable(match: Any) -> str:
            var_path = match.group(1).strip()
            return str(self._get_nested_value(context, var_path))

        rendered = re.sub(r"\{\{\s*([^}]+)\s*\}\}", replace_variable, rendered)

        # Handle conditional blocks {% if condition %}...{% endif %}
        rendered = self._process_conditionals(rendered, context)

        # Handle filters like {{ variable | default: "value" }}
        rendered = self._process_filters(rendered, context)

        return rendered

    def _get_nested_value(self, data: Dict[str, Any], path: str) -> Any:
        """Get a nested value from a dictionary using dot notation."""
        keys = path.split(".")
        value = data

        try:
            for key in keys:
                if isinstance(value, dict):
                    value = value.get(key, "")
            # Successfully processed all keys
            return str(value) if value is not None else ""
        except (KeyError, TypeError):
            return ""

    def _process_conditionals(self, content: str, context: Dict[str, Any]) -> str:
        """Process conditional blocks in the template."""
        # Simple conditional processing for {% if variable %}...{% endif %}
        pattern = r"\{%\s*if\s+([^%]+)\s*%\}(.*?)\{%\s*endif\s*%\}"

        def replace_conditional(match: Match[str]) -> str:
            condition = match.group(1).strip()
            block_content = match.group(2) or ""

            # Evaluate condition (simple variable existence check)
            if condition in context and context[condition]:
                return block_content
            else:
                return ""

        return re.sub(pattern, replace_conditional, content, flags=re.DOTALL)

    def _process_filters(self, content: str, context: Dict[str, Any]) -> str:
        """Process template filters like {{ variable | default: "value" }}."""
        # Handle default filter: {{ variable | default: "value" }}
        pattern = r"\{\{\s*([^|]+)\s*\|\s*default:\s*([^}]+)\s*\}\}"

        def replace_filter(match: Match[str]) -> str:
            var_name = (match.group(1) or "").strip()
            default_value = (match.group(2) or "").strip().strip("\"'")

            value = self._get_nested_value(context, var_name)
            return str(value) if value else str(default_value)

        return re.sub(pattern, replace_filter, content)

    def get_template_info(self, template_name: str) -> Dict[str, Any]:
        """Get metadata information about a template."""
        template_data = self.load_template(template_name)

        return {
            "name": template_data.get("name", ""),
            "category": template_data.get("category", ""),
            "description": template_data.get("description", ""),
            "version": template_data.get("version", ""),
            "author": template_data.get("author", ""),
            "tags": template_data.get("tags", []),
            "template_info": template_data.get("template_info", {}),
            "variables": template_data.get("variables", {}),
            "features": template_data.get("features", []),
            "styling": template_data.get("styling", {}),
        }

    def list_available_templates(self) -> List[str]:
        """List all available YAML HTML templates."""
        templates = []

        for template_file in self.templates_path.glob("*.yml"):
            templates.append(template_file.stem)

        for template_file in self.templates_path.glob("*.yaml"):
            if template_file.stem not in templates:  # Avoid duplicates
                templates.append(template_file.stem)

        return sorted(templates)
