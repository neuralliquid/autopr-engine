import asyncio
import json
from typing import Any, Dict, List

from .tool_base import Tool


class PyTestTool(Tool):
    """
    A tool for running tests using the PyTest framework.
    """

    @property
    def name(self) -> str:
        return "pytest"

    @property
    def description(self) -> str:
        return "A tool for running tests using PyTest."

    async def run(self, files: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run PyTest on the specified files or directories.
        Requires the `pytest-json-report` plugin to be installed.
        """
        target_paths = files if files else ["."]

        command = ["pytest", "--json-report", "--json-report-file=none", *target_paths]

        extra_args = config.get("args", [])
        command.extend(extra_args)

        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode not in [0, 1, 5]:
            error_message = stderr.decode().strip()
            print(f"Error running pytest: {error_message}")
            return [{"error": f"PyTest execution failed: {error_message}"}]

        if not stdout:
            if process.returncode == 5:
                return []
            return [{"error": "PyTest produced no output."}]

        try:
            report = json.loads(stdout)
            return self._format_output(report)
        except json.JSONDecodeError:
            print(f"Failed to parse pytest json report: {stdout.decode()}")
            return [{"error": "Failed to parse pytest JSON report"}]

    def _format_output(self, report: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Formats the pytest-json-report into a standardized list of issues.
        We only report failed tests.
        """
        issues = []
        if not report.get("tests"):
            return []

        for test in report["tests"]:
            if test.get("outcome") == "failed":
                filename = test.get("nodeid").split("::")[0]
                lineno = None
                if test.get("call", {}).get("traceback"):
                    last_trace = test["call"]["traceback"][-1]
                    filename = last_trace.get("path", filename)
                    lineno = last_trace.get("lineno")

                issues.append(
                    {
                        "filename": filename,
                        "line_number": lineno,
                        "code": "PYTEST_FAILURE",
                        "message": f"Test failed: {test.get('nodeid')}",
                        "details": {
                            "outcome": test.get("outcome"),
                            "long_report": test.get("longrepr", ""),
                        },
                    }
                )
        return issues
