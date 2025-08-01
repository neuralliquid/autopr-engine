import asyncio
import os
import re
from typing import Any, Dict, List

from .tool_base import Tool


class InterrogateTool(Tool):
    """
    A tool for checking Python docstring coverage using Interrogate.
    """

    @property
    def name(self) -> str:
        return "interrogate"

    @property
    def description(self) -> str:
        return "A tool for checking Python docstring coverage."

    async def run(self, files: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Run Interrogate on a list of files.
        """
        if not files:
            return []

        # Interrogate is best run on directories. We'll find the unique directories
        # from the file list and run Interrogate on them.
        directories = sorted(list(set(os.path.dirname(f) for f in files if os.path.dirname(f))))
        if not directories:
            # Handle case where all files are in the root directory
            if any(os.path.dirname(f) == "" for f in files):
                directories = ["."]
            else:
                return []

        command = ["interrogate", "-v", *directories]

        fail_under = config.get("fail_under", 80)
        command.extend(["--fail-under", str(fail_under)])

        extra_args = config.get("args", [])
        command.extend(extra_args)

        process = await asyncio.create_subprocess_exec(
            *command, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        # Interrogate returns 0 for success, 2 for issues found.
        if process.returncode not in [0, 2]:
            error_message = stderr.decode().strip()
            if not error_message and stdout:
                error_message = stdout.decode().strip()
            print(f"Error running interrogate: {error_message}")
            return [{"error": f"Interrogate execution failed: {error_message}"}]

        if not stdout:
            return []

        output = stdout.decode()
        return self._parse_output(output, files)

    def _parse_output(self, output: str, files_to_check: List[str]) -> List[Dict[str, Any]]:
        """
        Parses the verbose text output of Interrogate.
        Example: FAILED: autopr/my_module.py:10 - C001 - Missing docstring for public function `my_func`
        """
        issues = []
        pattern = re.compile(
            r"^FAILED: (?P<file>[^:]+):(?P<line>\d+) - (?P<code>\w+) - (?P<message>.+)$"
        )

        for line in output.strip().split("\n"):
            match = pattern.match(line.strip())
            if match:
                issue_data = match.groupdict()
                # Only report issues for the files we were asked to check
                if issue_data["file"] in files_to_check:
                    issues.append(
                        {
                            "filename": issue_data["file"],
                            "line_number": int(issue_data["line"]),
                            "code": issue_data["code"],
                            "message": issue_data["message"].strip(),
                        }
                    )
        return issues
