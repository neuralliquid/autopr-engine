#!/usr/bin/env python3
"""
Template Documentation Generator
===============================

Automatically generates comprehensive documentation for no-code platform templates
including user guides, API documentation, and integration tutorials.

This is the main orchestrator that coordinates the modular documentation generation system.

Features:
- Markdown documentation generation
- HTML documentation with styling
- Platform-specific guides
- Integration tutorials
- Code examples and snippets
- Interactive decision trees
- Modular architecture with template extraction
"""

import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

# Import modular components
from .template_loader import TemplateLoader
from .content_analyzer import ContentAnalyzer, TemplateAnalysis
from .format_generators import (
    DocumentationConfig, 
    FormatGeneratorFactory,
    MarkdownGenerator,
    HTMLGenerator,
    JSONGenerator
)


class TemplateDocumentationGenerator:
    """Generates comprehensive documentation for templates using modular architecture."""
    
    def __init__(self, templates_root: Optional[str] = None, config: Optional[DocumentationConfig] = None) -> None:
        """Initialize the documentation generator."""
        if templates_root is None:
            current_dir = Path(__file__).parent
            templates_root_path = current_dir.parent
        else:
            templates_root_path = Path(templates_root)
        
        self.templates_root = templates_root_path
        self.config = config or DocumentationConfig()
        self.output_dir = self.templates_root / "docs"
        self.output_dir.mkdir(exist_ok=True)
        
        # Initialize modular components
        self.template_loader = TemplateLoader(self.templates_root)
        self.content_analyzer = ContentAnalyzer(self.templates_root)
        self.format_generator = FormatGeneratorFactory.create_generator(
            self.config.output_format, self.config, self.template_loader
        )
    
    def _discover_templates(self) -> List[TemplateAnalysis]:
        """Discover and analyze all templates in the templates directory."""
        template_files = []
        
        # Find all template files
        for pattern in ['platforms/**/*.yml', 'use-cases/*.yml', 'integrations/*.yml']:
            template_files.extend(self.templates_root.glob(pattern))
        
        # Exclude platform-categories.yml
        template_files = [f for f in template_files if f.name != 'platform-categories.yml']
        
        # Analyze all templates
        return self.content_analyzer.analyze_multiple_templates(template_files)
    
    def generate_all_documentation(self) -> Dict[str, str]:
        """Generate complete documentation suite using modular architecture."""
        generated_files: Dict[str, str] = {}
        
        # Discover and analyze all templates
        template_analyses = self._discover_templates()
        
        # Generate main index
        if self.config.generate_index:
            index_file = self.generate_main_index(template_analyses)
            generated_files['index'] = index_file
        
        # Generate guides for each template
        for analysis in template_analyses:
            if analysis.category == 'platform':
                guide_file = self.generate_platform_guide(analysis)
                generated_files[f'platform_{analysis.name}'] = guide_file
            elif analysis.category == 'use_case':
                guide_file = self.generate_use_case_guide(analysis)
                generated_files[f'use_case_{analysis.name}'] = guide_file
            elif analysis.category == 'integration':
                guide_file = self.generate_integration_guide(analysis)
                generated_files[f'integration_{analysis.name}'] = guide_file
        
        # Generate comparison guide for platforms
        platform_analyses = [a for a in template_analyses if a.category == 'platform']
        if platform_analyses:
            comparison_file = self.generate_comparison_guide(platform_analyses)
            generated_files['platform_comparison'] = comparison_file
        
        return generated_files
    
    def generate_main_index(self) -> str:
        """Generate the main documentation index using modular approach."""
        try:
            # Use template loader to get main index template
            template_content = self.template_loader.load_template('main', 'index')
            
            # Use content analyzer to get template metadata
            analysis = self.content_analyzer.analyze_template('main', 'index')
            
            # Prepare template variables
            template_vars = {
                "title": analysis.metadata.get("title", "No-Code Platform Templates Documentation"),
                "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Use format generator to render content
            content = self.format_generator.generate_content(template_content, template_vars)
            
            return self._save_file("index.md", content)
        except Exception as e:
            # Fallback content if template loading fails
            fallback_content = f"# Documentation Index\n\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nError loading template: {e}"
            return self._save_file("index.md", fallback_content)
    
    def generate_platform_guides(self) -> Dict[str, str]:
        """Generate documentation for all platform templates using modular approach."""
        generated_files: Dict[str, str] = {}
        
        try:
            # Use template loader to discover platform templates
            platform_templates = self.template_loader.discover_templates('platform')
            
            # Create platforms docs directory
            platform_docs_dir = self.output_dir / "platforms"
            platform_docs_dir.mkdir(exist_ok=True)
            
            for template_name in platform_templates:
                try:
                    # Use content analyzer to analyze the platform template
                    analysis = self.content_analyzer.analyze_template('platform', template_name)
                    
                    # Generate platform guide using format generator
                    content = self.format_generator.generate_platform_guide(analysis)
                    
                    # Save the generated file
                    doc_file = self._save_file(f"platforms/{template_name}.md", content)
                    generated_files[f'platform_{template_name}'] = doc_file
                    
                except Exception as e:
                    # Generate error content for failed templates
                    error_content = f"# {template_name.title()} Platform Guide\n\nError generating guide: {e}"
                    doc_file = self._save_file(f"platforms/{template_name}.md", error_content)
                    generated_files[f'platform_{template_name}'] = doc_file
            
            return generated_files
            
        except Exception as e:
            # Return empty dict if discovery fails
            return generated_files
    

    
    def generate_use_case_guides(self) -> Dict[str, str]:
        """Generate documentation for use case templates using modular approach."""
        generated_files: Dict[str, str] = {}
        
        try:
            # Use template loader to discover use case templates
            use_case_templates = self.template_loader.discover_templates('use_case')
            
            # Create use cases docs directory
            use_case_docs_dir = self.output_dir / "use_cases"
            use_case_docs_dir.mkdir(exist_ok=True)
            
            for template_name in use_case_templates:
                try:
                    # Use content analyzer to analyze the use case template
                    analysis = self.content_analyzer.analyze_template('use_case', template_name)
                    
                    # Generate use case guide using format generator
                    content = self.format_generator.generate_use_case_guide(analysis)
                    
                    # Save the generated file
                    doc_file = self._save_file(f"use_cases/{template_name}.md", content)
                    generated_files[f'use_case_{template_name}'] = doc_file
                    
                except Exception as e:
                    # Generate error content for failed templates
                    error_content = f"# {template_name.title()} Use Case Guide\n\nError generating guide: {e}"
                    doc_file = self._save_file(f"use_cases/{template_name}.md", error_content)
                    generated_files[f'use_case_{template_name}'] = doc_file
            
            return generated_files
            
        except Exception as e:
            # Return empty dict if discovery fails
            return generated_files
    
    def generate_integration_guides(self) -> Dict[str, str]:
        """Generate documentation for integration templates using modular approach."""
        generated_files: Dict[str, str] = {}
        
        try:
            # Use template loader to discover integration templates
            integration_templates = self.template_loader.discover_templates('integration')
            
            # Create integrations docs directory
            integration_docs_dir = self.output_dir / "integrations"
            integration_docs_dir.mkdir(exist_ok=True)
            
            for template_name in integration_templates:
                try:
                    # Use content analyzer to analyze the integration template
                    analysis = self.content_analyzer.analyze_template('integration', template_name)
                    
                    # Generate integration guide using format generator
                    content = self.format_generator.generate_integration_guide(analysis)
                    
                    # Save the generated file
                    doc_file = self._save_file(f"integrations/{template_name}.md", content)
                    generated_files[f'integration_{template_name}'] = doc_file
                    
                except Exception as e:
                    # Generate error content for failed templates
                    error_content = f"# {template_name.title()} Integration Guide\n\nError generating guide: {e}"
                    doc_file = self._save_file(f"integrations/{template_name}.md", error_content)
                    generated_files[f'integration_{template_name}'] = doc_file
            
            return generated_files
            
        except Exception as e:
            # Return empty dict if discovery fails
            return generated_files
    

    
    def generate_comparison_guide(self, platform_analyses: List[TemplateAnalysis]) -> str:
        """Generate platform comparison documentation using modular approach."""
        try:
            # Use format generator to create comparison guide
            content = self.format_generator.generate_comparison_guide(platform_analyses)
            
            return self._save_file("platform_comparison.md", content)
            
        except Exception as e:
            # Fallback content if generation fails
            fallback_content = f"# Platform Comparison Guide\n\nGenerated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nError generating comparison: {e}"
            return self._save_file("platform_comparison.md", fallback_content)
    
    def generate_getting_started_guide(self) -> str:
        """Generate a comprehensive getting started guide using modular approach."""
        try:
            # Use template loader to get getting started template
            template_content = self.template_loader.load_template('getting_started', 'guide')
            
            # Use content analyzer to get template metadata
            analysis = self.content_analyzer.analyze_template('getting_started', 'guide')
            
            # Prepare template variables
            template_vars = {
                "title": analysis.metadata.get("title", "Getting Started with No-Code Platform Templates"),
                "generation_timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Use format generator to render content
            content = self.format_generator.generate_content(template_content, template_vars)
            
            return self._save_file("getting_started.md", content)
            
        except Exception as e:
            # Fallback content if template loading fails
            fallback_content = self._generate_header("Getting Started with No-Code Platform Templates")
            fallback_content += f"\n\nError loading template: {e}\n\nPlease check the template files and try again."
            return self._save_file("getting_started.md", fallback_content)
    
    def _generate_header(self, title: str) -> str:
        """Generate a standard header for documentation files."""
        return f"""# {title}

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

"""
    
    def _save_file(self, filename: str, content: str) -> str:
        """Save content to a file and return the file path."""
        file_path = self.output_dir / filename
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(file_path)


def main() -> None:
    """Generate all documentation."""
    generator = TemplateDocumentationGenerator()
    
    print("Generating template documentation...")
    generated_files = generator.generate_all_documentation()
    
    print(f"\nGenerated {len(generated_files)} documentation files:")
    for doc_type, file_path in generated_files.items():
        print(f"  {doc_type}: {file_path}")
    
    print(f"\nDocumentation available in: {generator.output_dir}")


if __name__ == "__main__":
    main()
