""" AutoPR Action: PR Review Analyzer Analyzes PR reviews from CodeRabbit and other AI tools to
determine next steps """

import json import re from typing import Dict, List, Any, Optional from pydantic import BaseModel
from datetime import datetime

class PRReviewInputs(BaseModel): pr_number: int repository: str review_data: Dict[str, Any]
severity_threshold: str = "medium" auto_assign: bool = True

class PRReviewOutputs(BaseModel): analysis_summary: str issues_found: List[Dict[str, Any]]
recommended_actions: List[str] github_issues_created: List[Dict[str, Any]] linear_tickets_created:
List[Dict[str, Any]] ai_assignments: Dict[str, str] should_block_merge: bool

class PRReviewAnalyzer: def **init**(self): self.severity_levels = { 'critical': 4, 'high': 3,
'medium': 2, 'low': 1 }

        self.ai_routing_rules = {
            'typescript': 'charlie',
            'security': 'snyk',
            'performance': 'azure_sre',
            'documentation': 'promptless',
            'testing': 'testim'
        }

    def analyze_pr_review(self, inputs: PRReviewInputs) -> PRReviewOutputs:
        """Main analysis function for PR reviews"""

        # Parse review data from multiple sources
        coderabbit_findings = self._parse_coderabbit_review(inputs.review_data.get('coderabbit', {}))
        copilot_suggestions = self._parse_copilot_review(inputs.review_data.get('copilot', {}))
        typescript_issues = self._parse_typescript_check(inputs.review_data.get('typescript_check', {}))

        # Combine all findings
        all_issues = coderabbit_findings + copilot_suggestions + typescript_issues

        # Filter by severity threshold
        filtered_issues = self._filter_by_severity(all_issues, inputs.severity_threshold)

        # Generate recommendations
        recommendations = self._generate_recommendations(filtered_issues)

        # Create issues and tickets
        github_issues = []
        linear_tickets = []
        ai_assignments = {}

        if inputs.auto_assign:
            github_issues, linear_tickets, ai_assignments = self._create_assignments(
                filtered_issues, inputs.pr_number, inputs.repository
            )

        # Determine if merge should be blocked
        should_block = self._should_block_merge(filtered_issues, inputs.severity_threshold)

        return PRReviewOutputs(
            analysis_summary=self._generate_summary(filtered_issues),
            issues_found=filtered_issues,
            recommended_actions=recommendations,
            github_issues_created=github_issues,
            linear_tickets_created=linear_tickets,
            ai_assignments=ai_assignments,
            should_block_merge=should_block
        )

    def _parse_coderabbit_review(self, coderabbit_data: Dict) -> List[Dict]:
        """Parse CodeRabbit review findings"""
        findings = []

        for finding in coderabbit_data.get('findings', []):
            findings.append({
                'source': 'coderabbit',
                'type': finding.get('category', 'general'),
                'severity': finding.get('severity', 'medium'),
                'title': finding.get('title', ''),
                'description': finding.get('description', ''),
                'file_path': finding.get('file', ''),
                'line_number': finding.get('line', 0),
                'suggested_fix': finding.get('suggestion', ''),
                'confidence': finding.get('confidence', 0.8),
                'tags': finding.get('tags', [])
            })

        return findings

    def _parse_copilot_review(self, copilot_data: Dict) -> List[Dict]:
        """Parse GitHub Copilot Chat suggestions"""
        suggestions = []

        for suggestion in copilot_data.get('suggestions', []):
            suggestions.append({
                'source': 'copilot',
                'type': suggestion.get('type', 'improvement'),
                'severity': suggestion.get('priority', 'low'),
                'title': suggestion.get('title', ''),
                'description': suggestion.get('explanation', ''),
                'file_path': suggestion.get('file', ''),
                'suggested_fix': suggestion.get('code', ''),
                'confidence': 0.7,
                'tags': ['enhancement']
            })

        return suggestions

    def _parse_typescript_check(self, ts_data: Dict) -> List[Dict]:
        """Parse AI TypeScript Check results"""
        issues = []

        for error in ts_data.get('errors', []):
            issues.append({
                'source': 'typescript_check',
                'type': 'typescript',
                'severity': 'high' if error.get('category') == 'error' else 'medium',
                'title': f"TypeScript {error.get('category', 'issue')}",
                'description': error.get('messageText', ''),
                'file_path': error.get('file', ''),
                'line_number': error.get('line', 0),
                'suggested_fix': error.get('suggestion', ''),
                'confidence': 0.9,
                'tags': ['typescript', 'type-safety']
            })

        return issues

    def _filter_by_severity(self, issues: List[Dict], threshold: str) -> List[Dict]:
        """Filter issues by severity threshold"""
        threshold_level = self.severity_levels.get(threshold, 2)

        return [
            issue for issue in issues
            if self.severity_levels.get(issue['severity'], 1) >= threshold_level
        ]

    def _generate_recommendations(self, issues: List[Dict]) -> List[str]:
        """Generate action recommendations based on issues"""
        recommendations = []

        # Group issues by type
        issue_types = {}
        for issue in issues:
            issue_type = issue['type']
            if issue_type not in issue_types:
                issue_types[issue_type] = []
            issue_types[issue_type].append(issue)

        for issue_type, type_issues in issue_types.items():
            count = len(type_issues)
            if issue_type == 'typescript':
                recommendations.append(f"Assign {count} TypeScript issues to CharlieHelps for autonomous fixing")
            elif issue_type == 'security':
                recommendations.append(f"Create security incidents for {count} security vulnerabilities")
            elif issue_type == 'performance':
                recommendations.append(f"Investigate {count} performance issues with monitoring tools")
            else:
                recommendations.append(f"Create GitHub issues for {count} {issue_type} problems")

        return recommendations

    def _create_assignments(self, issues: List[Dict], pr_number: int, repository: str) -> tuple:
        """Create GitHub issues, Linear tickets, and AI assignments"""
        github_issues = []
        linear_tickets = []
        ai_assignments = {}

        for issue in issues:
            if self._should_create_github_issue(issue):
                github_issue = self._create_github_issue(issue, pr_number, repository)
                github_issues.append(github_issue)

            if self._should_create_linear_ticket(issue):
                linear_ticket = self._create_linear_ticket(issue, pr_number)
                linear_tickets.append(linear_ticket)

            # Assign to AI if applicable
            ai_tool = self._get_ai_assignment(issue)
            if ai_tool:
                ai_assignments[f"{issue['type']}_{issue.get('file_path', 'unknown')}"] = ai_tool

        return github_issues, linear_tickets, ai_assignments

    def _should_create_github_issue(self, issue: Dict) -> bool:
        """Determine if issue should create GitHub issue"""
        return issue['type'] in ['security', 'bug', 'performance'] and issue['severity'] in ['high', 'critical']

    def _should_create_linear_ticket(self, issue: Dict) -> bool:
        """Determine if issue should create Linear ticket"""
        return issue['type'] in ['typescript', 'feature', 'enhancement']

    def _create_github_issue(self, issue: Dict, pr_number: int, repository: str) -> Dict:
        """Create GitHub issue data structure"""
        return {
            'title': f"[AI Detected] {issue['title']}",
            'body': f"""

**Detected by**: {issue['source']} **PR**: #{pr_number} **File**: {issue['file_path']} **Line**:
{issue['line_number']} **Severity**: {issue['severity']}

## Issue Description

{issue['description']}

## Suggested Fix

{issue['suggested_fix']}

## AI Confidence Score

{issue['confidence']:.1%} """.strip(), 'labels': [ 'ai-detected', issue['severity'], issue['type'],
f"source-{issue['source']}" ], 'assignees': self.\_get_default_assignees(issue['type']),
'repository': repository }

    def _create_linear_ticket(self, issue: Dict, pr_number: int) -> Dict:
        """Create Linear ticket data structure"""
        return {
            'title': f"[AI Suggested] {issue['title']}",
            'description': f"""

**Source**: {issue['source']} **PR**: #{pr_number} **Type**: {issue['type']}

## Current Implementation

File: {issue['file_path']} Line: {issue['line_number']}

## Suggested Improvement

{issue['description']}

## Implementation Guide

{issue['suggested_fix']}

## AI Confidence

{issue['confidence']:.1%} """.strip(), 'labels': ['ai-suggested', issue['type']], 'priority':
self.\_map_severity_to_priority(issue['severity']), 'team':
self.\_get_team_for_issue_type(issue['type']) }

    def _get_ai_assignment(self, issue: Dict) -> Optional[str]:
        """Get AI tool assignment for issue type"""
        return self.ai_routing_rules.get(issue['type'])

    def _get_default_assignees(self, issue_type: str) -> List[str]:
        """Get default assignees for issue type"""
        assignee_map = {
            'security': ['security-team'],
            'typescript': ['frontend-team'],
            'performance': ['devops-team'],
            'bug': ['development-team']
        }
        return assignee_map.get(issue_type, ['development-team'])

    def _map_severity_to_priority(self, severity: str) -> int:
        """Map severity to Linear priority"""
        priority_map = {
            'critical': 1,
            'high': 2,
            'medium': 3,
            'low': 4
        }
        return priority_map.get(severity, 3)

    def _get_team_for_issue_type(self, issue_type: str) -> str:
        """Get team assignment for issue type"""
        team_map = {
            'typescript': 'frontend',
            'security': 'security',
            'performance': 'devops',
            'documentation': 'product'
        }
        return team_map.get(issue_type, 'development')

    def _should_block_merge(self, issues: List[Dict], threshold: str) -> bool:
        """Determine if merge should be blocked"""
        critical_issues = [
            issue for issue in issues
            if issue['severity'] in ['critical', 'high'] and issue['type'] in ['security', 'typescript']
        ]
        return len(critical_issues) > 0

    def _generate_summary(self, issues: List[Dict]) -> str:
        """Generate analysis summary"""
        if not issues:
            return "No significant issues found. PR is ready for review."

        total_issues = len(issues)
        severity_counts = {}
        type_counts = {}

        for issue in issues:
            severity = issue['severity']
            issue_type = issue['type']

            severity_counts[severity] = severity_counts.get(severity, 0) + 1
            type_counts[issue_type] = type_counts.get(issue_type, 0) + 1

        summary = f"Found {total_issues} issues:\n"

        # Severity breakdown
        for severity, count in sorted(severity_counts.items(), key=lambda x: self.severity_levels.get(x[0], 0), reverse=True):
            summary += f"- {severity.title()}: {count}\n"

        summary += "\nIssue types:\n"

        # Type breakdown
        for issue_type, count in sorted(type_counts.items()):
            summary += f"- {issue_type.title()}: {count}\n"

        return summary

# Entry point for AutoPR

def run(inputs_dict: dict) -> dict: """AutoPR entry point""" inputs =
PRReviewInputs(\*\*inputs_dict) analyzer = PRReviewAnalyzer() outputs =
analyzer.analyze_pr_review(inputs) return outputs.dict()

if **name** == "**main**": # Test the action sample_inputs = { "pr_number": 123, "repository":
"my-org/my-repo", "review_data": { "coderabbit": { "findings": [ { "category": "typescript",
"severity": "high", "title": "Missing type annotation", "description": "Function parameter lacks
type annotation", "file": "src/components/User.tsx", "line": 15, "suggestion": "Add proper
TypeScript interface", "confidence": 0.9 } ] } } }

    result = run(sample_inputs)
    print(json.dumps(result, indent=2))
