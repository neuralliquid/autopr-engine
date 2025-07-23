"""
AutoPR Engine Actions
Core automation actions for GitHub PR processing
"""

# Import all action classes for easy access
from .platform_detector_enhanced import EnhancedPlatformDetector
from .prototype_enhancer import PrototypeEnhancer
from .platform_detector import PlatformDetector
from .autogen_implementation import AutoGenImplementation
from .issue_creator import IssueCreator
from .configurable_llm_provider import LLMProviderManager
from .autogen_multi_agent import AutoGenAgentSystem
from .mem0_memory_integration import Mem0MemoryManager
from .quality_gates import QualityGates
from .learning_memory_system import LearningMemorySystem
from .multi_platform_integrator import MultiPlatformIntegrator
from .ai_comment_analyzer import AICommentAnalyzer
from .handle_pr_comment import PRCommentHandler

# Utility actions
from .label_pr import LabelPR
from .post_comment import PostComment
from .create_or_update_issue import CreateOrUpdateIssue
from .apply_git_patch import ApplyGitPatch
from .run_security_audit import RunSecurityAudit
from .check_performance_budget import CheckPerformanceBudget
from .visual_regression_test import VisualRegressionTest
from .generate_release_notes import GenerateReleaseNotes

# All available actions
__all__ = [
    # Core AI-powered actions
    "EnhancedPlatformDetector",
    "PrototypeEnhancer", 
    "PlatformDetector",
    "AutoGenImplementation",
    "IssueCreator",
    "LLMProviderManager",
    "AutoGenAgentSystem",
    "Mem0MemoryManager",
    "QualityGates",
    "LearningMemorySystem",
    "MultiPlatformIntegrator",
    "AICommentAnalyzer",
    "PRCommentHandler",
    
    # Utility actions
    "LabelPR",
    "PostComment", 
    "CreateOrUpdateIssue",
    "ApplyGitPatch",
    "RunSecurityAudit",
    "CheckPerformanceBudget",
    "VisualRegressionTest",
    "GenerateReleaseNotes",
] 