#!/usr/bin/env python3
"""
Template Documentation Generator
===============================

Automatically generates comprehensive documentation for no-code platform templates
including user guides, API documentation, and integration tutorials.

Features:
- Markdown documentation generation
- HTML documentation with styling
- Platform-specific guides
- Integration tutorials
- Code examples and snippets
- Interactive decision trees
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
import re


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


class TemplateDocumentationGenerator:
    """Generates comprehensive documentation for templates."""
    
    def __init__(self, templates_root: str = None, config: DocumentationConfig = None):
        """Initialize the documentation generator."""
        if templates_root is None:
            current_dir = Path(__file__).parent
            templates_root = current_dir.parent
        
        self.templates_root = Path(templates_root)
        self.config = config or DocumentationConfig()
        self.output_dir = self.templates_root / "docs"
        self.output_dir.mkdir(exist_ok=True)
    
    def generate_all_documentation(self) -> Dict[str, str]:
        """Generate complete documentation suite."""
        generated_files = {}
        
        # Generate main index
        if self.config.generate_index:
            index_file = self.generate_main_index()
            generated_files['index'] = index_file
        
        # Generate platform guides
        platform_guides = self.generate_platform_guides()
        generated_files.update(platform_guides)
        
        # Generate use case guides
        use_case_guides = self.generate_use_case_guides()
        generated_files.update(use_case_guides)
        
        # Generate integration guides
        integration_guides = self.generate_integration_guides()
        generated_files.update(integration_guides)
        
        # Generate comparison guide
        comparison_file = self.generate_comparison_guide()
        generated_files['comparison'] = comparison_file
        
        # Generate getting started guide
        getting_started_file = self.generate_getting_started_guide()
        generated_files['getting_started'] = getting_started_file
        
        return generated_files
    
    def generate_main_index(self) -> str:
        """Generate the main documentation index."""
        content = self._generate_header("No-Code Platform Templates Documentation")
        
        content += """
## Overview

This documentation provides comprehensive guides for using no-code platform templates to build applications quickly and efficiently. Our template system supports multiple platforms and use cases, helping you choose the right tools and approaches for your projects.

## Quick Navigation

### 🚀 Getting Started
- [Getting Started Guide](getting_started.md) - New to no-code development?
- [Platform Comparison](platform_comparison.md) - Choose the right platform
- [Template Browser](template_browser.md) - Find the perfect template

### 🏗️ Platform Guides
- [Hostinger Horizons](platforms/horizons.md) - AI-powered web development
- [Bubble](platforms/bubble.md) - Visual drag-and-drop web apps
- [Lovable](platforms/lovable.md) - AI-assisted development with code ownership
- [FlutterFlow](platforms/flutterflow.md) - Professional Flutter mobile apps
- [Thunkable](platforms/thunkable.md) - Cross-platform mobile development
- [Glide](platforms/glide.md) - Spreadsheet-driven mobile apps
- [Replit](platforms/replit.md) - Collaborative development environment

### 📱 Use Case Templates
- [E-commerce Store](use_cases/ecommerce_store.md) - Online stores and marketplaces
- [Social Media Platform](use_cases/social_platform.md) - Community and social apps
- [Project Management Tool](use_cases/project_management.md) - Productivity and collaboration

### 🔌 Integration Guides
- [Authentication Integration](integrations/authentication.md) - User management and security
- [Payment Processing](integrations/payments.md) - E-commerce and subscription billing

### 📊 Decision Tools
- [Platform Selection Wizard](tools/platform_wizard.md) - Interactive platform selection
- [Feature Comparison Matrix](tools/feature_matrix.md) - Detailed feature comparisons
- [Cost Calculator](tools/cost_calculator.md) - Estimate project costs

## Template Categories

### Core Platform Templates
Templates specific to individual no-code platforms, optimized for each platform's strengths and capabilities.

### Use Case Templates
Cross-platform templates for common application types that can be implemented across multiple platforms.

### Integration Templates
Specialized templates for adding specific functionality like authentication, payments, and third-party services.

## Support and Community

- **Documentation Issues**: Report problems or suggest improvements
- **Template Requests**: Request new templates or platform support
- **Community Forum**: Connect with other no-code developers
- **Best Practices**: Learn from successful implementations

---

