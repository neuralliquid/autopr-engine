"""
Quality Engine - Single entry point for all code quality operations
"""

import os
from typing import Any, Dict, List, Optional, Set, cast

import structlog

from ..base import Action
from .ai_handler import create_tool_result_from_ai_analysis, initialize_llm_manager, run_ai_analysis
from .config import ToolConfig, load_config
from .handler_registry import HandlerRegistry
from .models import QualityInputs, QualityMode, QualityOutputs, ToolResult
from .summary import build_comprehensive_summary
from .tool_runner import determine_smart_tools, run_tool
from .tools import discover_tools
from .tools.registry import ToolRegistry

logger = structlog.get_logger(__name__)


class QualityEngine(Action):
    """Engine for all code quality operations"""

    id = "quality_engine"

    def __init__(
        self,
        config_path: str = "pyproject.toml",
        tool_registry: Optional[ToolRegistry] = None,
        handler_registry: Optional[HandlerRegistry] = None,
        config: Optional[Any] = None,
    ):
        super().__init__(
            name="quality_engine",
            description="Engine for all code quality operations",
            version="1.0.0",
        )

        # Use injected registry or create a new one
        self.tool_registry = tool_registry
        if self.tool_registry is None:
            # Fallback to discover tools if not injected
            tools = discover_tools()
            self.tools = {tool().name: tool() for tool in tools}
        else:
            # Use the tool instances from the registry
            self.tools = {name: tool for name, tool in self.tool_registry._tools.items()}

        # Use injected handler registry or create a new one
        self.handler_registry = handler_registry

        # Use injected config or load from path
        self.config = config if config is not None else load_config(config_path)

        # LLM manager will be lazy-loaded when needed
        self.llm_manager = None

        logger.info(
            "Quality Engine initialized",
            discovered_tools=list(self.tools.keys()),
            default_mode=self.config.default_mode,
        )

    def _determine_tools_for_mode(self, mode: QualityMode, files: List[str]) -> List[str]:
        """Determine which tools to run based on the mode."""
        if mode == QualityMode.SMART:
            return determine_smart_tools(files)

        # For other modes, use the configuration
        return self.config.modes.get(mode.value, [])

    def _get_tool_config(self, tool_name: str) -> ToolConfig:
        """Get the tool configuration, ensuring it has the right structure."""
        raw_config = self.config.tools.get(tool_name, {})

        # If raw_config is already a ToolConfig instance, return it
        if isinstance(raw_config, ToolConfig):
            return raw_config

        # If raw_config is a dict, convert it to a ToolConfig
        if isinstance(raw_config, dict):
            return ToolConfig(**raw_config)

        # Otherwise create a default ToolConfig
        return ToolConfig()

    async def execute(self, inputs: QualityInputs, context: Dict[str, Any]) -> QualityOutputs:
        """Execute unified quality workflow"""
        logger.info("Executing Quality Engine", mode=inputs.mode.value)

        results = {}
        files_to_check = inputs.files or []

        if not files_to_check:
            logger.warning("No files provided to check")
            return QualityOutputs(
                success=False,
                total_issues_found=0,
                total_issues_fixed=0,
                files_modified=[],
                summary="No files provided to check.",
            )

        # Determine which tools to run based on mode
        tools_to_run = self._determine_tools_for_mode(inputs.mode, files_to_check)

        if not tools_to_run:
            logger.warning("No tools configured for mode", mode=inputs.mode.value)
            return QualityOutputs(
                success=True,
                total_issues_found=0,
                total_issues_fixed=0,
                files_modified=[],
                summary=f"No tools to run for mode: {inputs.mode.value}",
            )

        if inputs.mode == QualityMode.COMPREHENSIVE:
            logger.info("Running in comprehensive mode - using all available tools")
            # Get all enabled tools from config
            all_enabled_tools = []

            for tool_name in self.tools.keys():
                tool_config = self._get_tool_config(tool_name)
                if tool_config.enabled:
                    all_enabled_tools.append(tool_name)

            tools_to_run = list(set(tools_to_run) | set(all_enabled_tools))

            # Add detailed logging for comprehensive mode
            logger.info(
                "Comprehensive mode activated",
                tools=tools_to_run,
                file_count=len(files_to_check),
                file_types=list(set([os.path.splitext(f)[1] for f in files_to_check if "." in f])),
            )

        # Run tools in parallel for better performance
        tool_tasks = []
        for tool_name in tools_to_run:
            tool_instance = self.tools.get(tool_name)
            if not tool_instance:
                logger.warning("Tool not available", tool=tool_name)
                continue

            tool_config = self._get_tool_config(tool_name)

            if tool_config.enabled:
                task = run_tool(
                    tool_name=tool_name,
                    tool_instance=tool_instance,
                    files=files_to_check,
                    tool_config=tool_config.config,
                    handler_registry=self.handler_registry,
                )
                tool_tasks.append((tool_name, task))

        # Execute tools and gather results
        for tool_name, task in tool_tasks:
            tool_result = await task
            if tool_result:
                results[tool_name] = tool_result

        # Handle AI-enhanced mode
        ai_result = None
        ai_summary = None

        if inputs.mode == QualityMode.AI_ENHANCED and inputs.enable_ai_agents:
            # Lazy load the LLM manager if needed
            if not self.llm_manager:
                self.llm_manager = await initialize_llm_manager()

            if self.llm_manager:
                ai_result = await run_ai_analysis(
                    files_to_check,
                    self.llm_manager,
                    provider_name=inputs.ai_provider,
                    model=inputs.ai_model,
                )

                if ai_result:
                    results["ai_analysis"] = create_tool_result_from_ai_analysis(ai_result)
                    ai_summary = ai_result.get("summary")

        # Build the comprehensive summary
        summary = build_comprehensive_summary(results, ai_summary)

        # Collect issues and files by tool
        issues_by_tool = {tool_name: result.issues for tool_name, result in results.items()}
        files_by_tool = {
            tool_name: result.files_with_issues for tool_name, result in results.items()
        }

        # Get execution times by tool
        tool_execution_times = {
            tool_name: result.execution_time for tool_name, result in results.items()
        }

        # Calculate total issues
        total_issues_found = sum(len(result.issues) for result in results.values())

        # Get unique files with issues
        unique_files_with_issues = set()
        for result in results.values():
            unique_files_with_issues.update(result.files_with_issues)

        return QualityOutputs(
            success=total_issues_found == 0,
            total_issues_found=total_issues_found,
            total_issues_fixed=0,  # Placeholder for future fix implementation
            files_modified=[],  # Placeholder for future fix implementation
            issues_by_tool=issues_by_tool,
            files_by_tool=files_by_tool,
            tool_execution_times=tool_execution_times,
            summary=summary,
            ai_enhanced=inputs.mode == QualityMode.AI_ENHANCED and ai_result is not None,
            ai_summary=ai_summary,
        )

    async def run(self, inputs: QualityInputs) -> QualityOutputs:
        """Execute the quality engine with the given inputs"""
        # Create an empty context dictionary to satisfy the base class contract
        return await self.execute(inputs, {})


# Factory function to create a quality engine with dependencies
def create_engine(
    config_path: str = "pyproject.toml",
    tool_registry: Optional[ToolRegistry] = None,
    handler_registry: Optional[HandlerRegistry] = None,
    config: Optional[Any] = None,
) -> QualityEngine:
    """
    Create a QualityEngine instance with dependencies.

    This factory function allows for easy creation of QualityEngine instances
    with dependency injection support.

    Args:
        config_path: Path to configuration file
        tool_registry: Optional tool registry
        handler_registry: Optional handler registry
        config: Optional pre-loaded configuration

    Returns:
        Configured QualityEngine instance
    """
    return QualityEngine(
        config_path=config_path,
        tool_registry=tool_registry,
        handler_registry=handler_registry,
        config=config,
    )
