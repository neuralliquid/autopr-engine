"""
Base classes and interfaces for quality tools used by the Quality Engine.
"""

import abc
from enum import Enum
from typing import Any, Dict, List, Optional, Set

import pydantic
from structlog import get_logger

logger = get_logger(__name__)


class ToolCategory(Enum):
    """Categories of quality tools"""

    FORMATTING = "formatting"
    LINTING = "linting"
    TYPE_CHECKING = "type_checking"
    SECURITY = "security"
    DOCUMENTATION = "documentation"
    COMPLEXITY = "complexity"
    TESTING = "testing"
    DEPENDENCY = "dependency"
    AI_ENHANCED = "ai_enhanced"


class QualityMode(Enum):
    """Available quality modes"""

    FAST = "fast"
    COMPREHENSIVE = "comprehensive"
    AI_ENHANCED = "ai_enhanced"
    SMART = "smart"


class ToolResult(pydantic.BaseModel):
    """Results from running a quality tool"""

    success: bool
    issues_found: int
    issues_fixed: int
    files_analyzed: List[str]
    files_modified: List[str]
    error_message: Optional[str] = None
    logs: List[str] = []
    tool_name: str
    tool_category: ToolCategory
    execution_time_ms: int


class QualityToolConfig(pydantic.BaseModel):
    """Base configuration for quality tools"""

    enabled: bool = True
    modes: Set[QualityMode] = {QualityMode.COMPREHENSIVE, QualityMode.SMART}
    auto_fix: bool = True
    max_issues: Optional[int] = None
    timeout_seconds: int = 60
    exclude_patterns: List[str] = []
    include_patterns: List[str] = []


class QualityTool(abc.ABC):
    """Base class for all quality tools"""

    def __init__(self, config: Optional[QualityToolConfig] = None):
        self.config = config or QualityToolConfig()
        self.logger = get_logger(self.__class__.__name__)

    @property
    @abc.abstractmethod
    def name(self) -> str:
        """Return the name of the tool"""
        pass

    @property
    @abc.abstractmethod
    def category(self) -> ToolCategory:
        """Return the category of the tool"""
        pass

    @property
    def modes(self) -> Set[QualityMode]:
        """Return the modes this tool supports"""
        return self.config.modes

    def supports_mode(self, mode: QualityMode) -> bool:
        """Check if the tool supports a specific mode"""
        return mode in self.modes

    @abc.abstractmethod
    async def check(self, files: Optional[List[str]] = None) -> ToolResult:
        """Run the tool in check-only mode"""
        pass

    @abc.abstractmethod
    async def fix(self, files: Optional[List[str]] = None) -> ToolResult:
        """Run the tool in fix mode"""
        pass

    async def run(
        self, files: Optional[List[str]] = None, auto_fix: Optional[bool] = None
    ) -> ToolResult:
        """Run the tool based on configuration"""
        should_fix = self.config.auto_fix if auto_fix is None else auto_fix

        try:
            if should_fix:
                return await self.fix(files)
            else:
                return await self.check(files)
        except Exception as e:
            self.logger.exception(f"Error running {self.name}", exc_info=e)
            return ToolResult(
                success=False,
                issues_found=0,
                issues_fixed=0,
                files_analyzed=[],
                files_modified=[],
                error_message=str(e),
                logs=[f"Exception: {str(e)}"],
                tool_name=self.name,
                tool_category=self.category,
                execution_time_ms=0,
            )

    def filter_files(self, files: List[str]) -> List[str]:
        """Filter files based on include/exclude patterns"""
        # This is a simplified implementation - in a real system,
        # you would use proper glob pattern matching
        if not files:
            return []

        result = files.copy()

        # Apply exclusions
        for pattern in self.config.exclude_patterns:
            result = [f for f in result if pattern not in f]

        # Apply inclusions if specified
        if self.config.include_patterns:
            result = [
                f for f in result if any(pattern in f for pattern in self.config.include_patterns)
            ]

        return result
