from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, TypedDict, TypeVar

# Change the bound to Any to allow TypedDict
TConfig = TypeVar("TConfig", bound=Any)
TIssue = TypeVar("TIssue")


class Tool(ABC, Generic[TConfig, TIssue]):
    """Abstract base class for quality tools."""

    @property
    @abstractmethod
    def name(self) -> str:
        """The name of the tool."""
        pass

    @property
    @abstractmethod
    def description(self) -> str:
        """A brief description of what the tool does."""
        pass

    @property
    def category(self) -> str:
        """The category of the tool (e.g., 'linting', 'security', etc.)."""
        return "general"

    @abstractmethod
    async def run(self, files: List[str], config: TConfig) -> List[TIssue]:
        """
        Run the tool on a list of files.

        Args:
            files: The list of files to process.
            config: The configuration for the tool.

        Returns:
            A list of issues found by the tool.
        """
        pass
