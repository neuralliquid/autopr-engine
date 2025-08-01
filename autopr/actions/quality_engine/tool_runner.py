"""
Tool runner for quality engine - handles running tools and processing results
"""

import time
from typing import Any, Dict, List, Optional

import structlog

from .models import ToolResult

logger = structlog.get_logger(__name__)


async def run_tool(
    tool_name: str,
    tool_instance: Any,
    files: List[str],
    tool_config: Dict[str, Any],
    handler_registry: Optional[Any] = None,
) -> Optional[ToolResult]:
    """Run a quality tool with timing and error handling."""
    try:
        start_time = time.time()
        logger.info("Running tool", tool=tool_name, file_count=len(files))

        results = await tool_instance.run(files=files, config=tool_config)

        # If we have a handler registry, process the results with the appropriate handler
        if handler_registry is not None and hasattr(tool_instance, "result_type"):
            result_type = tool_instance.result_type
            try:
                handler_registry.handle_results(results.get("issues", []), result_type)
            except Exception as handler_error:
                logger.warning(
                    "Error handling tool results", tool=tool_name, error=str(handler_error)
                )

        execution_time = time.time() - start_time
        logger.info(
            "Tool completed",
            tool=tool_name,
            issues_found=len(results.get("issues", [])),
            execution_time=f"{execution_time:.2f}s",
        )

        return ToolResult(
            issues=results.get("issues", []),
            files_with_issues=results.get("files_with_issues", []),
            summary=results.get("summary", f"Completed {tool_name} analysis"),
            execution_time=execution_time,
        )

    except Exception as e:
        logger.error("Error running tool", tool=tool_name, error=str(e))
        return None


def determine_smart_tools(files: list[str]) -> list[str]:
    """Select tools dynamically based on file context."""
    tools = set()

    for file in files:
        if file.endswith(".py"):
            # Python files get standard Python tools
            tools.update(["ruff", "mypy", "bandit", "pytest"])

            # Add documentation checking for Python files
            tools.add("interrogate")

            # Add complexity analysis for Python files
            tools.add("radon")

        elif file.endswith((".js", ".ts", ".jsx", ".tsx")):
            # JavaScript/TypeScript files would get JS-specific tools
            # These would be added as plugins
            pass

        elif file.endswith((".yml", ".yaml")):
            # YAML files might need specific validation
            pass

        elif file.endswith(".md"):
            # Markdown files get documentation tools
            tools.add("interrogate")

    # Add security scanning for all code files
    if any(file.endswith((".py", ".js", ".ts", ".jsx", ".tsx", ".java", ".go")) for file in files):
        tools.add("bandit")
        tools.add("codeql")

    # Run SonarQube on larger sets of files for more comprehensive analysis
    if len(files) > 5:
        tools.add("sonarqube")

    return list(tools)
