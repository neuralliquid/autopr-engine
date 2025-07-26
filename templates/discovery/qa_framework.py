#!/usr/bin/env python3
"""
Template Quality Assurance Framework
====================================

Comprehensive quality assurance system for validating no-code platform templates
including validation, testing, and quality scoring.

Features:
- Template validation and linting
- Quality scoring and metrics
- Automated testing framework
- Best practices compliance checking
- Performance and security validation
"""

import os
import yaml
import json
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple, Set
from dataclasses import dataclass, field
from enum import Enum
import re
from datetime import datetime


class ValidationSeverity(Enum):
    """Severity levels for validation issues."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class ValidationIssue:
    """Represents a validation issue found in a template."""
    severity: ValidationSeverity
    category: str
    message: str
    location: str
    suggestion: Optional[str] = None
    rule_id: str = ""


@dataclass
class QualityMetrics:
    """Quality metrics for a template."""
    completeness_score: float = 0.0
    consistency_score: float = 0.0
    usability_score: float = 0.0
    documentation_score: float = 0.0
    security_score: float = 0.0
    performance_score: float = 0.0
    overall_score: float = 0.0
    issues: List[ValidationIssue] = field(default_factory=list)


class TemplateValidator:
    """Validates templates against quality standards."""
    
    def __init__(self) -> None:
        """Initialize the validator with quality rules."""
        self.validation_rules = self._load_validation_rules()
    
    def validate_template(self, template_file: Path) -> QualityMetrics:
        """Validate a single template file."""
        try:
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
        except Exception as e:
            return QualityMetrics(
                issues=[ValidationIssue(
                    ValidationSeverity.ERROR,
                    "parsing",
                    f"Failed to parse template: {e}",
                    str(template_file)
                )]
            )
        
        if not template_data:
            return QualityMetrics(
                issues=[ValidationIssue(
                    ValidationSeverity.ERROR,
                    "structure",
                    "Template file is empty or invalid",
                    str(template_file)
                )]
            )
        
        metrics = QualityMetrics()
        
        # Run all validation checks
        self._validate_structure(template_data, template_file, metrics)
        self._validate_metadata(template_data, template_file, metrics)
        self._validate_variables(template_data, template_file, metrics)
        self._validate_documentation(template_data, template_file, metrics)
        self._validate_examples(template_data, template_file, metrics)
        self._validate_security(template_data, template_file, metrics)
        self._validate_performance(template_data, template_file, metrics)
        
        # Calculate overall scores
        self._calculate_scores(metrics, template_data)
        
        return metrics
    
    def _validate_structure(self, data: Dict[str, Any], file_path: Path, metrics: QualityMetrics) -> None:
        """Validate basic template structure."""
        required_fields = ['name', 'description', 'category', 'platforms']
        
        for field in required_fields:
            if field not in data:
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    "structure",
                    f"Missing required field: {field}",
                    str(file_path),
                    f"Add '{field}' field to template root"
                ))
        
        # Validate field types
        if 'name' in data and not isinstance(data['name'], str):
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                "structure",
                "Template name must be a string",
                str(file_path)
            ))
        
        if 'platforms' in data and not isinstance(data['platforms'], list):
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                "structure",
                "Platforms must be a list",
                str(file_path)
            ))
        
        # Check for empty platforms list
        if 'platforms' in data and len(data['platforms']) == 0:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.WARNING,
                "structure",
                "Platforms list is empty",
                str(file_path),
                "Add at least one supported platform"
            ))
    
    def _validate_metadata(self, data: Dict[str, Any], file_path: Path, metrics: QualityMetrics) -> None:
        """Validate template metadata quality."""
        # Check description length and quality
        if 'description' in data:
            desc = data['description']
            if len(desc) < 20:
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    "metadata",
                    "Description is too short (minimum 20 characters)",
                    str(file_path),
                    "Provide a more detailed description"
                ))
            elif len(desc) > 200:
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.INFO,
                    "metadata",
                    "Description is very long (over 200 characters)",
                    str(file_path),
                    "Consider shortening the description"
                ))
        
        # Validate category
        valid_categories = [
            'no_code_platform', 'use_case_template', 'integration_template',
            'platform_template', 'feature_template'
        ]
        if 'category' in data and data['category'] not in valid_categories:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.WARNING,
                "metadata",
                f"Unknown category: {data['category']}",
                str(file_path),
                f"Use one of: {', '.join(valid_categories)}"
            ))
        
        # Check for version information
        if 'version' not in data:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.INFO,
                "metadata",
                "Template version not specified",
                str(file_path),
                "Add version field for better tracking"
            ))
    
    def _validate_variables(self, data: Dict[str, Any], file_path: Path, metrics: QualityMetrics) -> None:
        """Validate template variables configuration."""
        if 'variables' not in data:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.INFO,
                "variables",
                "No variables defined",
                str(file_path),
                "Consider adding configurable variables"
            ))
            return
        
        variables = data['variables']
        if not isinstance(variables, dict):
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                "variables",
                "Variables must be a dictionary",
                str(file_path)
            ))
            return
        
        for var_name, var_config in variables.items():
            if not isinstance(var_config, dict):
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.ERROR,
                    "variables",
                    f"Variable '{var_name}' configuration must be a dictionary",
                    str(file_path)
                ))
                continue
            
            # Check required variable fields
            if 'type' not in var_config:
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    "variables",
                    f"Variable '{var_name}' missing type specification",
                    str(file_path),
                    "Add 'type' field to variable configuration"
                ))
            
            if 'description' not in var_config:
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    "variables",
                    f"Variable '{var_name}' missing description",
                    str(file_path),
                    "Add 'description' field to variable configuration"
                ))
            
            # Check for examples
            if 'examples' not in var_config:
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.INFO,
                    "variables",
                    f"Variable '{var_name}' missing examples",
                    str(file_path),
                    "Add 'examples' to help users understand usage"
                ))
    
    def _validate_documentation(self, data: Dict[str, Any], file_path: Path, metrics: QualityMetrics) -> None:
        """Validate documentation completeness."""
        documentation_sections = [
            'usage', 'best_practices', 'limitations', 'dependencies'
        ]
        
        missing_sections = []
        for section in documentation_sections:
            if section not in data:
                missing_sections.append(section)
        
        if missing_sections:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.INFO,
                "documentation",
                f"Missing documentation sections: {', '.join(missing_sections)}",
                str(file_path),
                "Add missing sections for better user guidance"
            ))
        
        # Check for platform-specific information
        template_category = data.get('category', '')
        if template_category == 'no_code_platform':
            required_platform_info = ['platform_info']
            for section in required_platform_info:
                if section not in data:
                    metrics.issues.append(ValidationIssue(
                        ValidationSeverity.WARNING,
                        "documentation",
                        f"Platform template missing {section} section",
                        str(file_path),
                        f"Add {section} section with platform details"
                    ))
        
        # Check for use case information
        if template_category == 'use_case_template':
            if 'use_case_info' not in data:
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    "documentation",
                    "Use case template missing use_case_info section",
                    str(file_path),
                    "Add use_case_info section with project details"
                ))
    
    def _validate_examples(self, data: Dict[str, Any], file_path: Path, metrics: QualityMetrics) -> None:
        """Validate examples quality and completeness."""
        if 'examples' not in data:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.INFO,
                "examples",
                "No examples provided",
                str(file_path),
                "Add practical examples to help users"
            ))
            return
        
        examples = data['examples']
        if not isinstance(examples, dict):
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.ERROR,
                "examples",
                "Examples must be a dictionary",
                str(file_path)
            ))
            return
        
        if len(examples) < 2:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.INFO,
                "examples",
                "Consider adding more examples (minimum 2 recommended)",
                str(file_path),
                "Multiple examples show different use cases"
            ))
        
        # Validate example structure
        for example_name, example_data in examples.items():
            if not isinstance(example_data, dict):
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    "examples",
                    f"Example '{example_name}' should be a dictionary",
                    str(file_path)
                ))
                continue
            
            if 'description' not in example_data:
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.INFO,
                    "examples",
                    f"Example '{example_name}' missing description",
                    str(file_path),
                    "Add description to explain the example"
                ))
    
    def _validate_security(self, data: Dict[str, Any], file_path: Path, metrics: QualityMetrics) -> None:
        """Validate security considerations."""
        # Check for security-related documentation
        has_security_info = any(
            'security' in str(data.get(section, '')).lower()
            for section in ['best_practices', 'documentation', 'limitations']
        )
        
        if not has_security_info:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.INFO,
                "security",
                "No security considerations mentioned",
                str(file_path),
                "Consider adding security best practices"
            ))
        
        # Check for sensitive data in examples
        sensitive_patterns = [
            r'password\s*[:=]\s*["\'][^"\']+["\']',
            r'api[_-]?key\s*[:=]\s*["\'][^"\']+["\']',
            r'secret\s*[:=]\s*["\'][^"\']+["\']',
            r'token\s*[:=]\s*["\'][^"\']+["\']'
        ]
        
        content_str = str(data).lower()
        for pattern in sensitive_patterns:
            if re.search(pattern, content_str):
                metrics.issues.append(ValidationIssue(
                    ValidationSeverity.WARNING,
                    "security",
                    "Potential sensitive data in template",
                    str(file_path),
                    "Remove actual credentials and use placeholders"
                ))
                break
    
    def _validate_performance(self, data: Dict[str, Any], file_path: Path, metrics: QualityMetrics) -> None:
        """Validate performance considerations."""
        # Check for performance-related documentation
        has_performance_info = any(
            'performance' in str(data.get(section, '')).lower()
            for section in ['best_practices', 'documentation', 'limitations']
        )
        
        if not has_performance_info:
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.INFO,
                "performance",
                "No performance considerations mentioned",
                str(file_path),
                "Consider adding performance best practices"
            ))
        
        # Check for complexity estimates
        if 'complexity' not in str(data):
            metrics.issues.append(ValidationIssue(
                ValidationSeverity.INFO,
                "performance",
                "No complexity estimate provided",
                str(file_path),
                "Add complexity or time estimates"
            ))
    
    def _calculate_scores(self, metrics: QualityMetrics, data: Dict[str, Any]) -> None:
        """Calculate quality scores based on validation results."""
        # Count issues by severity
        error_count = sum(1 for issue in metrics.issues if issue.severity == ValidationSeverity.ERROR)
        warning_count = sum(1 for issue in metrics.issues if issue.severity == ValidationSeverity.WARNING)
        info_count = sum(1 for issue in metrics.issues if issue.severity == ValidationSeverity.INFO)
        
        # Completeness score (based on required fields)
        required_fields = ['name', 'description', 'category', 'platforms', 'variables', 'examples']
        present_fields = sum(1 for field in required_fields if field in data)
        metrics.completeness_score = (present_fields / len(required_fields)) * 100
        
        # Consistency score (based on naming and structure)
        consistency_deductions = error_count * 20 + warning_count * 10
        metrics.consistency_score = max(0, 100 - consistency_deductions)
        
        # Usability score (based on documentation and examples)
        usability_sections = ['usage', 'best_practices', 'examples', 'variables']
        present_usability = sum(1 for section in usability_sections if section in data)
        metrics.usability_score = (present_usability / len(usability_sections)) * 100
        
        # Documentation score
        doc_sections = ['description', 'usage', 'best_practices', 'limitations', 'dependencies']
        present_docs = sum(1 for section in doc_sections if section in data)
        metrics.documentation_score = (present_docs / len(doc_sections)) * 100
        
        # Security score (basic check)
        security_issues = sum(1 for issue in metrics.issues if issue.category == 'security')
        metrics.security_score = max(0, 100 - security_issues * 25)
        
        # Performance score (basic check)
        performance_issues = sum(1 for issue in metrics.issues if issue.category == 'performance')
        metrics.performance_score = max(0, 100 - performance_issues * 20)
        
        # Overall score (weighted average)
        weights = {
            'completeness': 0.25,
            'consistency': 0.20,
            'usability': 0.20,
            'documentation': 0.15,
            'security': 0.10,
            'performance': 0.10
        }
        
        metrics.overall_score = (
            metrics.completeness_score * weights['completeness'] +
            metrics.consistency_score * weights['consistency'] +
            metrics.usability_score * weights['usability'] +
            metrics.documentation_score * weights['documentation'] +
            metrics.security_score * weights['security'] +
            metrics.performance_score * weights['performance']
        )
    
    def _load_validation_rules(self) -> Dict[str, Any]:
        """Load validation rules configuration."""
        # This would typically load from a configuration file
        return {
            "required_fields": ["name", "description", "category", "platforms"],
            "recommended_fields": ["variables", "examples", "usage", "best_practices"],
            "valid_categories": [
                "no_code_platform", "use_case_template", "integration_template"
            ],
            "security_patterns": [
                r"password\s*[:=]",
                r"api[_-]?key\s*[:=]",
                r"secret\s*[:=]",
                r"token\s*[:=]"
            ]
        }


class QualityAssuranceFramework:
    """Main QA framework for template validation and testing."""
    
    def __init__(self, templates_root: Optional[str] = None) -> None:
        """Initialize the QA framework."""
        if templates_root is None:
            current_dir = Path(__file__).parent
            templates_root_path = current_dir.parent
        else:
            templates_root_path = Path(templates_root)
        
        self.templates_root = templates_root_path
        self.validator = TemplateValidator()
        self.output_dir = self.templates_root / "qa_reports"
        self.output_dir.mkdir(exist_ok=True)
    
    def run_full_qa_suite(self) -> Dict[str, Any]:
        """Run complete QA suite on all templates."""
        results = {
            'summary': {
                'total_templates': 0,
                'passed': 0,
                'failed': 0,
                'warnings': 0,
                'average_score': 0.0,
                'timestamp': datetime.now().isoformat()
            },
            'template_results': {},
            'category_analysis': {},
            'recommendations': []
        }
        
        # Find all template files
        template_files: List[Path] = []
        for pattern in ['platforms/**/*.yml', 'use-cases/*.yml', 'integrations/*.yml']:
            template_files.extend(self.templates_root.glob(pattern))
        
        # Exclude platform-categories.yml
        template_files = [f for f in template_files if f.name != 'platform-categories.yml']
        
        results['summary']['total_templates'] = len(template_files)
        
        total_score = 0.0
        category_scores: Dict[str, float] = {}
        
        # Validate each template
        for template_file in template_files:
            metrics = self.validator.validate_template(template_file)
            
            # Determine pass/fail status
            error_count = sum(1 for issue in metrics.issues if issue.severity == ValidationSeverity.ERROR)
            warning_count = sum(1 for issue in metrics.issues if issue.severity == ValidationSeverity.WARNING)
            
            if error_count == 0:
                if warning_count == 0:
                    results['summary']['passed'] += 1
                else:
                    results['summary']['warnings'] += 1
            else:
                results['summary']['failed'] += 1
            
            # Store results
            results['template_results'][str(template_file)] = {
                'overall_score': metrics.overall_score,
                'scores': {
                    'completeness': metrics.completeness_score,
                    'consistency': metrics.consistency_score,
                    'usability': metrics.usability_score,
                    'documentation': metrics.documentation_score,
                    'security': metrics.security_score,
                    'performance': metrics.performance_score
                },
                'issues': [
                    {
                        'severity': issue.severity.value,
                        'category': issue.category,
                        'message': issue.message,
                        'suggestion': issue.suggestion
                    }
                    for issue in metrics.issues
                ]
            }
            
            total_score += metrics.overall_score
            
            # Track category scores
            try:
                with open(template_file, 'r', encoding='utf-8') as f:
                    template_data = yaml.safe_load(f)
                    category = template_data.get('category', 'unknown')
                    if category not in category_scores:
                        category_scores[category] = []
                    category_scores[category].append(metrics.overall_score)
            except:
                pass
        
        # Calculate averages
        if len(template_files) > 0:
            results['summary']['average_score'] = total_score / len(template_files)
        
        # Category analysis
        for category, scores in category_scores.items():
            results['category_analysis'][category] = {
                'count': len(scores),
                'average_score': sum(scores) / len(scores),
                'min_score': min(scores),
                'max_score': max(scores)
            }
        
        # Generate recommendations
        results['recommendations'] = self._generate_recommendations(results)
        
        # Save report
        self._save_qa_report(results)
        
        return results
    
    def validate_single_template(self, template_path: str) -> QualityMetrics:
        """Validate a single template and return metrics."""
        return self.validator.validate_template(Path(template_path))
    
    def _generate_recommendations(self, results: Dict[str, Any]) -> List[str]:
        """Generate improvement recommendations based on QA results."""
        recommendations = []
        
        # Overall quality recommendations
        avg_score = results['summary']['average_score']
        if avg_score < 70:
            recommendations.append("Overall template quality is below recommended threshold (70%). Focus on improving documentation and examples.")
        elif avg_score < 85:
            recommendations.append("Template quality is good but can be improved. Focus on consistency and completeness.")
        
        # Category-specific recommendations
        for category, analysis in results['category_analysis'].items():
            if analysis['average_score'] < 75:
                recommendations.append(f"Templates in '{category}' category need improvement (avg: {analysis['average_score']:.1f})")
        
        # Common issue recommendations
        all_issues = []
        for template_result in results['template_results'].values():
            all_issues.extend(template_result['issues'])
        
        # Count issue types
        issue_counts: Dict[str, int] = {}
        for issue in all_issues:
            category = issue['category']
            issue_counts[category] = issue_counts.get(category, 0) + 1
        
        # Recommend fixes for common issues
        if issue_counts.get('documentation', 0) > len(results['template_results']) * 0.3:
            recommendations.append("Many templates lack proper documentation. Add usage guides and best practices.")
        
        if issue_counts.get('examples', 0) > len(results['template_results']) * 0.3:
            recommendations.append("Many templates need better examples. Add practical, real-world examples.")
        
        if issue_counts.get('security', 0) > 0:
            recommendations.append("Some templates have security concerns. Review and remove sensitive data.")
        
        return recommendations
    
    def _save_qa_report(self, results: Dict[str, Any]) -> str:
        """Save QA report to file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_file = self.output_dir / f"qa_report_{timestamp}.json"
        
        with open(report_file, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        # Also save a summary report
        summary_file = self.output_dir / f"qa_summary_{timestamp}.md"
        self._generate_markdown_report(results, summary_file)
        
        return str(report_file)
    
    def _generate_markdown_report(self, results: Dict[str, Any], output_file: Path) -> None:
        """Generate a markdown summary report."""
        content = f"""# Template Quality Assurance Report

*Generated on {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*

## Summary

- **Total Templates**: {results['summary']['total_templates']}
- **Passed**: {results['summary']['passed']} ✅
- **Failed**: {results['summary']['failed']} ❌
- **Warnings**: {results['summary']['warnings']} ⚠️
- **Average Score**: {results['summary']['average_score']:.1f}/100

## Category Analysis

| Category | Count | Average Score | Min Score | Max Score |
|----------|-------|---------------|-----------|-----------|
"""
        
        for category, analysis in results['category_analysis'].items():
            content += f"| {category} | {analysis['count']} | {analysis['average_score']:.1f} | {analysis['min_score']:.1f} | {analysis['max_score']:.1f} |\n"
        
        content += "\n## Recommendations\n\n"
        for i, rec in enumerate(results['recommendations'], 1):
            content += f"{i}. {rec}\n"
        
        content += "\n## Template Details\n\n"
        for template_path, template_result in results['template_results'].items():
            template_name = Path(template_path).name
            score = template_result['overall_score']
            status = "✅" if score >= 80 else "⚠️" if score >= 60 else "❌"
            
            content += f"### {template_name} {status}\n\n"
            content += f"**Overall Score**: {score:.1f}/100\n\n"
            
            if template_result['issues']:
                content += "**Issues**:\n"
                for issue in template_result['issues']:
                    severity_icon = "❌" if issue['severity'] == 'error' else "⚠️" if issue['severity'] == 'warning' else "ℹ️"
                    content += f"- {severity_icon} {issue['message']}\n"
                content += "\n"
        
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(content)


def main() -> None:
    """Run QA framework demonstration."""
    qa_framework = QualityAssuranceFramework()
    
    print("Running Template Quality Assurance Suite...")
    results = qa_framework.run_full_qa_suite()
    
    print(f"\n=== QA Results Summary ===")
    print(f"Total Templates: {results['summary']['total_templates']}")
    print(f"Passed: {results['summary']['passed']}")
    print(f"Failed: {results['summary']['failed']}")
    print(f"Warnings: {results['summary']['warnings']}")
    print(f"Average Score: {results['summary']['average_score']:.1f}/100")
    
    print(f"\n=== Category Analysis ===")
    for category, analysis in results['category_analysis'].items():
        print(f"{category}: {analysis['average_score']:.1f}/100 ({analysis['count']} templates)")
    
    print(f"\n=== Recommendations ===")
    for i, rec in enumerate(results['recommendations'], 1):
        print(f"{i}. {rec}")
    
    print(f"\nDetailed reports saved to: {qa_framework.output_dir}")


if __name__ == "__main__":
    main()
