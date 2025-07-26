#!/usr/bin/env python3
"""
Quality Metrics Module
=====================

Quality scoring algorithms and calculations for template quality assurance.

Features:
- Quality scoring and metrics calculation
- Metrics aggregation and analysis
- Score calculation algorithms
- Quality trend analysis
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
import statistics
from datetime import datetime

from .template_validators import ValidationIssue, ValidationSeverity


@dataclass
class QualityMetrics:
    """Comprehensive quality metrics for a template."""
    overall_score: float = 0.0
    category_scores: Dict[str, float] = field(default_factory=dict)
    issues: List[ValidationIssue] = field(default_factory=list)
    total_checks: int = 0
    passed_checks: int = 0
    warnings_count: int = 0
    errors_count: int = 0
    info_count: int = 0
    template_path: str = ""
    analysis_timestamp: Optional[datetime] = None
    
    def __post_init__(self):
        """Calculate derived metrics after initialization."""
        if self.analysis_timestamp is None:
            self.analysis_timestamp = datetime.now()
        
        # Count issues by severity
        self.errors_count = sum(1 for issue in self.issues if issue.severity == ValidationSeverity.ERROR)
        self.warnings_count = sum(1 for issue in self.issues if issue.severity == ValidationSeverity.WARNING)
        self.info_count = sum(1 for issue in self.issues if issue.severity == ValidationSeverity.INFO)
        
        # Calculate passed checks
        self.passed_checks = self.total_checks - len(self.issues)
    
    @property
    def success_rate(self) -> float:
        """Calculate success rate as percentage."""
        if self.total_checks == 0:
            return 0.0
        return (self.passed_checks / self.total_checks) * 100
    
    @property
    def quality_grade(self) -> str:
        """Get quality grade based on overall score."""
        if self.overall_score >= 90:
            return "A"
        elif self.overall_score >= 80:
            return "B"
        elif self.overall_score >= 70:
            return "C"
        elif self.overall_score >= 60:
            return "D"
        else:
            return "F"
    
    @property
    def has_critical_issues(self) -> bool:
        """Check if template has critical issues (errors)."""
        return self.errors_count > 0
    
    def get_issues_by_category(self, category: str) -> List[ValidationIssue]:
        """Get issues for a specific category."""
        return [issue for issue in self.issues if issue.category == category]
    
    def get_issues_by_severity(self, severity: ValidationSeverity) -> List[ValidationIssue]:
        """Get issues by severity level."""
        return [issue for issue in self.issues if issue.severity == severity]


class QualityScorer:
    """Calculates quality scores based on validation results."""
    
    def __init__(self):
        """Initialize the quality scorer."""
        # Severity weights for scoring
        self.severity_weights = {
            ValidationSeverity.ERROR: 10.0,
            ValidationSeverity.WARNING: 5.0,
            ValidationSeverity.INFO: 1.0
        }
        
        # Category importance weights
        self.category_weights = {
            'structure': 2.0,
            'metadata': 1.5,
            'variables': 1.2,
            'documentation': 1.0,
            'examples': 0.8,
            'security': 2.5,
            'performance': 0.8
        }
    
    def calculate_metrics(self, 
                         issues: List[ValidationIssue], 
                         total_checks: int,
                         template_path: str = "") -> QualityMetrics:
        """Calculate comprehensive quality metrics."""
        
        # Initialize metrics
        metrics = QualityMetrics(
            issues=issues,
            total_checks=total_checks,
            template_path=template_path
        )
        
        # Calculate category scores
        metrics.category_scores = self._calculate_category_scores(issues, total_checks)
        
        # Calculate overall score
        metrics.overall_score = self._calculate_overall_score(metrics.category_scores, issues)
        
        return metrics
    
    def _calculate_category_scores(self, issues: List[ValidationIssue], total_checks: int) -> Dict[str, float]:
        """Calculate scores for each category."""
        category_scores = {}
        
        # Group issues by category
        category_issues = {}
        for issue in issues:
            if issue.category not in category_issues:
                category_issues[issue.category] = []
            category_issues[issue.category].append(issue)
        
        # Calculate score for each category
        for category in self.category_weights.keys():
            category_penalty = 0.0
            category_issue_list = category_issues.get(category, [])
            
            # Calculate penalty for this category
            for issue in category_issue_list:
                penalty = self.severity_weights.get(issue.severity, 1.0)
                category_penalty += penalty
            
            # Calculate category score (0-100)
            # Assume roughly equal distribution of checks across categories
            estimated_category_checks = max(1, total_checks // len(self.category_weights))
            max_possible_penalty = estimated_category_checks * self.severity_weights[ValidationSeverity.ERROR]
            
            if max_possible_penalty > 0:
                penalty_ratio = min(1.0, category_penalty / max_possible_penalty)
                category_score = max(0.0, 100.0 * (1.0 - penalty_ratio))
            else:
                category_score = 100.0
            
            category_scores[category] = category_score
        
        return category_scores
    
    def _calculate_overall_score(self, category_scores: Dict[str, float], issues: List[ValidationIssue]) -> float:
        """Calculate weighted overall score."""
        if not category_scores:
            return 0.0
        
        # Calculate weighted average of category scores
        total_weight = 0.0
        weighted_sum = 0.0
        
        for category, score in category_scores.items():
            weight = self.category_weights.get(category, 1.0)
            weighted_sum += score * weight
            total_weight += weight
        
        if total_weight == 0:
            return 0.0
        
        base_score = weighted_sum / total_weight
        
        # Apply critical issue penalty
        critical_penalty = 0.0
        for issue in issues:
            if issue.severity == ValidationSeverity.ERROR:
                critical_penalty += 5.0  # 5 point penalty per error
        
        final_score = max(0.0, base_score - critical_penalty)
        return min(100.0, final_score)
    
    def compare_metrics(self, metrics1: QualityMetrics, metrics2: QualityMetrics) -> Dict[str, Any]:
        """Compare two quality metrics."""
        comparison = {
            'score_difference': metrics2.overall_score - metrics1.overall_score,
            'score_improvement': metrics2.overall_score > metrics1.overall_score,
            'issues_difference': len(metrics2.issues) - len(metrics1.issues),
            'issues_improvement': len(metrics2.issues) < len(metrics1.issues),
            'category_improvements': {},
            'category_regressions': {},
            'new_issues': [],
            'resolved_issues': []
        }
        
        # Compare category scores
        for category in set(metrics1.category_scores.keys()) | set(metrics2.category_scores.keys()):
            score1 = metrics1.category_scores.get(category, 0.0)
            score2 = metrics2.category_scores.get(category, 0.0)
            difference = score2 - score1
            
            if difference > 0:
                comparison['category_improvements'][category] = difference
            elif difference < 0:
                comparison['category_regressions'][category] = abs(difference)
        
        # Find new and resolved issues
        issues1_set = {(issue.category, issue.message, issue.rule_id) for issue in metrics1.issues}
        issues2_set = {(issue.category, issue.message, issue.rule_id) for issue in metrics2.issues}
        
        comparison['new_issues'] = [
            issue for issue in metrics2.issues 
            if (issue.category, issue.message, issue.rule_id) not in issues1_set
        ]
        
        comparison['resolved_issues'] = [
            issue for issue in metrics1.issues 
            if (issue.category, issue.message, issue.rule_id) not in issues2_set
        ]
        
        return comparison


class QualityAnalyzer:
    """Analyzes quality trends and provides insights."""
    
    def __init__(self):
        """Initialize the quality analyzer."""
        self.scorer = QualityScorer()
    
    def analyze_template_quality(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Analyze template quality and provide insights."""
        analysis = {
            'quality_summary': self._get_quality_summary(metrics),
            'strengths': self._identify_strengths(metrics),
            'weaknesses': self._identify_weaknesses(metrics),
            'recommendations': self._generate_recommendations(metrics),
            'priority_fixes': self._get_priority_fixes(metrics),
            'quality_trends': self._analyze_quality_trends(metrics)
        }
        
        return analysis
    
    def _get_quality_summary(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Get a summary of quality metrics."""
        return {
            'overall_score': metrics.overall_score,
            'quality_grade': metrics.quality_grade,
            'success_rate': metrics.success_rate,
            'total_issues': len(metrics.issues),
            'critical_issues': metrics.errors_count,
            'has_critical_issues': metrics.has_critical_issues,
            'analysis_date': metrics.analysis_timestamp.isoformat() if metrics.analysis_timestamp else None
        }
    
    def _identify_strengths(self, metrics: QualityMetrics) -> List[str]:
        """Identify template strengths."""
        strengths = []
        
        # Check high-scoring categories
        for category, score in metrics.category_scores.items():
            if score >= 90:
                strengths.append(f"Excellent {category} quality (score: {score:.1f})")
            elif score >= 80:
                strengths.append(f"Good {category} quality (score: {score:.1f})")
        
        # Check for absence of critical issues
        if metrics.errors_count == 0:
            strengths.append("No critical errors found")
        
        # Check success rate
        if metrics.success_rate >= 90:
            strengths.append(f"High validation success rate ({metrics.success_rate:.1f}%)")
        
        return strengths
    
    def _identify_weaknesses(self, metrics: QualityMetrics) -> List[str]:
        """Identify template weaknesses."""
        weaknesses = []
        
        # Check low-scoring categories
        for category, score in metrics.category_scores.items():
            if score < 60:
                weaknesses.append(f"Poor {category} quality (score: {score:.1f})")
            elif score < 70:
                weaknesses.append(f"Below average {category} quality (score: {score:.1f})")
        
        # Check for critical issues
        if metrics.errors_count > 0:
            weaknesses.append(f"{metrics.errors_count} critical error(s) found")
        
        # Check success rate
        if metrics.success_rate < 70:
            weaknesses.append(f"Low validation success rate ({metrics.success_rate:.1f}%)")
        
        return weaknesses
    
    def _generate_recommendations(self, metrics: QualityMetrics) -> List[str]:
        """Generate improvement recommendations."""
        recommendations = []
        
        # Priority: Fix critical errors first
        if metrics.errors_count > 0:
            recommendations.append(f"PRIORITY: Fix {metrics.errors_count} critical error(s) immediately")
        
        # Category-specific recommendations
        for category, score in metrics.category_scores.items():
            if score < 70:
                category_issues = metrics.get_issues_by_category(category)
                if category_issues:
                    recommendations.append(
                        f"Improve {category}: {len(category_issues)} issue(s) need attention"
                    )
        
        # General recommendations based on overall score
        if metrics.overall_score < 60:
            recommendations.append("Consider major template revision - multiple areas need improvement")
        elif metrics.overall_score < 80:
            recommendations.append("Focus on addressing warnings to improve overall quality")
        
        return recommendations
    
    def _get_priority_fixes(self, metrics: QualityMetrics) -> List[ValidationIssue]:
        """Get priority issues that should be fixed first."""
        priority_issues = []
        
        # All errors are high priority
        priority_issues.extend(metrics.get_issues_by_severity(ValidationSeverity.ERROR))
        
        # High-impact warnings (security, structure)
        high_impact_categories = ['security', 'structure']
        for category in high_impact_categories:
            category_warnings = [
                issue for issue in metrics.get_issues_by_category(category)
                if issue.severity == ValidationSeverity.WARNING
            ]
            priority_issues.extend(category_warnings)
        
        # Sort by severity and category importance
        priority_issues.sort(key=lambda issue: (
            issue.severity.value,
            -self.scorer.category_weights.get(issue.category, 1.0)
        ))
        
        return priority_issues[:10]  # Return top 10 priority issues
    
    def _analyze_quality_trends(self, metrics: QualityMetrics) -> Dict[str, Any]:
        """Analyze quality trends (placeholder for historical analysis)."""
        # This would be enhanced with historical data in a real implementation
        return {
            'current_score': metrics.overall_score,
            'trend_direction': 'stable',  # Would be calculated from historical data
            'improvement_areas': [
                category for category, score in metrics.category_scores.items()
                if score < 80
            ],
            'maintenance_areas': [
                category for category, score in metrics.category_scores.items()
                if score >= 80
            ]
        }
    
    def batch_analyze_templates(self, template_metrics: List[QualityMetrics]) -> Dict[str, Any]:
        """Analyze multiple templates and provide comparative insights."""
        if not template_metrics:
            return {'error': 'No template metrics provided'}
        
        # Calculate aggregate statistics
        scores = [metrics.overall_score for metrics in template_metrics]
        
        analysis = {
            'total_templates': len(template_metrics),
            'average_score': statistics.mean(scores),
            'median_score': statistics.median(scores),
            'score_range': {
                'min': min(scores),
                'max': max(scores)
            },
            'quality_distribution': self._get_quality_distribution(template_metrics),
            'common_issues': self._find_common_issues(template_metrics),
            'best_practices': self._identify_best_practices(template_metrics),
            'improvement_opportunities': self._find_improvement_opportunities(template_metrics)
        }
        
        return analysis
    
    def _get_quality_distribution(self, template_metrics: List[QualityMetrics]) -> Dict[str, int]:
        """Get distribution of quality grades."""
        distribution = {'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0}
        
        for metrics in template_metrics:
            grade = metrics.quality_grade
            distribution[grade] += 1
        
        return distribution
    
    def _find_common_issues(self, template_metrics: List[QualityMetrics]) -> List[Dict[str, Any]]:
        """Find issues that appear across multiple templates."""
        issue_counts = {}
        
        for metrics in template_metrics:
            for issue in metrics.issues:
                key = (issue.category, issue.message)
                if key not in issue_counts:
                    issue_counts[key] = {
                        'category': issue.category,
                        'message': issue.message,
                        'severity': issue.severity,
                        'count': 0,
                        'templates': []
                    }
                issue_counts[key]['count'] += 1
                issue_counts[key]['templates'].append(metrics.template_path)
        
        # Return issues that appear in multiple templates
        common_issues = [
            issue_data for issue_data in issue_counts.values()
            if issue_data['count'] > 1
        ]
        
        # Sort by frequency
        common_issues.sort(key=lambda x: x['count'], reverse=True)
        
        return common_issues[:10]  # Top 10 common issues
    
    def _identify_best_practices(self, template_metrics: List[QualityMetrics]) -> List[str]:
        """Identify best practices from high-quality templates."""
        best_practices = []
        
        # Find high-quality templates (score >= 85)
        high_quality_templates = [
            metrics for metrics in template_metrics
            if metrics.overall_score >= 85
        ]
        
        if high_quality_templates:
            # Analyze common characteristics
            avg_scores = {}
            for category in self.scorer.category_weights.keys():
                category_scores = [
                    metrics.category_scores.get(category, 0)
                    for metrics in high_quality_templates
                ]
                if category_scores:
                    avg_scores[category] = statistics.mean(category_scores)
            
            # Identify strong categories
            for category, avg_score in avg_scores.items():
                if avg_score >= 90:
                    best_practices.append(f"High-quality templates excel in {category} (avg: {avg_score:.1f})")
        
        return best_practices
    
    def _find_improvement_opportunities(self, template_metrics: List[QualityMetrics]) -> List[str]:
        """Find common improvement opportunities across templates."""
        opportunities = []
        
        # Analyze category scores across all templates
        category_scores = {}
        for category in self.scorer.category_weights.keys():
            scores = []
            for metrics in template_metrics:
                if category in metrics.category_scores:
                    scores.append(metrics.category_scores[category])
            
            if scores:
                category_scores[category] = statistics.mean(scores)
        
        # Identify weak areas
        for category, avg_score in category_scores.items():
            if avg_score < 70:
                opportunities.append(f"Organization-wide improvement needed in {category} (avg: {avg_score:.1f})")
            elif avg_score < 80:
                opportunities.append(f"Moderate improvement opportunity in {category} (avg: {avg_score:.1f})")
        
        return opportunities


# Global instances
_quality_scorer = QualityScorer()
_quality_analyzer = QualityAnalyzer()

def get_quality_scorer() -> QualityScorer:
    """Get the global quality scorer instance."""
    return _quality_scorer

def get_quality_analyzer() -> QualityAnalyzer:
    """Get the global quality analyzer instance."""
    return _quality_analyzer
