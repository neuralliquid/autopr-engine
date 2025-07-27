"""
File Analysis Module

Provides a modular system for analyzing files and directories to detect platform-specific patterns.
"""

from pathlib import Path
from typing import Dict, List, Optional, Protocol, Set, Type, TypeVar, runtime_checkable

from autopr.actions.platform_detection.analysis.base import FileAnalysisResult, FileAnalyzer
from autopr.actions.platform_detection.analysis.handlers import (
    DefaultFileHandler,
    DockerfileHandler,
    FileHandler,
    JsonFileHandler,
    PackageJsonHandler,
    PythonFileHandler,
    RequirementsFileHandler,
    YamlFileHandler,
)
from autopr.actions.platform_detection.analysis.patterns import (
    ContentPattern,
    DirectoryPattern,
    FilePattern,
)

__all__ = [
    "FileAnalyzer",
    "FileAnalysisResult",
    "FileHandler",
    "FilePattern",
    "ContentPattern",
    "DirectoryPattern",
]

# Default file handlers for common file types
DEFAULT_HANDLERS = {
    "*.json": JsonFileHandler,
    "*.yaml": YamlFileHandler,
    "*.yml": YamlFileHandler,
    "*.py": PythonFileHandler,
    "requirements*.txt": RequirementsFileHandler,
    "package.json": PackageJsonHandler,
    "Dockerfile": DockerfileHandler,
    "*": DefaultFileHandler,  # Catch-all handler
}


def create_file_analyzer(
    workspace_path: str = ".",
    handlers: Optional[Dict[str, Type[FileHandler]]] = None,
) -> FileAnalyzer:
    """
    Create a configured FileAnalyzer instance with default handlers.

    Args:
        workspace_path: Path to the workspace to analyze
        handlers: Optional mapping of file patterns to handler classes

    Returns:
        Configured FileAnalyzer instance
    """
    if handlers is None:
        handlers = DEFAULT_HANDLERS

    return FileAnalyzer(workspace_path, handlers)
