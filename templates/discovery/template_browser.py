#!/usr/bin/env python3
"""
Template Discovery and Browsing System
=====================================

A comprehensive system for discovering, browsing, and selecting templates
from the no-code platform template library.

Features:
- Template search and filtering
- Platform comparison and recommendations
- Use case matching and suggestions
- Integration requirement analysis
- Template metadata visualization
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, asdict
from collections import defaultdict
import re


@dataclass
class TemplateInfo:
    """Structured template information for discovery and comparison."""
    name: str
    description: str
    category: str
    platforms: List[str]
    file_path: str
    complexity: str = "medium"
    estimated_time: str = "unknown"
    use_cases: List[str] = field(default_factory=list)
    key_features: List[str] = field(default_factory=list)
    variables: Dict[str, Any] = field(default_factory=dict)
    variants: Dict[str, Any] = field(default_factory=dict)
    dependencies: List[str] = field(default_factory=list)
    
    def __post_init__(self) -> None:
        # Fields are now initialized with default_factory, no need for None checks
        pass


class TemplateBrowser:
    """Main template discovery and browsing system."""
    
    def __init__(self, templates_root: Optional[str] = None) -> None:
        """Initialize the template browser with the templates directory."""
        if templates_root is None:
            current_dir = Path(__file__).parent
            templates_root_path = current_dir.parent
        else:
            templates_root_path = Path(templates_root)
        
        self.templates_root = templates_root_path
        self.templates: List[TemplateInfo] = []
        self.platform_categories: Dict[str, Any] = {}
        self._load_all_templates()
    
    def _load_all_templates(self) -> None:
        """Load all templates from the templates directory structure."""
        self.templates = []
        
        # Load platform categories
        categories_file = self.templates_root / "platforms" / "platform-categories.yml"
        if categories_file.exists():
            with open(categories_file, 'r', encoding='utf-8') as f:
                self.platform_categories = yaml.safe_load(f)
        
        # Load platform templates
        platforms_dir = self.templates_root / "platforms"
        if platforms_dir.exists():
            for platform_dir in platforms_dir.iterdir():
                if platform_dir.is_dir():
                    self._load_platform_templates(platform_dir)
        
        # Load use case templates
        use_cases_dir = self.templates_root / "use-cases"
        if use_cases_dir.exists():
            for template_file in use_cases_dir.glob("*.yml"):
                self._load_template_file(template_file, "use_case")
        
        # Load integration templates
        integrations_dir = self.templates_root / "integrations"
        if integrations_dir.exists():
            for template_file in integrations_dir.glob("*.yml"):
                self._load_template_file(template_file, "integration")
    
    def _load_platform_templates(self, platform_dir: Path) -> None:
        """Load templates from a platform directory."""
        for template_file in platform_dir.glob("*.yml"):
            if template_file.name != "platform-categories.yml":
                self._load_template_file(template_file, "platform")
    
    def _load_template_file(self, template_file: Path, default_category: str) -> None:
        """Load a single template file and extract metadata."""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
            
            if not template_data:
                return
            
            # Extract basic information
            name = template_data.get('name', template_file.stem)
            description = template_data.get('description', '')
            category = template_data.get('category', default_category)
            platforms = template_data.get('platforms', [])
            
            # Extract complexity and time estimates
            complexity = "medium"
            estimated_time = "unknown"
            
            if 'use_case_info' in template_data:
                info = template_data['use_case_info']
                complexity = info.get('complexity', 'medium')
                estimated_time = info.get('estimated_development_time', 'unknown')
            elif 'integration_info' in template_data:
                info = template_data['integration_info']
                complexity = info.get('complexity', 'medium')
                estimated_time = info.get('estimated_setup_time', 'unknown')
            elif 'platform_info' in template_data:
                # Platform templates don't have complexity, estimate based on features
                features = template_data['platform_info'].get('key_features', [])
                complexity = "low" if len(features) < 4 else "medium" if len(features) < 7 else "high"
            
            # Extract use cases and features
            use_cases = []
            key_features = []
            
            if 'use_case_info' in template_data:
                use_cases = template_data['use_case_info'].get('use_cases', [])
                key_features = template_data['use_case_info'].get('key_features', [])
            elif 'integration_info' in template_data:
                use_cases = template_data['integration_info'].get('use_cases', [])
                key_features = template_data['integration_info'].get('key_features', [])
            elif 'platform_info' in template_data:
                key_features = template_data['platform_info'].get('key_features', [])
            
            # Extract variables, variants, and dependencies
            variables = template_data.get('variables', {})
            variants = template_data.get('variants', {})
            dependencies = []
            
            if 'dependencies' in template_data:
                deps = template_data['dependencies']
                if isinstance(deps, dict):
                    dependencies = deps.get('required', []) + deps.get('optional', [])
                elif isinstance(deps, list):
                    dependencies = deps
            
            template_info = TemplateInfo(
                name=name,
                description=description,
                category=category,
                platforms=platforms,
                file_path=str(template_file),
                complexity=complexity,
                estimated_time=estimated_time,
                use_cases=use_cases,
                key_features=key_features,
                variables=variables,
                variants=variants,
                dependencies=dependencies
            )
            
            self.templates.append(template_info)
            
        except Exception as e:
            print(f"Error loading template {template_file}: {e}")
    
    def search_templates(self, 
                        query: str = None,
                        category: str = None,
                        platform: str = None,
                        complexity: str = None,
                        use_case: str = None) -> List[TemplateInfo]:
        """Search templates based on various criteria."""
        results = self.templates.copy()
        
        # Filter by category
        if category:
            results = [t for t in results if t.category == category]
        
        # Filter by platform
        if platform:
            results = [t for t in results if platform in t.platforms]
        
        # Filter by complexity
        if complexity:
            results = [t for t in results if t.complexity == complexity]
        
        # Filter by use case
        if use_case:
            results = [t for t in results if any(use_case.lower() in uc.lower() for uc in t.use_cases)]
        
        # Text search in name, description, and features
        if query:
            query_lower = query.lower()
            filtered_results = []
            for template in results:
                if (query_lower in template.name.lower() or
                    query_lower in template.description.lower() or
                    any(query_lower in feature.lower() for feature in template.key_features)):
                    filtered_results.append(template)
            results = filtered_results
        
        return results
    
    def get_platform_recommendations(self, requirements: Dict[str, Any]) -> List[Tuple[str, float, str]]:
        """Get platform recommendations based on project requirements."""
        recommendations = []
        
        # Extract requirements
        project_type = requirements.get('project_type', 'web_app')
        team_size = requirements.get('team_size', 'small')
        technical_expertise = requirements.get('technical_expertise', 'beginner')
        budget = requirements.get('budget', 'low')
        timeline = requirements.get('timeline', 'medium')
        features_needed = requirements.get('features', [])
        
        # Score each platform based on requirements
        for category_name, category_data in self.platform_categories.get('categories', {}).items():
            for platform in category_data.get('platforms', []):
                platform_name = platform['name']
                score = 0.0
                reasoning = []
                
                # Project type compatibility
                if project_type == 'mobile_app' and category_name == 'mobile_focused':
                    score += 30
                    reasoning.append("Optimized for mobile development")
                elif project_type == 'web_app' and category_name in ['ai_powered', 'visual_builders']:
                    score += 25
                    reasoning.append("Excellent for web applications")
                
                # Technical expertise matching
                if technical_expertise == 'beginner':
                    if category_name in ['ai_powered', 'visual_builders']:
                        score += 20
                        reasoning.append("Beginner-friendly interface")
                elif technical_expertise == 'advanced':
                    if category_name == 'developer_friendly':
                        score += 25
                        reasoning.append("Advanced customization capabilities")
                
                # Budget considerations
                pricing_tiers = self.platform_categories.get('pricing_tiers', {})
                if budget == 'low' and platform_name in pricing_tiers.get('free', []):
                    score += 15
                    reasoning.append("Generous free tier available")
                elif budget == 'medium' and platform_name in pricing_tiers.get('budget_friendly', []):
                    score += 10
                    reasoning.append("Affordable pricing")
                
                # Timeline considerations
                if timeline == 'urgent' and category_name == 'ai_powered':
                    score += 15
                    reasoning.append("Rapid development with AI assistance")
                
                # Feature matching
                platform_templates = [t for t in self.templates if platform_name in t.platforms]
                if platform_templates:
                    template_features = set()
                    for template in platform_templates:
                        template_features.update(template.key_features)
                    
                    feature_matches = sum(1 for feature in features_needed 
                                        if any(feature.lower() in tf.lower() for tf in template_features))
                    if feature_matches > 0:
                        score += feature_matches * 5
                        reasoning.append(f"Supports {feature_matches} required features")
                
                if score > 0:
                    recommendations.append((platform_name, score, "; ".join(reasoning)))
        
        # Sort by score descending
        recommendations.sort(key=lambda x: x[1], reverse=True)
        return recommendations[:5]  # Return top 5 recommendations
    
    def get_template_combinations(self, use_case: str) -> List[Dict[str, Any]]:
        """Get recommended template combinations for a specific use case."""
        combinations = []
        
        # Find use case templates
        use_case_templates = [t for t in self.templates if t.category == 'use_case_template' 
                             and use_case.lower() in t.name.lower()]
        
        if not use_case_templates:
            return combinations
        
        main_template = use_case_templates[0]
        
        # Find relevant integration templates
        integration_templates = [t for t in self.templates if t.category == 'integration_template']
        
        # Create combinations for each platform
        for platform in main_template.platforms:
            combination = {
                'platform': platform,
                'main_template': main_template.name,
                'recommended_integrations': [],
                'estimated_total_time': main_template.estimated_time,
                'complexity_score': self._complexity_to_score(main_template.complexity)
            }
            
            # Add relevant integrations based on use case
            if 'ecommerce' in use_case.lower():
                auth_template = next((t for t in integration_templates if 'auth' in t.name.lower()), None)
                payment_template = next((t for t in integration_templates if 'payment' in t.name.lower()), None)
                
                if auth_template and platform in auth_template.platforms:
                    combination['recommended_integrations'].append(auth_template.name)
                if payment_template and platform in payment_template.platforms:
                    combination['recommended_integrations'].append(payment_template.name)
            
            elif 'social' in use_case.lower():
                auth_template = next((t for t in integration_templates if 'auth' in t.name.lower()), None)
                if auth_template and platform in auth_template.platforms:
                    combination['recommended_integrations'].append(auth_template.name)
            
            combinations.append(combination)
        
        return combinations
    
    def _complexity_to_score(self, complexity: str) -> int:
        """Convert complexity string to numeric score."""
        complexity_map = {
            'low': 1,
            'low_to_medium': 2,
            'medium': 3,
            'medium_to_high': 4,
            'high': 5
        }
        return complexity_map.get(complexity, 3)
    
    def generate_template_report(self) -> Dict[str, Any]:
        """Generate a comprehensive report of all templates."""
        report = {
            'summary': {
                'total_templates': len(self.templates),
                'categories': {},
                'platforms': {},
                'complexity_distribution': {},
            },
            'templates_by_category': {},
            'platform_coverage': {},
            'recommendations': {}
        }
        
        # Count by category
        for template in self.templates:
            category = template.category
            report['summary']['categories'][category] = report['summary']['categories'].get(category, 0) + 1
            
            if category not in report['templates_by_category']:
                report['templates_by_category'][category] = []
            report['templates_by_category'][category].append({
                'name': template.name,
                'platforms': template.platforms,
                'complexity': template.complexity
            })
        
        # Count by platform
        platform_counts = defaultdict(int)
        for template in self.templates:
            for platform in template.platforms:
                platform_counts[platform] += 1
        report['summary']['platforms'] = dict(platform_counts)
        
        # Complexity distribution
        complexity_counts = defaultdict(int)
        for template in self.templates:
            complexity_counts[template.complexity] += 1
        report['summary']['complexity_distribution'] = dict(complexity_counts)
        
        # Platform coverage analysis
        for platform in platform_counts:
            platform_templates = [t for t in self.templates if platform in t.platforms]
            report['platform_coverage'][platform] = {
                'total_templates': len(platform_templates),
                'categories': list(set(t.category for t in platform_templates)),
                'use_cases': list(set(uc for t in platform_templates for uc in t.use_cases))
            }
        
        return report
    
    def export_templates_json(self, output_file: str = None) -> str:
        """Export all template metadata to JSON format."""
        if output_file is None:
            output_file = str(self.templates_root / "templates_metadata.json")
        
        templates_data = [asdict(template) for template in self.templates]
        
        export_data = {
            'metadata': {
                'total_templates': len(self.templates),
                'generated_at': '2024-01-01T00:00:00Z',  # Would use actual timestamp
                'version': '1.0.0'
            },
            'platform_categories': self.platform_categories,
            'templates': templates_data
        }
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        return output_file


def main():
    """Example usage of the template browser."""
    browser = TemplateBrowser()
    
    print("=== Template Discovery System ===\n")
    
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
    for template in ecommerce_templates:
        print(f"  - {template.name} ({template.category})")
    
    # Search for mobile templates
    mobile_templates = browser.search_templates(platform="thunkable")
    print(f"\nThunkable templates found: {len(mobile_templates)}")
    for template in mobile_templates:
        print(f"  - {template.name}")
    
    # Platform recommendations
    print("\n=== Platform Recommendations ===")
    requirements = {
        'project_type': 'mobile_app',
        'team_size': 'small',
        'technical_expertise': 'beginner',
        'budget': 'low',
        'timeline': 'medium',
        'features': ['user_authentication', 'data_storage']
    }
    
    recommendations = browser.get_platform_recommendations(requirements)
    print("Top platform recommendations:")
    for platform, score, reasoning in recommendations:
        print(f"  {platform}: {score:.1f} points - {reasoning}")
    
    # Export metadata
    output_file = browser.export_templates_json()
    print(f"\nTemplate metadata exported to: {output_file}")


if __name__ == "__main__":
    main()