*Last updated: {timestamp}*
""".format(timestamp=datetime.now().strftime("%Y-%m-%d"))
        
        return self._save_file("index.md", content)
    
    def generate_platform_guides(self) -> Dict[str, str]:
        """Generate documentation for all platform templates."""
        generated_files = {}
        platforms_dir = self.templates_root / "platforms"
        
        if not platforms_dir.exists():
            return generated_files
        
        # Create platforms docs directory
        platform_docs_dir = self.output_dir / "platforms"
        platform_docs_dir.mkdir(exist_ok=True)
        
        for platform_dir in platforms_dir.iterdir():
            if platform_dir.is_dir():
                platform_name = platform_dir.name
                
                # Skip if it's the categories file
                if platform_name == "platform-categories.yml":
                    continue
                
                # Find template file in platform directory
                template_files = list(platform_dir.glob("*.yml"))
                if template_files:
                    template_file = template_files[0]
                    doc_file = self._generate_platform_guide(template_file, platform_name)
                    generated_files[f'platform_{platform_name}'] = doc_file
        
        return generated_files
    
    def _generate_platform_guide(self, template_file: Path, platform_name: str) -> str:
        """Generate documentation for a specific platform."""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
        except Exception as e:
            return self._save_file(f"platforms/{platform_name}.md", f"Error loading template: {e}")
        
        platform_info = template_data.get('platform_info', {})
        name = platform_info.get('name', platform_name.title())
        
        content = self._generate_header(f"{name} Platform Guide")
        
        # Platform overview
        content += f"""
## Platform Overview

**{name}** is a {platform_info.get('type', 'no-code')} platform that enables {template_data.get('description', 'application development')}.

### Key Features
"""
        
        key_features = platform_info.get('key_features', [])
        for feature in key_features:
            content += f"- {feature}\n"
        
        # Pricing information
        if 'pricing' in platform_info:
            content += "\n### Pricing\n\n"
            pricing = platform_info['pricing']
            for tier, details in pricing.items():
                content += f"- **{tier.title()}**: {details}\n"
        
        # Variables and customization
        if 'variables' in template_data:
            content += "\n## Configuration Options\n\n"
            variables = template_data['variables']
            for var_name, var_info in variables.items():
                var_type = var_info.get('type', 'string')
                required = "Required" if var_info.get('required', False) else "Optional"
                description = var_info.get('description', '')
                content += f"### {var_name.replace('_', ' ').title()}\n"
                content += f"- **Type**: {var_type}\n"
                content += f"- **Required**: {required}\n"
                content += f"- **Description**: {description}\n\n"
                
                if 'examples' in var_info:
                    content += "**Examples**:\n"
                    for example in var_info['examples']:
                        content += f"- `{example}`\n"
                    content += "\n"
        
        # Development approach
        if 'development_approach' in template_data:
            approach = template_data['development_approach']
            content += "## Development Approach\n\n"
            content += f"**Method**: {approach.get('method', 'Not specified')}\n\n"
            content += f"{approach.get('description', '')}\n\n"
            
            if 'steps' in approach:
                content += "### Development Steps\n\n"
                for i, step in enumerate(approach['steps'], 1):
                    content += f"{i}. {step}\n"
                content += "\n"
        
        # Best practices
        if 'best_practices' in template_data and self.config.include_best_practices:
            content += "## Best Practices\n\n"
            best_practices = template_data['best_practices']
            for category, practices in best_practices.items():
                content += f"### {category.replace('_', ' ').title()}\n\n"
                if isinstance(practices, list):
                    for practice in practices:
                        content += f"- {practice}\n"
                elif isinstance(practices, dict):
                    for key, value in practices.items():
                        content += f"**{key.replace('_', ' ').title()}**: {value}\n"
                content += "\n"
        
        # Examples
        if 'examples' in template_data and self.config.include_examples:
            content += "## Examples\n\n"
            examples = template_data['examples']
            for example_name, example_data in examples.items():
                content += f"### {example_name.replace('_', ' ').title()}\n\n"
                if isinstance(example_data, dict):
                    if 'name' in example_data:
                        content += f"**Project Name**: {example_data['name']}\n\n"
                    if 'description' in example_data:
                        content += f"**Description**: {example_data['description']}\n\n"
                    if 'variables' in example_data:
                        content += "**Configuration**:\n"
                        for var, value in example_data['variables'].items():
                            content += f"- {var}: `{value}`\n"
                        content += "\n"
                content += "\n"
        
        # Limitations
        if 'limitations' in template_data:
            content += "## Limitations\n\n"
            limitations = template_data['limitations']
            for limitation in limitations:
                content += f"- {limitation}\n"
            content += "\n"
        
        return self._save_file(f"platforms/{platform_name}.md", content)
    
    def generate_use_case_guides(self) -> Dict[str, str]:
        """Generate documentation for use case templates."""
        generated_files = {}
        use_cases_dir = self.templates_root / "use-cases"
        
        if not use_cases_dir.exists():
            return generated_files
        
        # Create use cases docs directory
        use_case_docs_dir = self.output_dir / "use_cases"
        use_case_docs_dir.mkdir(exist_ok=True)
        
        for template_file in use_cases_dir.glob("*.yml"):
            use_case_name = template_file.stem
            doc_file = self._generate_use_case_guide(template_file, use_case_name)
            generated_files[f'use_case_{use_case_name}'] = doc_file
        
        return generated_files
    
    def _generate_use_case_guide(self, template_file: Path, use_case_name: str) -> str:
        """Generate documentation for a specific use case template."""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
        except Exception as e:
            return self._save_file(f"use_cases/{use_case_name}.md", f"Error loading template: {e}")
        
        use_case_info = template_data.get('use_case_info', {})
        name = template_data.get('name', use_case_name.replace('-', ' ').title())
        
        content = self._generate_header(f"{name} Template Guide")
        
        # Use case overview
        content += f"""
