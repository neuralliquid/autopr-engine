"""
Platform Configuration Module

Centralized platform definitions and configurations for detection.
"""

from typing import Any, Dict, List


class PlatformConfig:
    """Centralized platform configuration definitions."""

    @staticmethod
    def get_core_platforms() -> Dict[str, Dict[str, Any]]:
        """Get core rapid prototyping platform configurations."""
        return {
            "replit": {
                "files": [".replit", "replit.nix", "pyproject.toml", ".replit.json"],
                "package_scripts": ["repl-run", "replit-dev", "repl-dev"],
                "commit_patterns": [
                    "replit",
                    "exported from replit",
                    "repl.it",
                    "from replit",
                ],
                "dependencies": ["@replit/database", "replit-py"],
                "folder_patterns": [".replit_modules", "replit_modules"],
                "content_patterns": ["replit.com", "repl.co"],
            },
            "lovable": {
                "files": ["lovable.config.js", ".lovable", "lovable.json"],
                "package_scripts": ["lovable-dev", "lovable-build", "lovable-deploy"],
                "commit_patterns": ["lovable", "from lovable", "lovable.dev"],
                "dependencies": ["@lovable/cli", "@lovable/components"],
                "folder_patterns": [".lovable", "lovable_modules"],
                "content_patterns": ["lovable.dev", "lovable.app"],
            },
            "bolt": {
                "files": ["bolt.config.js", ".bolt", "bolt.json"],
                "package_scripts": ["bolt-dev", "bolt-build", "bolt-deploy"],
                "commit_patterns": ["bolt", "from bolt", "bolt.new"],
                "dependencies": ["@bolt/cli", "@bolt/components"],
                "folder_patterns": [".bolt", "bolt_modules"],
                "content_patterns": ["bolt.new", "bolt.dev"],
            },
            "cursor": {
                "files": [".cursor", "cursor.config.json", ".cursorrules"],
                "package_scripts": ["cursor-dev", "cursor-build"],
                "commit_patterns": ["cursor", "from cursor", "cursor.sh"],
                "dependencies": ["@cursor/cli"],
                "folder_patterns": [".cursor", "cursor_modules"],
                "content_patterns": ["cursor.sh", "cursor.com"],
            },
            "v0": {
                "files": ["v0.config.js", ".v0", "v0.json"],
                "package_scripts": ["v0-dev", "v0-build", "v0-deploy"],
                "commit_patterns": ["v0", "from v0", "v0.dev"],
                "dependencies": ["@v0/cli", "@v0/components"],
                "folder_patterns": [".v0", "v0_modules"],
                "content_patterns": ["v0.dev", "vercel.com/v0"],
            },
        }

    @staticmethod
    def get_ai_platforms() -> Dict[str, Dict[str, Any]]:
        """Get AI-specific platform configurations."""
        return {
            "github_copilot": {
                "files": [".github/copilot.yml", "copilot.config.json"],
                "package_scripts": ["copilot-suggest", "copilot-complete"],
                "commit_patterns": ["copilot", "github copilot", "co-authored-by: github"],
                "dependencies": ["@github/copilot"],
                "folder_patterns": [".copilot"],
                "content_patterns": ["github.com/features/copilot"],
            },
            "codeium": {
                "files": [".codeium", "codeium.config.json"],
                "package_scripts": ["codeium-suggest"],
                "commit_patterns": ["codeium", "from codeium"],
                "dependencies": ["codeium"],
                "folder_patterns": [".codeium"],
                "content_patterns": ["codeium.com"],
            },
            "tabnine": {
                "files": [".tabnine", "tabnine.config.json"],
                "package_scripts": ["tabnine-suggest"],
                "commit_patterns": ["tabnine", "from tabnine"],
                "dependencies": ["tabnine"],
                "folder_patterns": [".tabnine"],
                "content_patterns": ["tabnine.com"],
            },
        }

    @staticmethod
    def get_cloud_platforms() -> Dict[str, Dict[str, Any]]:
        """Get cloud platform configurations."""
        return {
            "vercel": {
                "files": ["vercel.json", ".vercel", "now.json"],
                "package_scripts": ["vercel", "vercel-build", "vercel-dev"],
                "commit_patterns": ["vercel", "deployed to vercel"],
                "dependencies": ["vercel", "@vercel/node"],
                "folder_patterns": [".vercel"],
                "content_patterns": ["vercel.com", "vercel.app"],
            },
            "netlify": {
                "files": ["netlify.toml", ".netlify", "_redirects"],
                "package_scripts": ["netlify", "netlify-build", "netlify-dev"],
                "commit_patterns": ["netlify", "deployed to netlify"],
                "dependencies": ["netlify-cli", "@netlify/functions"],
                "folder_patterns": [".netlify"],
                "content_patterns": ["netlify.com", "netlify.app"],
            },
            "railway": {
                "files": ["railway.json", ".railway", "Procfile"],
                "package_scripts": ["railway", "railway-deploy"],
                "commit_patterns": ["railway", "deployed to railway"],
                "dependencies": ["@railway/cli"],
                "folder_patterns": [".railway"],
                "content_patterns": ["railway.app"],
            },
        }

    @staticmethod
    def get_all_platforms() -> Dict[str, Dict[str, Any]]:
        """Get all platform configurations combined."""
        platforms = {}
        platforms.update(PlatformConfig.get_core_platforms())
        platforms.update(PlatformConfig.get_ai_platforms())
        platforms.update(PlatformConfig.get_cloud_platforms())
        return platforms

    @staticmethod
    def get_platform_categories() -> Dict[str, List[str]]:
        """Get platform categories for classification."""
        return {
            "rapid_prototyping": list(PlatformConfig.get_core_platforms().keys()),
            "ai_assisted": list(PlatformConfig.get_ai_platforms().keys()),
            "cloud_deployment": list(PlatformConfig.get_cloud_platforms().keys()),
        }
