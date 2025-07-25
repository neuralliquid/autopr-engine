"""
File Analysis Module

Handles file system scanning and content analysis for platform detection.
"""

import json
import os
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple


class FileAnalyzer:
    """Analyzes file system for platform-specific indicators."""

    def __init__(self, workspace_path: str = "."):
        self.workspace_path = Path(workspace_path)

    def scan_for_platform_files(
        self, platform_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Scan workspace for platform-specific files."""
        found_files = {}

        for platform, config in platform_configs.items():
            platform_files = []

            for file_pattern in config.get("files", []):
                matches = self._find_files_by_pattern(file_pattern)
                platform_files.extend(matches)

            if platform_files:
                found_files[platform] = platform_files

        return found_files

    def scan_for_folder_patterns(
        self, platform_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, List[str]]:
        """Scan workspace for platform-specific folder patterns."""
        found_folders = {}

        for platform, config in platform_configs.items():
            platform_folders = []

            for folder_pattern in config.get("folder_patterns", []):
                matches = self._find_folders_by_pattern(folder_pattern)
                platform_folders.extend(matches)

            if platform_folders:
                found_folders[platform] = platform_folders

        return found_folders

    def analyze_package_json(self) -> Dict[str, Any]:
        """Analyze package.json for platform indicators."""
        package_json_path = self.workspace_path / "package.json"

        if not package_json_path.exists():
            return {}

        try:
            with open(package_json_path, "r", encoding="utf-8") as f:
                package_data = json.load(f)

            return {
                "dependencies": package_data.get("dependencies", {}),
                "devDependencies": package_data.get("devDependencies", {}),
                "scripts": package_data.get("scripts", {}),
                "name": package_data.get("name", ""),
                "description": package_data.get("description", ""),
            }
        except (json.JSONDecodeError, IOError):
            return {}

    def analyze_requirements_txt(self) -> List[str]:
        """Analyze requirements.txt for Python dependencies."""
        requirements_path = self.workspace_path / "requirements.txt"

        if not requirements_path.exists():
            return []

        try:
            with open(requirements_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            dependencies = []
            for line in lines:
                line = line.strip()
                if line and not line.startswith("#"):
                    # Extract package name (before version specifiers)
                    package_name = re.split(r"[>=<!=]", line)[0].strip()
                    dependencies.append(package_name)

            return dependencies
        except IOError:
            return []

    def analyze_dockerfile(self) -> Dict[str, Any]:
        """Analyze Dockerfile for platform indicators."""
        dockerfile_path = self.workspace_path / "Dockerfile"

        if not dockerfile_path.exists():
            return {}

        try:
            with open(dockerfile_path, "r", encoding="utf-8") as f:
                content = f.read()

            analysis = {
                "base_images": self._extract_base_images(content),
                "exposed_ports": self._extract_exposed_ports(content),
                "environment_vars": self._extract_env_vars(content),
                "commands": self._extract_run_commands(content),
            }

            return analysis
        except IOError:
            return {}

    def scan_content_for_patterns(
        self, platform_configs: Dict[str, Dict[str, Any]]
    ) -> Dict[str, int]:
        """Scan file contents for platform-specific patterns."""
        pattern_matches = {}

        for platform, config in platform_configs.items():
            match_count = 0

            for pattern in config.get("content_patterns", []):
                matches = self._search_content_pattern(pattern)
                match_count += matches

            if match_count > 0:
                pattern_matches[platform] = match_count

        return pattern_matches

    def _find_files_by_pattern(self, pattern: str) -> List[str]:
        """Find files matching a specific pattern."""
        matches = []

        try:
            if "*" in pattern or "?" in pattern:
                # Use glob for wildcard patterns
                matches.extend([str(p) for p in self.workspace_path.glob(pattern)])
            else:
                # Direct file check
                file_path = self.workspace_path / pattern
                if file_path.exists():
                    matches.append(str(file_path))
        except Exception:
            pass

        return matches

    def _find_folders_by_pattern(self, pattern: str) -> List[str]:
        """Find folders matching a specific pattern."""
        matches = []

        try:
            if "*" in pattern or "?" in pattern:
                # Use glob for wildcard patterns
                matches.extend([str(p) for p in self.workspace_path.glob(pattern) if p.is_dir()])
            else:
                # Direct folder check
                folder_path = self.workspace_path / pattern
                if folder_path.exists() and folder_path.is_dir():
                    matches.append(str(folder_path))
        except Exception:
            pass

        return matches

    def _search_content_pattern(self, pattern: str) -> int:
        """Search for pattern in file contents."""
        match_count = 0

        try:
            for file_path in self.workspace_path.rglob("*"):
                if file_path.is_file() and self._is_text_file(file_path):
                    try:
                        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
                            content = f.read()
                            match_count += len(re.findall(pattern, content, re.IGNORECASE))
                    except Exception:
                        continue
        except Exception:
            pass

        return match_count

    def _is_text_file(self, file_path: Path) -> bool:
        """Check if file is likely a text file."""
        text_extensions = {
            ".txt",
            ".md",
            ".json",
            ".yml",
            ".yaml",
            ".toml",
            ".ini",
            ".py",
            ".js",
            ".ts",
            ".jsx",
            ".tsx",
            ".html",
            ".css",
            ".scss",
            ".php",
            ".rb",
            ".go",
            ".rs",
            ".java",
            ".c",
            ".cpp",
            ".h",
            ".sh",
            ".bat",
            ".ps1",
            ".dockerfile",
            ".gitignore",
        }

        return file_path.suffix.lower() in text_extensions or file_path.name.lower() in {
            "dockerfile",
            "makefile",
            "readme",
        }

    def _extract_base_images(self, dockerfile_content: str) -> List[str]:
        """Extract base images from Dockerfile."""
        pattern = r"^FROM\s+([^\s]+)"
        matches = re.findall(pattern, dockerfile_content, re.MULTILINE | re.IGNORECASE)
        return matches

    def _extract_exposed_ports(self, dockerfile_content: str) -> List[str]:
        """Extract exposed ports from Dockerfile."""
        pattern = r"^EXPOSE\s+(.+)"
        matches = re.findall(pattern, dockerfile_content, re.MULTILINE | re.IGNORECASE)
        ports = []
        for match in matches:
            ports.extend(match.split())
        return ports

    def _extract_env_vars(self, dockerfile_content: str) -> List[str]:
        """Extract environment variables from Dockerfile."""
        pattern = r"^ENV\s+([^=\s]+)"
        matches = re.findall(pattern, dockerfile_content, re.MULTILINE | re.IGNORECASE)
        return matches

    def _extract_run_commands(self, dockerfile_content: str) -> List[str]:
        """Extract RUN commands from Dockerfile."""
        pattern = r"^RUN\s+(.+)"
        matches = re.findall(pattern, dockerfile_content, re.MULTILINE | re.IGNORECASE)
        return matches
