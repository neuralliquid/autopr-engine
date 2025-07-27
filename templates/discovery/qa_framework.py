#!/usr/bin/env python3
"""
Template Quality Assurance Framework
===================================

Clean modular orchestrator for template quality assurance using focused components.

Features:
- Modular architecture with single responsibility components
- Template validation using external rule definitions
- Quality scoring and analysis with pluggable algorithms
- Multiple report formats (JSON, Markdown, HTML)
- Batch processing and comparison capabilities
- Backward compatibility maintained
"""

from pathlib import Path
from typing import Dict, List, Any, Optional, Union
from datetime import datetime

# Import modular components
from .validation_rules import get_validation_rules
from .template_validators import ValidationSeverity, ValidationIssue, get_validator_registry
from autopr.quality.template_metrics import QualityMetrics, get_quality_scorer, get_quality_analyzer
from .report_generators import (
    ReportGeneratorFactory, generate_report, generate_batch_report, save_report
)


class TemplateValidator:
    """Validates individual templates using modular validation rules."""
    
    def __init__(self) -> None:
        """Initialize the template validator with modular components."""
        self.validation_rules = get_validation_rules()
        self.validator_registry = get_validator_registry()
        self.quality_scorer = get_quality_scorer()
    
    def validate_template(self, template_file: Path) -> QualityMetrics:
        """Validate a single template file using modular validation."""
        import yaml
        
        try:
            # Load template data
            with open(template_file, 'r', encoding='utf-8') as f:
                template_data = yaml.safe_load(f)
            
            if template_data is None:
                return QualityMetrics(
                    issues=[ValidationIssue(
                        ValidationSeverity.ERROR,
                        "parsing",
                        "Template file is empty or invalid",
                        str(template_file)
                    )],
                    template_path=str(template_file)
                )
            
        except Exception as e:
            return QualityMetrics(
                issues=[ValidationIssue(
                    ValidationSeverity.ERROR,
                    "parsing",
                    f"Failed to parse template: {e}",
                    str(template_file)
                )],
                template_path=str(template_file)
            )
        
        # Run all validation rules using modular validators
        all_issues = []
        total_checks = 0
        
        for rule in self.validation_rules.get_all_rules():
            if not rule.enabled:
                continue
            
            total_checks += 1
            issues = self.validator_registry.run_validation(
                rule.check_function, template_data, template_file, rule
            )
            all_issues.extend(issues)
        
        # Calculate quality metrics using modular scorer
        metrics = self.quality_scorer.calculate_metrics(
            all_issues, total_checks, str(template_file)
        )
        
        return metrics
    
    def validate_templates_batch(self, template_files: List[Path]) -> List[QualityMetrics]:
        """Validate multiple template files in batch."""
        results = []
        
        for template_file in template_files:
            try:
                metrics = self.validate_template(template_file)
                results.append(metrics)
            except Exception as e:
                # Create error metrics for failed validation
                error_metrics = QualityMetrics(
                    issues=[ValidationIssue(
                        ValidationSeverity.ERROR,
                        "system",
                        f"Validation failed: {e}",
                        str(template_file)
                    )],
                    template_path=str(template_file)
                )
                results.append(error_metrics)
        
        return results


