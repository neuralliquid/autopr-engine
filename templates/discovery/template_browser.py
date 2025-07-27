#!/usr/bin/env python3
"""
Modular Template Browser
========================

Main orchestrator for the template discovery and browsing system.
Uses modular components for better maintainability and type safety.
"""

from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .platform_recommendations import PlatformRecommendationEngine
from .template_combinations import TemplateCombinationEngine
from .template_file_loader import TemplateFileLoader
from .template_models import (
    PlatformRecommendation,
    PlatformRequirements,
    TemplateCombination,
    TemplateInfo,
    TemplateReport,
)
from .template_reports import TemplateReportGenerator
from .template_search import TemplateSearchEngine

# Export all components
__all__ = [
    "TemplateBrowser",
    "TemplateInfo",
    "PlatformRequirements",
    "PlatformRecommendation",
    "TemplateCombination",
    "TemplateReport",
]


class TemplateBrowser:
    """Main template discovery and browsing system using modular architecture."""

    def __init__(self, templates_root: Optional[str] = None) -> None:
        """Initialize the template browser with modular components."""
        if templates_root is None:
            current_dir = Path(__file__).parent
            templates_root_path = current_dir.parent
        else:
            templates_root_path = Path(templates_root)

        self.templates_root = templates_root_path

        # Initialize modular components
        self.file_loader = TemplateFileLoader(self.templates_root)
        self.templates = self.file_loader.load_all_templates()
        self.platform_categories = self.file_loader.get_platform_categories()

        # Initialize engines
        self.search_engine = TemplateSearchEngine(self.templates)
        self.recommendation_engine = PlatformRecommendationEngine(
            self.templates, self.platform_categories
        )
        self.combination_engine = TemplateCombinationEngine(self.templates)
        self.report_generator = TemplateReportGenerator(self.templates, self.platform_categories)

    def search_templates(
        self,
        query: Optional[str] = None,
        category: Optional[str] = None,
        platform: Optional[str] = None,
        complexity: Optional[str] = None,
        use_case: Optional[str] = None,
    ) -> List[TemplateInfo]:
        """Search templates based on various criteria."""
        return self.search_engine.search_templates(
            query=query,
            category=category,
            platform=platform,
            complexity=complexity,
            use_case=use_case,
        )

    def search_by_features(self, required_features: List[str]) -> List[TemplateInfo]:
        """Search templates that have all required features."""
        return self.search_engine.search_by_features(required_features)

    def search_by_dependencies(self, dependencies: List[str]) -> List[TemplateInfo]:
        """Search templates that have specific dependencies."""
        return self.search_engine.search_by_dependencies(dependencies)

    def get_platform_recommendations(
        self, requirements: Dict[str, Any]
    ) -> List[Tuple[str, float, str]]:
        """Get platform recommendations based on project requirements."""
        return self.recommendation_engine.get_platform_recommendations(requirements)

    def get_template_combinations(self, use_case: str) -> List[Dict[str, Any]]:
        """Get recommended template combinations for a specific use case."""
        return self.combination_engine.get_template_combinations(use_case)

    def get_integration_recommendations(self, template: TemplateInfo) -> List[TemplateInfo]:
        """Get integration recommendations for a specific template."""
        return self.combination_engine.get_integration_recommendations(template)

    def get_workflow_templates(self, main_template: TemplateInfo) -> List[TemplateInfo]:
        """Get workflow templates that complement the main template."""
        return self.combination_engine.get_workflow_templates(main_template)

    def find_similar_templates(self, template: TemplateInfo, limit: int = 5) -> List[TemplateInfo]:
        """Find templates similar to the given template."""
        return self.search_engine.find_similar_templates(template, limit)

    def get_templates_by_category(self) -> Dict[str, List[TemplateInfo]]:
        """Group templates by category."""
        return self.search_engine.get_templates_by_category()

    def get_templates_by_platform(self) -> Dict[str, List[TemplateInfo]]:
        """Group templates by platform."""
        return self.search_engine.get_templates_by_platform()

    def get_templates_by_complexity(self) -> Dict[str, List[TemplateInfo]]:
        """Group templates by complexity level."""
        return self.search_engine.get_templates_by_complexity()

    def generate_template_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of all templates."""
        return self.report_generator.generate_template_report()

    def generate_platform_summary(self) -> Dict[str, Any]:
        """Generate a summary of platform coverage and capabilities."""
        return self.report_generator.generate_platform_summary()

    def generate_category_analysis(self) -> Dict[str, Any]:
        """Generate analysis of template categories."""
        return self.report_generator.generate_category_analysis()

    def export_templates_json(self, output_file: Optional[str] = None) -> str:
        """Export all template metadata to JSON format."""
        return self.report_generator.export_templates_json(
            output_file=output_file, templates_root=self.templates_root
        )

    def export_templates_csv(self, output_file: Optional[str] = None) -> str:
        """Export template metadata to CSV format."""
        return self.report_generator.export_templates_csv(
            output_file=output_file, templates_root=self.templates_root
        )

    def reload_templates(self) -> None:
        """Reload all templates from filesystem."""
        self.templates = self.file_loader.load_all_templates()
        self.platform_categories = self.file_loader.get_platform_categories()

        # Update engines with new data
        self.search_engine = TemplateSearchEngine(self.templates)
        self.recommendation_engine = PlatformRecommendationEngine(
            self.templates, self.platform_categories
        )
        self.combination_engine = TemplateCombinationEngine(self.templates)
        self.report_generator = TemplateReportGenerator(self.templates, self.platform_categories)

    def get_template_count(self) -> int:
        """Get total number of loaded templates."""
        return len(self.templates)

    def get_platform_count(self) -> int:
        """Get total number of unique platforms."""
        platforms = set()
        for template in self.templates:
            platforms.update(template.platforms)
        return len(platforms)

    def get_category_count(self) -> int:
        """Get total number of unique categories."""
        categories = set(template.category for template in self.templates)
        return len(categories)


def main() -> None:
    """Example usage of the modular template browser."""
    browser = TemplateBrowser()

    print("=== Modular Template Discovery System ===\n")

    # Show summary
    report = browser.generate_template_report()
    print(f"Total Templates: {report['summary']['total_templates']}")
    print(f"Categories: {list(report['summary']['categories'].keys())}")
    print(f"Platforms: {list(report['summary']['platforms'].keys())}\n")

    # Search examples
    print("=== Search Examples ===")

    # Search for e-commerce templates
    ecommerce_templates = browser.search_templates(query="ecommerce")
    print(f"E-commerce templates found: {len(ecommerce_templates)}")
    for template in ecommerce_templates[:3]:  # Show first 3
        print(f"  - {template.name} ({template.category})")

    # Search by features
    auth_templates = browser.search_by_features(["authentication", "user management"])
    print(f"\nAuthentication templates found: {len(auth_templates)}")
    for template in auth_templates[:3]:  # Show first 3
        print(f"  - {template.name}")

    # Platform recommendations
    print("\n=== Platform Recommendations ===")
    requirements = {
        "project_type": "mobile_app",
        "team_size": "small",
        "technical_expertise": "beginner",
        "budget": "low",
        "timeline": "medium",
        "features": ["user_authentication", "data_storage"],
    }

    recommendations = browser.get_platform_recommendations(requirements)
    print("Top platform recommendations:")
    for platform, score, reasoning in recommendations[:3]:  # Show top 3
        print(f"  {platform}: {score:.1f} points - {reasoning}")

    # Export metadata
    output_file = browser.export_templates_json()
    print(f"\nTemplate metadata exported to: {output_file}")

    # Show statistics
    print(f"\nStatistics:")
    print(f"  Templates: {browser.get_template_count()}")
    print(f"  Platforms: {browser.get_platform_count()}")
    print(f"  Categories: {browser.get_category_count()}")


if __name__ == "__main__":
    main()
