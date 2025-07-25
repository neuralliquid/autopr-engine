"""
Scoring Engine Module

Handles confidence calculation and platform ranking for detection results.
"""

from typing import Dict, List, Any, Tuple
import re


class PlatformScoringEngine:
    """Calculates confidence scores for platform detection."""

    def __init__(self) -> None:
        self.scoring_weights = {
            "files": 3.0,  # Platform-specific files are strong indicators
            "dependencies": 2.5,  # Dependencies are reliable indicators
            "scripts": 2.0,  # Package scripts indicate usage patterns
            "folders": 1.5,  # Folder patterns show structure
            "content": 1.0,  # Content patterns are weaker but useful
            "commits": 0.8,  # Commit messages can be misleading
        }

    def calculate_platform_scores(
        self, platform_configs: Dict[str, Dict[str, Any]], detection_results: Dict[str, Any]
    ) -> Dict[str, float]:
        """Calculate confidence scores for all platforms."""
        scores = {}

        for platform in platform_configs.keys():
            score = self._calculate_single_platform_score(
                platform, platform_configs[platform], detection_results
            )
            if score > 0:
                scores[platform] = score

        return self._normalize_scores(scores)

    def rank_platforms(
        self, scores: Dict[str, float], threshold: float = 0.1
    ) -> Tuple[str, List[str]]:
        """Rank platforms by confidence score."""
        # Filter platforms above threshold
        valid_platforms = {k: v for k, v in scores.items() if v >= threshold}

        if not valid_platforms:
            return "unknown", []

        # Sort by score descending
        sorted_platforms = sorted(valid_platforms.items(), key=lambda x: x[1], reverse=True)

        primary_platform = sorted_platforms[0][0]
        secondary_platforms = [platform for platform, _ in sorted_platforms[1:]]

        return primary_platform, secondary_platforms

    def determine_workflow_type(self, scores: Dict[str, float]) -> str:
        """Determine the type of workflow based on platform scores."""
        high_confidence_platforms = [platform for platform, score in scores.items() if score >= 0.7]
        medium_confidence_platforms = [
            platform for platform, score in scores.items() if 0.3 <= score < 0.7
        ]

        if len(high_confidence_platforms) == 1 and len(medium_confidence_platforms) == 0:
            return "single_platform"
        elif len(high_confidence_platforms) >= 1 and len(medium_confidence_platforms) >= 1:
            return "hybrid_workflow"
        elif len(high_confidence_platforms) + len(medium_confidence_platforms) >= 2:
            return "multi_platform"
        else:
            return "single_platform"

    def analyze_hybrid_workflow(
        self, scores: Dict[str, float], platform_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Analyze hybrid workflow patterns."""
        categories = {
            "rapid_prototyping": ["replit", "lovable", "bolt", "cursor", "v0"],
            "ai_assisted": ["github_copilot", "codeium", "tabnine"],
            "cloud_deployment": ["vercel", "netlify", "railway"],
        }

        detected_categories = {}
        for category, platforms in categories.items():
            category_scores = {p: scores.get(p, 0) for p in platforms if p in scores}
            if category_scores:
                max_score = max(category_scores.values())
                if max_score >= 0.3:
                    detected_categories[category] = {
                        "primary_platform": max(category_scores, key=category_scores.get),  # type: ignore[arg-type]
                        "confidence": max_score,
                        "all_platforms": category_scores,
                    }

        return {
            "detected_categories": detected_categories,
            "workflow_complexity": len(detected_categories),
            "integration_opportunities": self._identify_integration_opportunities(
                detected_categories
            ),
        }

    def generate_recommendations(
        self,
        primary_platform: str,
        secondary_platforms: List[str],
        scores: Dict[str, float],
        workflow_type: str,
    ) -> List[str]:
        """Generate enhancement recommendations based on detection results."""
        recommendations = []

        # Platform-specific recommendations
        platform_recommendations = {
            "replit": [
                "Add Replit-specific deployment configuration",
                "Optimize for Replit's collaborative features",
                "Configure Replit database integration",
            ],
            "lovable": [
                "Enhance component library integration",
                "Add Lovable-specific styling optimizations",
                "Configure automated deployment pipeline",
            ],
            "vercel": [
                "Optimize for Vercel's edge functions",
                "Configure automatic deployments",
                "Add Vercel Analytics integration",
            ],
            "github_copilot": [
                "Add Copilot-friendly code comments",
                "Configure Copilot workspace settings",
                "Optimize code structure for AI assistance",
            ],
        }

        # Add primary platform recommendations
        if primary_platform in platform_recommendations:
            recommendations.extend(platform_recommendations[primary_platform])

        # Add workflow-specific recommendations
        if workflow_type == "hybrid_workflow":
            recommendations.extend(
                [
                    "Configure cross-platform compatibility",
                    "Add environment-specific configurations",
                    "Implement unified deployment strategy",
                ]
            )
        elif workflow_type == "multi_platform":
            recommendations.extend(
                [
                    "Standardize development environments",
                    "Add platform detection scripts",
                    "Configure conditional deployments",
                ]
            )

        # Add general recommendations based on confidence
        max_confidence = max(scores.values()) if scores else 0
        if max_confidence < 0.5:
            recommendations.extend(
                [
                    "Add platform-specific configuration files",
                    "Improve project structure clarity",
                    "Add deployment documentation",
                ]
            )

        return recommendations

    def identify_migration_opportunities(
        self, scores: Dict[str, float], platform_configs: Dict[str, Dict[str, Any]]
    ) -> List[str]:
        """Identify potential migration opportunities."""
        opportunities = []

        # Check for outdated platforms
        legacy_indicators = {
            "heroku": "Consider migrating to Railway or Vercel for better performance",
            "now": "Migrate to Vercel (Now.sh is deprecated)",
            "surge": "Consider Netlify or Vercel for better features",
        }

        for platform, message in legacy_indicators.items():
            if platform in scores and scores[platform] > 0.3:
                opportunities.append(message)

        # Check for platform synergies
        if "replit" in scores and scores["replit"] > 0.5:
            if "vercel" not in scores:
                opportunities.append("Consider Vercel for production deployment from Replit")

        if "github_copilot" in scores and "cursor" not in scores:
            opportunities.append("Consider Cursor IDE for enhanced AI-assisted development")

        return opportunities

    def _calculate_single_platform_score(
        self, platform: str, config: Dict[str, Any], results: Dict[str, Any]
    ) -> float:
        """Calculate confidence score for a single platform."""
        score = 0.0

        # File-based scoring
        found_files = results.get("found_files", {}).get(platform, [])
        if found_files:
            file_score = min(len(found_files) / len(config.get("files", [])), 1.0)
            score += file_score * self.scoring_weights["files"]

        # Dependency-based scoring
        dependencies = results.get("dependencies", [])
        platform_deps = config.get("dependencies", [])
        if platform_deps:
            dep_matches = sum(1 for dep in platform_deps if any(dep in d for d in dependencies))
            dep_score = min(dep_matches / len(platform_deps), 1.0)
            score += dep_score * self.scoring_weights["dependencies"]

        # Script-based scoring
        scripts = results.get("scripts", {})
        platform_scripts = config.get("package_scripts", [])
        if platform_scripts:
            script_matches = sum(1 for script in platform_scripts if script in scripts)
            script_score = min(script_matches / len(platform_scripts), 1.0)
            score += script_score * self.scoring_weights["scripts"]

        # Folder-based scoring
        found_folders = results.get("found_folders", {}).get(platform, [])
        if found_folders:
            folder_score = min(len(found_folders) / len(config.get("folder_patterns", [])), 1.0)
            score += folder_score * self.scoring_weights["folders"]

        # Content pattern scoring
        content_matches = results.get("content_matches", {}).get(platform, 0)
        if content_matches > 0:
            content_score = min(content_matches / 10.0, 1.0)  # Normalize to max 1.0
            score += content_score * self.scoring_weights["content"]

        # Commit message scoring
        commit_matches = results.get("commit_matches", {}).get(platform, 0)
        if commit_matches > 0:
            commit_score = min(commit_matches / 5.0, 1.0)  # Normalize to max 1.0
            score += commit_score * self.scoring_weights["commits"]

        return score

    def _normalize_scores(self, scores: Dict[str, float]) -> Dict[str, float]:
        """Normalize scores to 0-1 range."""
        if not scores:
            return {}

        max_score = max(scores.values())
        if max_score == 0:
            return scores

        # Calculate theoretical maximum score
        max_possible = sum(self.scoring_weights.values())

        # Normalize to 0-1 range
        normalized = {}
        for platform, score in scores.items():
            normalized[platform] = min(score / max_possible, 1.0)

        return normalized

    def _identify_integration_opportunities(self, detected_categories: Dict[str, Any]) -> List[str]:
        """Identify integration opportunities between detected platforms."""
        opportunities = []

        categories = list(detected_categories.keys())

        if "rapid_prototyping" in categories and "cloud_deployment" in categories:
            opportunities.append("Integrate prototyping platform with cloud deployment")

        if "ai_assisted" in categories and "rapid_prototyping" in categories:
            opportunities.append("Enhance AI assistance in prototyping workflow")

        if len(categories) >= 3:
            opportunities.append("Create unified development pipeline across all platforms")

        return opportunities
