"""
Template Discovery System
========================

A modular system for discovering, analyzing, and generating documentation
for no-code platform templates.

Main Components:
- template_loader: Template loading and caching
- content_analyzer: Template content analysis and metadata extraction
- format_generators: Multiple output format generators
- template_validators: Template validation system
- quality_metrics: Quality scoring and analysis
- report_generators: Report generation in multiple formats
- qa_framework: Quality assurance framework
- docs_generator: Documentation generation system
- template_browser: Template discovery and browsing
"""

from .content_analyzer import ContentAnalyzer
from .docs_generator import TemplateDocumentationGenerator
from .format_generators import (
    BaseFormatGenerator,
    FormatGeneratorFactory,
    HTMLGenerator,
    JSONGenerator,
    MarkdownGenerator,
)
from .qa_framework import QualityAssuranceFramework

# Quality metrics have been moved to autopr.quality.template_metrics
# Import them directly from there when needed
from .report_generators import HTMLReportGenerator, JSONReportGenerator, MarkdownReportGenerator
from .report_generators import ReportGeneratorFactory as QAReportGeneratorFactory
from .template_browser import TemplateBrowser, TemplateInfo
from .template_loader import TemplateLoader
from .template_validators import ValidationIssue, ValidationSeverity, ValidatorRegistry
from .validation_rules import ValidationRuleLoader

__all__ = [
    # Template loading and analysis
    "TemplateLoader",
    "ContentAnalyzer",
    # Format generators
    "BaseFormatGenerator",
    "MarkdownGenerator",
    "HTMLGenerator",
    "JSONGenerator",
    "FormatGeneratorFactory",
    # Validation system
    "ValidationIssue",
    "ValidationSeverity",
    "ValidatorRegistry",
    "ValidationRuleLoader",
    # Quality metrics
    "QualityMetrics",
    "QualityAnalyzer",
    "QualityScorer",
    # Report generators
    "JSONReportGenerator",
    "MarkdownReportGenerator",
    "HTMLReportGenerator",
    "QAReportGeneratorFactory",
    # Main systems
    "QualityAssuranceFramework",
    "TemplateDocumentationGenerator",
    "TemplateBrowser",
    "TemplateInfo",
]