class QualityAssuranceFramework:
    """Main QA framework orchestrator using modular components."""
    
    def __init__(self, templates_root: Optional[str] = None):
        """Initialize the QA framework with modular architecture."""
        if templates_root is None:
            self.templates_root = Path(__file__).parent.parent
        else:
            self.templates_root = Path(templates_root)
        
        # Initialize modular components
        self.validator = TemplateValidator()
        self.quality_analyzer = get_quality_analyzer()
        self.report_factory = ReportGeneratorFactory()
        
        # Create output directory for reports
        self.output_dir = self.templates_root / "qa_reports"
        self.output_dir.mkdir(exist_ok=True)
    
    def run_qa_suite(self, 
                     template_path: Optional[Union[str, Path]] = None,
                     output_format: str = "markdown",
                     save_report_flag: bool = True,
                     report_path: Optional[str] = None) -> Dict[str, Any]:
        """Run complete QA suite using modular components."""
        
        # Determine templates to validate
        if template_path is None:
            template_files = list(self.templates_root.rglob("*.yml")) + list(self.templates_root.rglob("*.yaml"))
        else:
            template_path = Path(template_path)
            if template_path.is_file():
                template_files = [template_path]
            elif template_path.is_dir():
                template_files = list(template_path.rglob("*.yml")) + list(template_path.rglob("*.yaml"))
            else:
                raise ValueError(f"Template path does not exist: {template_path}")
        
        if not template_files:
            return {
                'error': 'No template files found',
                'template_count': 0,
                'results': []
            }
        
        # Validate templates using modular validator
        template_metrics = self.validator.validate_templates_batch(template_files)
        
        # Analyze results using modular analyzer
        batch_analysis = self.quality_analyzer.batch_analyze_templates(template_metrics)
        
        # Generate report using modular report generators
        report_content = ""
        if len(template_metrics) == 1:
            # Single template report
            analysis = self.quality_analyzer.analyze_template_quality(template_metrics[0])
            report_content = generate_report(template_metrics[0], output_format, analysis)
        else:
            # Batch report
            report_content = generate_batch_report(template_metrics, output_format, batch_analysis)
        
        # Save report if requested
        if save_report_flag and report_content:
            if report_path is None:
                report_path = str(self.templates_root / f"qa_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
            
            saved_path = save_report(report_content, Path(report_path), output_format)
            print(f"QA report saved to: {saved_path}")
        
        # Prepare results
        results = {
            'template_count': len(template_files),
            'average_score': batch_analysis.get('average_score', 0.0),
            'total_issues': sum(len(m.issues) for m in template_metrics),
            'critical_issues': sum(m.errors_count for m in template_metrics),
            'templates_with_errors': sum(1 for m in template_metrics if m.has_critical_issues),
            'quality_distribution': batch_analysis.get('quality_distribution', {}),
            'report_content': report_content,
            'batch_analysis': batch_analysis,
            'template_results': [
                {
                    'path': m.template_path,
                    'score': m.overall_score,
                    'grade': m.quality_grade,
                    'issues': len(m.issues),
                    'errors': m.errors_count,
                    'has_critical_issues': m.has_critical_issues
                }
                for m in template_metrics
            ]
        }
        
        return results
    
    def get_template_recommendations(self, template_path: Union[str, Path]) -> Dict[str, Any]:
        """Get specific recommendations for a template using modular analysis."""
        template_path = Path(template_path)
        
        if not template_path.exists():
            return {'error': f'Template file not found: {template_path}'}
        
        # Validate template using modular validator
        metrics = self.validator.validate_template(template_path)
        
        # Analyze quality using modular analyzer
        analysis = self.quality_analyzer.analyze_template_quality(metrics)
        
        return {
            'template_path': str(template_path),
            'overall_score': metrics.overall_score,
            'quality_grade': metrics.quality_grade,
            'recommendations': analysis.get('recommendations', []),
            'priority_fixes': [
                {
                    'severity': issue.severity.value,
                    'category': issue.category,
                    'message': issue.message,
                    'suggestion': issue.suggestion,
                    'rule_id': issue.rule_id
                }
                for issue in analysis.get('priority_fixes', [])
            ],
            'strengths': analysis.get('strengths', []),
            'weaknesses': analysis.get('weaknesses', [])
        }
    
    def compare_templates(self, template1_path: Union[str, Path], template2_path: Union[str, Path]) -> Dict[str, Any]:
        """Compare quality metrics between two templates using modular components."""
        template1_path = Path(template1_path)
        template2_path = Path(template2_path)
        
        if not template1_path.exists():
            return {'error': f'Template 1 not found: {template1_path}'}
        if not template2_path.exists():
            return {'error': f'Template 2 not found: {template2_path}'}
        
        # Validate both templates using modular validator
        metrics1 = self.validator.validate_template(template1_path)
        metrics2 = self.validator.validate_template(template2_path)
        
        # Compare metrics using modular scorer
        comparison = self.quality_analyzer.scorer.compare_metrics(metrics1, metrics2)
        
        return {
            'template1': {
                'path': str(template1_path),
                'score': metrics1.overall_score,
                'grade': metrics1.quality_grade,
                'issues': len(metrics1.issues)
            },
            'template2': {
                'path': str(template2_path),
                'score': metrics2.overall_score,
                'grade': metrics2.quality_grade,
                'issues': len(metrics2.issues)
            },
            'comparison': comparison
        }


# Convenience functions for backward compatibility
def validate_template(template_path: Union[str, Path]) -> QualityMetrics:
    """Validate a single template (convenience function)."""
    validator = TemplateValidator()
    return validator.validate_template(Path(template_path))


def run_qa_suite(templates_root: Optional[str] = None, **kwargs: Any) -> Dict[str, Any]:
    """Run QA suite (convenience function)."""
    qa_framework = QualityAssuranceFramework(templates_root)
    return qa_framework.run_qa_suite(**kwargs)


# CLI demonstration
if __name__ == "__main__":
    import sys
    
    print("🔍 Template Quality Assurance Framework (Modular)")
    print("=================================================")
    
    # Initialize QA framework
    qa = QualityAssuranceFramework()
    
    if len(sys.argv) > 1:
        template_path = sys.argv[1]
        print(f"\n📋 Analyzing template: {template_path}")
        
        try:
            results = qa.run_qa_suite(template_path=template_path, save_report_flag=False)
            
            print(f"\n📊 Results Summary:")
            print(f"   • Templates analyzed: {results['template_count']}")
            print(f"   • Average score: {results['average_score']:.1f}/100")
            print(f"   • Total issues: {results['total_issues']}")
            print(f"   • Critical issues: {results['critical_issues']}")
            
            if results['critical_issues'] > 0:
                print(f"\n⚠️  {results['critical_issues']} critical issue(s) found!")
            else:
                print(f"\n✅ No critical issues found!")
            
            # Show quality distribution
            if 'quality_distribution' in results['batch_analysis']:
                dist = results['batch_analysis']['quality_distribution']
                print(f"\n📈 Quality Distribution:")
                for grade, count in dist.items():
                    if count > 0:
                        print(f"   • Grade {grade}: {count} template(s)")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    else:
        print("\n📋 Running batch analysis on all templates...")
        
        try:
            results = qa.run_qa_suite(save_report_flag=True)
            
            print(f"\n📊 Batch Results Summary:")
            print(f"   • Templates analyzed: {results['template_count']}")
            print(f"   • Average score: {results['average_score']:.1f}/100")
            print(f"   • Total issues: {results['total_issues']}")
            print(f"   • Templates with errors: {results['templates_with_errors']}")
            
            # Show top issues
            if 'common_issues' in results['batch_analysis']:
                common_issues = results['batch_analysis']['common_issues'][:3]
                if common_issues:
                    print(f"\n🔍 Most Common Issues:")
                    for issue in common_issues:
                        print(f"   • {issue['category']}: {issue['message']} ({issue['count']} templates)")
            
            print(f"\n📄 Detailed report saved to file.")
            
        except Exception as e:
            print(f"❌ Error: {e}")
            sys.exit(1)
    
    print(f"\n✨ QA analysis complete!")


def main() -> None:
    """Main entry point for QA framework CLI."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Template Quality Assurance Framework")
    parser.add_argument("--template-path", "-t", type=str, help="Path to specific template or directory")
    parser.add_argument("--output-format", "-f", choices=["json", "markdown", "html"], default="markdown", help="Output format")
    parser.add_argument("--no-save", action="store_true", help="Don't save report to file")
    parser.add_argument("--report-path", "-r", type=str, help="Custom report output path")
    
    args = parser.parse_args()
    
    # Initialize QA framework
    qa_framework = QualityAssuranceFramework()
    
    try:
        # Run QA suite
        results = qa_framework.run_qa_suite(
            template_path=args.template_path,
            output_format=args.output_format,
            save_report_flag=not args.no_save,
            report_path=args.report_path
        )
        
        # Display summary
        print(f"\n=== QA Results Summary ===")
        print(f"Templates analyzed: {results['template_count']}")
        print(f"Average quality score: {results['average_score']:.1f}/100")
        print(f"Total issues found: {results['total_issues']}")
        print(f"Critical issues: {results['critical_issues']}")
        print(f"Templates with errors: {results['templates_with_errors']}")
        
        if 'quality_distribution' in results:
            print(f"\n=== Quality Distribution ===")
            for grade, count in results['quality_distribution'].items():
                print(f"Grade {grade}: {count} templates")
        
        if 'batch_analysis' in results and 'category_analysis' in results['batch_analysis']:
            print(f"\n=== Category Analysis ===")
            for category, analysis in results['batch_analysis']['category_analysis'].items():
                print(f"{category}: {analysis['average_score']:.1f}/100 ({analysis['count']} templates)")
        
        print(f"\n=== Recommendations ===")
        for i, rec in enumerate(results.get('recommendations', []), 1):
            print(f"{i}. {rec}")
        
        print(f"\nDetailed reports saved to: {qa_framework.output_dir}")
        
    except Exception as e:
        print(f"Error running QA suite: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