## Overview

{template_data.get('description', '')}

### Project Information
- **Complexity**: {use_case_info.get('complexity', 'Medium')}
- **Estimated Development Time**: {use_case_info.get('estimated_development_time', 'Varies')}
- **Target Audience**: {', '.join(use_case_info.get('target_audience', []))}

### Key Features
"""
        
        key_features = use_case_info.get('key_features', [])
        for feature in key_features:
            content += f"- {feature}\n"
        
        # Platform implementations
        if 'platform_implementations' in template_data:
            content += "\n## Platform Implementations\n\n"
            implementations = template_data['platform_implementations']
            
            for platform, impl_data in implementations.items():
                content += f"### {platform.title()}\n\n"
                content += f"**Approach**: {impl_data.get('approach', 'Not specified')}\n\n"
                
                if 'strengths' in impl_data:
                    content += "**Strengths**:\n"
                    for strength in impl_data['strengths']:
                        content += f"- {strength}\n"
                    content += "\n"
                
                if 'setup_steps' in impl_data:
                    content += "**Setup Steps**:\n"
                    for i, step in enumerate(impl_data['setup_steps'], 1):
                        content += f"{i}. {step}\n"
                    content += "\n"
                
                content += f"**Estimated Time**: {impl_data.get('estimated_time', 'Unknown')}\n"
                content += f"**Complexity**: {impl_data.get('complexity', 'Medium')}\n\n"
        
        # Core features breakdown
        if 'core_features' in template_data:
            content += "## Core Features Breakdown\n\n"
            core_features = template_data['core_features']
            
            for feature_name, feature_data in core_features.items():
                content += f"### {feature_name.replace('_', ' ').title()}\n\n"
                content += f"{feature_data.get('description', '')}\n\n"
                
                if 'components' in feature_data:
                    content += "**Components**:\n"
                    for component in feature_data['components']:
                        content += f"- {component}\n"
                    content += "\n"
                
                if 'database_schema' in feature_data:
                    content += "**Database Schema**:\n"
                    schema = feature_data['database_schema']
                    for table, fields in schema.items():
                        if isinstance(fields, list):
                            content += f"- **{table}**: {', '.join(fields)}\n"
                        else:
                            content += f"- **{table}**: {fields}\n"
                    content += "\n"
        
        # Integration requirements
        if 'integration_requirements' in template_data:
            content += "## Integration Requirements\n\n"
            integrations = template_data['integration_requirements']
            
            for integration_name, integration_data in integrations.items():
                content += f"### {integration_name.replace('_', ' ').title()}\n\n"
                if isinstance(integration_data, dict):
                    for service, details in integration_data.items():
                        content += f"**{service.title()}**:\n"
                        if isinstance(details, dict):
                            for key, value in details.items():
                                content += f"- {key.replace('_', ' ').title()}: {value}\n"
                        content += "\n"
        
        return self._save_file(f"use_cases/{use_case_name}.md", content)
    
    def generate_integration_guides(self) -> Dict[str, str]:
        """Generate documentation for integration templates."""
        generated_files = {}
        integrations_dir = self.templates_root / "integrations"
        
        if not integrations_dir.exists():
            return generated_files
        
        # Create integrations docs directory
        integration_docs_dir = self.output_dir / "integrations"
        integration_docs_dir.mkdir(exist_ok=True)
        
        for template_file in integrations_dir.glob("*.yml"):
            integration_name = template_file.stem
            doc_file = self._generate_integration_guide(template_file, integration_name)
            generated_files[f'integration_{integration_name}'] = doc_file
        
        return generated_files
    
    def _generate_integration_guide(self, template_file: Path, integration_name: str) -> str:
        """Generate documentation for a specific integration template."""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
        except Exception as e:
            return self._save_file(f"integrations/{integration_name}.md", f"Error loading template: {e}")
        
        integration_info = template_data.get('integration_info', {})
        name = template_data.get('name', integration_name.replace('-', ' ').title())
        
        content = self._generate_header(f"{name} Guide")
        
        # Integration overview
        content += f"""
