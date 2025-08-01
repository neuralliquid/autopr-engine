"""
AI-Enhanced Quality Analysis Module

This module provides AI-powered code analysis capabilities for the Quality Engine,
integrating with the AutoPR LLM provider system.
"""

from .ai_analyzer import AICodeAnalyzer, CodeSuggestion
from .ai_handler import AIHandler
from .ai_modes import (
    QualityMode,
    analyze_code_architecture,
    analyze_security_issues,
    create_tool_result_from_ai_analysis,
    initialize_llm_manager,
    run_ai_analysis,
)

__all__ = [
    "QualityMode",
    "run_ai_analysis",
    "initialize_llm_manager",
    "create_tool_result_from_ai_analysis",
    "analyze_code_architecture",
    "analyze_security_issues",
    "AICodeAnalyzer",
    "CodeSuggestion",
    "AIHandler",
]
