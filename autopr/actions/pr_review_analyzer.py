"""
PR Review Analyzer Module

This module provides functionality to analyze pull request reviews and generate
insights, metrics, and recommendations.
"""

import logging
from dataclasses import dataclass
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class PRReviewAnalysis:
    """Data class to hold PR review analysis results."""

    pr_number: int
    review_count: int
    comment_count: int
    approval_count: int
    requested_changes_count: int
    review_comment_count: int
    review_commenters: List[str]
    review_duration_hours: Optional[float] = None
    sentiment_score: Optional[float] = None
    risk_score: Optional[float] = None
    summary: Optional[str] = None
    recommendations: Optional[List[str]] = None
    metadata: Optional[Dict[str, Any]] = None


class PRReviewAnalyzer:
    """Analyzes pull request reviews to generate insights and metrics."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the PR review analyzer.

        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        logger.info("PRReviewAnalyzer initialized")

    def analyze_reviews(
        self,
        pr_number: int,
        reviews_data: List[Dict[str, Any]],
        comments_data: List[Dict[str, Any]],
        pr_data: Optional[Dict[str, Any]] = None,
    ) -> PRReviewAnalysis:
        """Analyze PR reviews and generate insights.

        Args:
            pr_number: The pull request number
            reviews_data: List of review data from GitHub API
            comments_data: List of review comments from GitHub API
            pr_data: Optional PR metadata

        Returns:
            PRReviewAnalysis object containing analysis results
        """
        logger.info(f"Analyzing reviews for PR #{pr_number}")

        # Count different types of reviews
        approval_count = sum(1 for r in reviews_data if r.get("state") == "APPROVED")
        requested_changes_count = sum(
            1 for r in reviews_data if r.get("state") == "CHANGES_REQUESTED"
        )

        # Count comments
        review_comment_count = len(comments_data)
        commenters = list({c["user"]["login"] for c in comments_data if c.get("user")})

        # Create analysis result
        analysis = PRReviewAnalysis(
            pr_number=pr_number,
            review_count=len(reviews_data),
            comment_count=review_comment_count,
            approval_count=approval_count,
            requested_changes_count=requested_changes_count,
            review_comment_count=review_comment_count,
            review_commenters=commenters,
        )

        # Generate summary and recommendations
        analysis.summary = self._generate_summary(analysis, pr_data)
        analysis.recommendations = self._generate_recommendations(analysis)

        return analysis

    def _generate_summary(
        self, analysis: PRReviewAnalysis, pr_data: Optional[Dict[str, Any]] = None
    ) -> str:
        """Generate a summary of the PR review analysis."""
        summary_parts = [
            f"PR #{analysis.pr_number} has received {analysis.review_count} reviews "
            f"({analysis.approval_count} approvals, {analysis.requested_changes_count} change requests)."
        ]

        if analysis.review_comment_count > 0:
            summary_parts.append(
                f"There are {analysis.review_comment_count} review comments "
                f"from {len(analysis.review_commenters)} different reviewers."
            )

        if pr_data:
            if pr_data.get("merged"):
                summary_parts.append("This PR has been successfully merged.")
            elif pr_data.get("state") == "closed":
                summary_parts.append("This PR was closed without merging.")

        return " ".join(summary_parts)

    def _generate_recommendations(self, analysis: PRReviewAnalysis) -> List[str]:
        """Generate recommendations based on the PR review analysis."""
        recommendations = []

        if analysis.approval_count == 0 and analysis.review_count > 0:
            recommendations.append(
                "Consider addressing the remaining review comments to get an approval."
            )

        if analysis.requested_changes_count > 0:
            recommendations.append(
                f"There are {analysis.requested_changes_count} change requests that need to be addressed."
            )

        if analysis.review_count == 0:
            recommendations.append(
                "This PR hasn't been reviewed yet. Consider requesting reviews from team members."
            )

        if not recommendations:
            recommendations.append("No specific recommendations at this time.")

        return recommendations