## Overview

{template_data.get('description', '')}

### Integration Information
- **Type**: {integration_info.get('type', 'Unknown')}
- **Complexity**: {integration_info.get('complexity', 'Medium')}
- **Estimated Setup Time**: {integration_info.get('estimated_setup_time', 'Varies')}

### Use Cases
"""
        
        use_cases = integration_info.get('use_cases', [])
        for use_case in use_cases:
            content += f"- {use_case.replace('_', ' ').title()}\n"
        
        content += "\n### Key Features\n"
        key_features = integration_info.get('key_features', [])
        for feature in key_features:
            content += f"- {feature}\n"
        
        # Platform implementations
        if 'platform_implementations' in template_data:
            content += "\n## Platform-Specific Implementation\n\n"
            implementations = template_data['platform_implementations']
            
            for platform, impl_data in implementations.items():
                content += f"### {platform.title()}\n\n"
                content += f"**Approach**: {impl_data.get('approach', 'Not specified')}\n\n"
                
                if 'setup_steps' in impl_data:
                    content += "**Setup Steps**:\n"
                    for i, step in enumerate(impl_data['setup_steps'], 1):
                        content += f"{i}. {step}\n"
                    content += "\n"
                
                content += f"**Estimated Time**: {impl_data.get('estimated_time', 'Unknown')}\n"
                content += f"**Complexity**: {impl_data.get('complexity', 'Medium')}\n\n"
        
        # Security and best practices
        if 'security_best_practices' in template_data and self.config.include_best_practices:
            content += "## Security Best Practices\n\n"
            security = template_data['security_best_practices']
            
            for category, practices in security.items():
                content += f"### {category.replace('_', ' ').title()}\n\n"
                if isinstance(practices, list):
                    for practice in practices:
                        content += f"- {practice}\n"
                content += "\n"
        
        return self._save_file(f"integrations/{integration_name}.md", content)
    
    def generate_comparison_guide(self) -> str:
        """Generate platform comparison documentation."""
        comparison_file = self.templates_root / "discovery" / "platform_comparison.yml"
        
        if not comparison_file.exists():
            return self._save_file("platform_comparison.md", "Platform comparison data not found.")
        
        try:
            with open(comparison_file, 'r', encoding='utf-8') as f:
                comparison_data = yaml.safe_load(f)
        except Exception as e:
            return self._save_file("platform_comparison.md", f"Error loading comparison data: {e}")
        
        content = self._generate_header("Platform Comparison Guide")
        
        content += """
## Overview

This guide helps you choose the right no-code platform for your project by comparing features, capabilities, and use cases across all supported platforms.

## Scoring Methodology

Our platform scoring is based on weighted criteria that matter most for no-code development:
"""
        
        criteria = comparison_data.get('comparison_criteria', {})
        for criterion, details in criteria.items():
            weight = details.get('weight', 0)
            description = details.get('description', '')
            content += f"- **{criterion.replace('_', ' ').title()}** ({weight}%): {description}\n"
        
        # Platform scores
        content += "\n## Platform Scores\n\n"
        content += "| Platform | Overall Score | Ease of Use | Customization | Performance | Best For |\n"
        content += "|----------|---------------|-------------|---------------|-------------|----------|\n"
        
        platform_scores = comparison_data.get('platform_scores', {})
        for platform, scores in platform_scores.items():
            name = scores.get('name', platform.title())
            total = scores.get('total_score', 0)
            ease = scores.get('ease_of_use', 0)
            custom = scores.get('customization', 0)
            perf = scores.get('performance', 0)
            platform_type = scores.get('type', 'Unknown')
            content += f"| {name} | {total}/10 | {ease}/10 | {custom}/10 | {perf}/10 | {platform_type.replace('_', ' ').title()} |\n"
        
        # Use case recommendations
        content += "\n## Use Case Recommendations\n\n"
        use_case_recs = comparison_data.get('use_case_recommendations', {})
        for use_case, rec_data in use_case_recs.items():
            content += f"### {use_case.replace('_', ' ').title()}\n\n"
            content += f"**Best Platforms**: {', '.join(rec_data.get('best_platforms', []))}\n\n"
            content += f"**Reasoning**: {rec_data.get('reasoning', '')}\n\n"
            content += f"**Typical Timeline**: {rec_data.get('timeline', 'Varies')}\n\n"
        
        return self._save_file("platform_comparison.md", content)
    
    def generate_getting_started_guide(self) -> str:
        """Generate a comprehensive getting started guide."""
        content = self._generate_header("Getting Started with No-Code Platform Templates")
        
        content += """
