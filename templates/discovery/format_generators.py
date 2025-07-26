#!/usr/bin/env python3
"""
Format Generators Module
=======================

Generates documentation in different output formats (Markdown, HTML, JSON).
Provides specialized generators for different types of documentation content.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime
from dataclasses import dataclass

from .template_loader import TemplateLoader
from .content_analyzer import TemplateAnalysis, ContentAnalyzer


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation."""
    output_format: str = "markdown"  # markdown, html, json
    include_examples: bool = True
    include_code_snippets: bool = True
    include_troubleshooting: bool = True
    include_best_practices: bool = True
    generate_index: bool = True
    custom_css: Optional[str] = None


class BaseFormatGenerator:
    """Base class for format generators."""
    
    def __init__(self, config: DocumentationConfig, template_loader: TemplateLoader) -> None:
        """Initialize the format generator."""
        self.config = config
        self.template_loader = template_loader
    
    def generate_content(self, template_name: str, **kwargs: Any) -> str:
        """Generate content using a template."""
        # Add common variables
        kwargs.setdefault('generation_date', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        kwargs.setdefault('config', self.config)
        
        return self.template_loader.render_template(template_name, **kwargs)


class MarkdownGenerator(BaseFormatGenerator):
    """Generates Markdown documentation."""
    
    def generate_platform_guide(self, analysis: TemplateAnalysis) -> str:
        """Generate platform guide in Markdown format."""
        return self.generate_content(
            'platform_guide',
            platform_name=analysis.name.replace('_', ' ').title(),
            platform_info=analysis.platform_info,
            key_features=analysis.key_features,
            variables=analysis.variables,
            development_approach=analysis.metadata.get('development_approach', {}),
            best_practices=analysis.metadata.get('best_practices', {}),
            troubleshooting=analysis.troubleshooting,
            pricing=analysis.platform_info.get('pricing', {})
        )
    
    def generate_use_case_guide(self, analysis: TemplateAnalysis) -> str:
        """Generate use case guide in Markdown format."""
        return self.generate_content(
            'use_case_guide',
            use_case_name=analysis.name.replace('_', ' ').title(),
            use_case_info=analysis.use_case_info,
            key_features=analysis.key_features,
            implementation_steps=analysis.use_case_info.get('implementation_steps', []),
            configuration_options=analysis.variables,
            recommended_platforms=analysis.metadata.get('recommended_platforms', []),
            examples=analysis.examples,
            best_practices=analysis.best_practices,
            common_pitfalls=analysis.metadata.get('common_pitfalls', [])
        )
    
    def generate_integration_guide(self, analysis: TemplateAnalysis) -> str:
        """Generate integration guide in Markdown format."""
        return self.generate_content(
            'integration_guide',
            integration_name=analysis.name.replace('_', ' ').title(),
            integration_info=analysis.integration_info,
            key_features=analysis.key_features,
            setup_steps=analysis.integration_info.get('setup_steps', []),
            configuration_options=analysis.variables,
            examples=analysis.examples,
            troubleshooting=analysis.troubleshooting
        )
    
    def generate_main_index(self, analyses: List[TemplateAnalysis]) -> str:
        """Generate main documentation index."""
        # Group analyses by category
        platforms = [a for a in analyses if a.category == 'platform']
        use_cases = [a for a in analyses if a.category == 'use_case']
        integrations = [a for a in analyses if a.category == 'integration']
        
        content = f"""# Template Documentation

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

Welcome to the comprehensive template documentation. This guide covers all available templates for no-code platform development.

## Quick Start

1. **Choose Your Platform**: Browse the [Platform Guides](#platform-guides) to find the right development environment
2. **Select a Use Case**: Explore [Use Case Templates](#use-case-templates) for specific application types
3. **Add Integrations**: Enhance your application with [Integration Templates](#integration-templates)

## Platform Guides

Build applications on these no-code platforms:

"""
        
        for platform in sorted(platforms, key=lambda x: x.name):
            platform_name = platform.name.replace('_', ' ').title()
            description = platform.platform_info.get('description', 'No description available')
            content += f"- **[{platform_name}](platforms/{platform.name}.md)**: {description}\n"
        
        content += "\n## Use Case Templates\n\nPre-built templates for common application types:\n\n"
        
        for use_case in sorted(use_cases, key=lambda x: x.name):
            use_case_name = use_case.name.replace('_', ' ').title()
            description = use_case.use_case_info.get('description', 'No description available')
            content += f"- **[{use_case_name}](use-cases/{use_case.name}.md)**: {description}\n"
        
        content += "\n## Integration Templates\n\nAdd functionality with these integrations:\n\n"
        
        for integration in sorted(integrations, key=lambda x: x.name):
            integration_name = integration.name.replace('_', ' ').title()
            description = integration.integration_info.get('description', 'No description available')
            content += f"- **[{integration_name}](integrations/{integration.name}.md)**: {description}\n"
        
        content += """

## Getting Started Guide

New to no-code development? Start with our [comprehensive getting started guide](getting_started.md).

## Platform Comparison

Not sure which platform to choose? Check out our [platform comparison guide](platform_comparison.md).

## Support

- [Troubleshooting Guide](troubleshooting.md)
- [Best Practices](best_practices.md)
- [Community Support](community.md)

---

*Happy building! 🚀*
"""
        
        return content
    
    def generate_comparison_guide(self, platform_analyses: List[TemplateAnalysis]) -> str:
        """Generate platform comparison guide."""
        content = f"""# Platform Comparison Guide

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

Choose the right no-code platform for your project with this comprehensive comparison.

## Quick Comparison

| Platform | Complexity | Best For | Pricing |
|----------|------------|----------|---------|
"""
        
        for analysis in sorted(platform_analyses, key=lambda x: x.name):
            platform_name = analysis.name.replace('_', ' ').title()
            complexity = analysis.complexity.title()
            best_for = analysis.platform_info.get('best_for', 'General use')
            pricing = analysis.platform_info.get('pricing_summary', 'Varies')
            content += f"| {platform_name} | {complexity} | {best_for} | {pricing} |\n"
        
        content += "\n## Detailed Comparison\n\n"
        
        for analysis in sorted(platform_analyses, key=lambda x: x.name):
            platform_name = analysis.name.replace('_', ' ').title()
            content += f"### {platform_name}\n\n"
            content += f"**Complexity**: {analysis.complexity.title()}\n\n"
            
            if analysis.key_features:
                content += "**Key Features**:\n"
                for feature in analysis.key_features[:5]:  # Limit to top 5
                    content += f"- {feature}\n"
                content += "\n"
            
            if analysis.platform_info.get('pros'):
                content += "**Pros**:\n"
                for pro in analysis.platform_info['pros']:
                    content += f"- {pro}\n"
                content += "\n"
            
            if analysis.platform_info.get('cons'):
                content += "**Cons**:\n"
                for con in analysis.platform_info['cons']:
                    content += f"- {con}\n"
                content += "\n"
        
        content += """## Decision Matrix

Use this matrix to help choose the right platform:

### For Beginners
- **Replit**: Great for learning and simple projects
- **Glide**: Perfect for data-driven apps
- **Bubble**: Comprehensive but has a learning curve

### For Advanced Users
- **Webflow**: Professional websites with custom code
- **Retool**: Complex internal tools and dashboards
- **Bubble**: Advanced workflows and integrations

### For Specific Use Cases
- **E-commerce**: Shopify, Webflow
- **Mobile Apps**: Glide, Adalo
- **Websites**: Webflow, Framer
- **Internal Tools**: Retool, Bubble

## Next Steps

1. Review the detailed platform guides
2. Try the platform's free tier or trial
3. Start with a simple project to test the waters
4. Join the platform's community for support

---

*Still unsure? Start with our [getting started guide](getting_started.md) for more guidance.*
"""
        
        return content


class HTMLGenerator(BaseFormatGenerator):
    """Generates HTML documentation."""
    
    def generate_platform_guide(self, analysis: TemplateAnalysis) -> str:
        """Generate platform guide in HTML format."""
        # Convert markdown to HTML (simplified version)
        markdown_content = MarkdownGenerator(self.config, self.template_loader).generate_platform_guide(analysis)
        
        html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{analysis.name.replace('_', ' ').title()} Platform Guide</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; max-width: 800px; margin: 0 auto; padding: 20px; }}
        h1, h2, h3 {{ color: #333; }}
        code {{ background: #f4f4f4; padding: 2px 4px; border-radius: 3px; }}
        pre {{ background: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        .metadata {{ background: #e8f4fd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        .feature-list {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 10px; }}
        .feature-item {{ background: #f8f9fa; padding: 10px; border-radius: 5px; }}
        {self.config.custom_css or ''}
    </style>
</head>
<body>
    <div class="content">
        {self._markdown_to_html(markdown_content)}
    </div>
</body>
</html>"""
        
        return html_content
    
    def _markdown_to_html(self, markdown: str) -> str:
        """Simple markdown to HTML conversion."""
        # This is a simplified conversion - in production, use a proper markdown parser
        html = markdown
        
        # Headers
        html = html.replace('### ', '<h3>').replace('\n', '</h3>\n', html.count('### '))
        html = html.replace('## ', '<h2>').replace('\n', '</h2>\n', html.count('## '))
        html = html.replace('# ', '<h1>').replace('\n', '</h1>\n', html.count('# '))
        
        # Lists
        lines = html.split('\n')
        in_list = False
        result_lines = []
        
        for line in lines:
            if line.strip().startswith('- '):
                if not in_list:
                    result_lines.append('<ul>')
                    in_list = True
                result_lines.append(f'<li>{line.strip()[2:]}</li>')
            else:
                if in_list:
                    result_lines.append('</ul>')
                    in_list = False
                result_lines.append(line)
        
        if in_list:
            result_lines.append('</ul>')
        
        # Paragraphs
        html = '\n'.join(result_lines)
        paragraphs = html.split('\n\n')
        html_paragraphs = []
        
        for p in paragraphs:
            p = p.strip()
            if p and not p.startswith('<'):
                html_paragraphs.append(f'<p>{p}</p>')
            else:
                html_paragraphs.append(p)
        
        return '\n\n'.join(html_paragraphs)


class JSONGenerator(BaseFormatGenerator):
    """Generates JSON documentation."""
    
    def generate_platform_guide(self, analysis: TemplateAnalysis) -> str:
        """Generate platform guide in JSON format."""
        data = {
            'name': analysis.name,
            'title': analysis.name.replace('_', ' ').title(),
            'category': analysis.category,
            'generated_at': datetime.now().isoformat(),
            'metadata': analysis.metadata,
            'platform_info': analysis.platform_info,
            'key_features': analysis.key_features,
            'variables': analysis.variables,
            'complexity': analysis.complexity,
            'estimated_time': analysis.estimated_time,
            'dependencies': analysis.dependencies,
            'best_practices': analysis.best_practices,
            'troubleshooting': analysis.troubleshooting,
            'examples': analysis.examples
        }
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def generate_summary_data(self, analyses: List[TemplateAnalysis]) -> str:
        """Generate summary data for all templates."""
        summary = {
            'generated_at': datetime.now().isoformat(),
            'total_templates': len(analyses),
            'categories': {},
            'templates': []
        }
        
        # Group by category
        for analysis in analyses:
            if analysis.category not in summary['categories']:
                summary['categories'][analysis.category] = 0
            summary['categories'][analysis.category] += 1
            
            # Add template summary
            summary['templates'].append({
                'name': analysis.name,
                'title': analysis.name.replace('_', ' ').title(),
                'category': analysis.category,
                'complexity': analysis.complexity,
                'estimated_time': analysis.estimated_time,
                'key_features_count': len(analysis.key_features),
                'variables_count': len(analysis.variables),
                'has_examples': len(analysis.examples) > 0
            })
        
        return json.dumps(summary, indent=2, ensure_ascii=False)


class FormatGeneratorFactory:
    """Factory for creating format generators."""
    
    @staticmethod
    def create_generator(format_type: str, config: DocumentationConfig, template_loader: TemplateLoader) -> BaseFormatGenerator:
        """Create a format generator based on the specified type.
        
        Args:
            format_type: Type of format ('markdown', 'html', 'json')
            config: Documentation configuration
            template_loader: Template loader instance
            
        Returns:
            Format generator instance
        """
        generators = {
            'markdown': MarkdownGenerator,
            'html': HTMLGenerator,
            'json': JSONGenerator
        }
        
        generator_class = generators.get(format_type.lower(), MarkdownGenerator)
        return generator_class(config, template_loader)


# Convenience functions
def generate_platform_guide(analysis: TemplateAnalysis, format_type: str = 'markdown', 
                           config: Optional[DocumentationConfig] = None,
                           template_loader: Optional[TemplateLoader] = None) -> str:
    """Generate a platform guide in the specified format."""
    if config is None:
        config = DocumentationConfig(output_format=format_type)
    if template_loader is None:
        template_loader = TemplateLoader()
    
    generator = FormatGeneratorFactory.create_generator(format_type, config, template_loader)
    return generator.generate_platform_guide(analysis)


def generate_documentation_index(analyses: List[TemplateAnalysis], format_type: str = 'markdown',
                                config: Optional[DocumentationConfig] = None,
                                template_loader: Optional[TemplateLoader] = None) -> str:
    """Generate a documentation index in the specified format."""
    if config is None:
        config = DocumentationConfig(output_format=format_type)
    if template_loader is None:
        template_loader = TemplateLoader()
    
    if format_type.lower() == 'markdown':
        generator = MarkdownGenerator(config, template_loader)
        return generator.generate_main_index(analyses)
    elif format_type.lower() == 'json':
        generator = JSONGenerator(config, template_loader)
        return generator.generate_summary_data(analyses)
    else:
        # Default to markdown
        generator = MarkdownGenerator(config, template_loader)
        return generator.generate_main_index(analyses)