## Welcome to No-Code Development!

This guide will help you get started with our no-code platform template system, whether you're a complete beginner or an experienced developer exploring no-code solutions.

## Step 1: Choose Your Platform

The first step is selecting the right platform for your project. Consider these factors:

### Project Type
- **Simple Website**: Hostinger Horizons, Glide
- **Web Application**: Lovable, Bubble, Horizons
- **Mobile App**: FlutterFlow, Thunkable, Glide
- **Complex Business Tool**: Bubble, Replit, FlutterFlow

### Your Experience Level
- **Beginner**: Horizons, Glide, Thunkable
- **Intermediate**: Lovable, Bubble, Thunkable
- **Advanced**: Replit, FlutterFlow, Bubble

### Budget Considerations
- **Free/Low Budget**: Horizons, Glide, Replit (free tiers)
- **Small Business**: Lovable, Thunkable ($25-30/month)
- **Professional**: Bubble, FlutterFlow ($30-70/month)

## Step 2: Select Your Template

Once you've chosen a platform, browse our template library:

### Platform-Specific Templates
Start with templates designed specifically for your chosen platform to leverage its unique strengths.

### Use Case Templates
Choose templates based on what you're building:
- **E-commerce Store**: Online shopping, marketplaces
- **Social Platform**: Community apps, social networks
- **Project Management**: Team collaboration, task tracking

### Integration Templates
Add specific functionality:
- **Authentication**: User login and management
- **Payments**: E-commerce and subscription billing

## Step 3: Set Up Your Development Environment

### Account Creation
1. Sign up for your chosen platform
2. Verify your account and complete any required setup
3. Familiarize yourself with the platform's interface

### Template Configuration
1. Download or access your chosen template
2. Review the configuration variables
3. Customize settings for your specific needs
4. Set up any required integrations

## Step 4: Build Your Application

### Follow the Template Guide
Each template includes:
- Step-by-step setup instructions
- Configuration examples
- Best practices and tips
- Common troubleshooting solutions

### Customize and Extend
- Modify the template to match your requirements
- Add additional features as needed
- Test thoroughly on different devices
- Gather feedback from potential users

## Step 5: Deploy and Launch

### Pre-Launch Checklist
- [ ] Test all functionality thoroughly
- [ ] Verify mobile responsiveness
- [ ] Check security settings
- [ ] Set up analytics and monitoring
- [ ] Prepare marketing materials

### Deployment Options
- **Platform Hosting**: Use your platform's built-in hosting
- **Custom Domain**: Connect your own domain name
- **App Stores**: Submit mobile apps to iOS/Android stores
- **Custom Deployment**: Export code for self-hosting (where available)

## Common Pitfalls to Avoid

### Planning Issues
- Starting without clear requirements
- Choosing the wrong platform for your needs
- Underestimating complexity and timeline

### Development Issues
- Not testing on multiple devices
- Ignoring security best practices
- Over-customizing before validating core functionality

### Launch Issues
- Insufficient user testing
- Poor performance optimization
- Lack of user onboarding

## Getting Help

### Documentation Resources
- Platform-specific guides in this documentation
- Template-specific tutorials and examples
- Integration guides for common services

### Community Support
- Platform community forums
- No-code development communities
- Template-specific discussion groups

### Professional Services
- Platform-certified developers
- No-code development agencies
- Custom development services

## Next Steps

1. **Choose Your Platform**: Use our [Platform Comparison Guide](platform_comparison.md)
2. **Browse Templates**: Explore our [Template Library](template_browser.md)
3. **Start Building**: Follow platform-specific guides
4. **Join the Community**: Connect with other no-code developers

Remember: Start small, iterate quickly, and don't be afraid to experiment. No-code development is about rapid prototyping and learning from real user feedback.

---

*Ready to build something amazing? Let's get started!*
"""
        
        return self._save_file("getting_started.md", content)
    
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


def main():
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
