#!/usr/bin/env python3
"""
AutoPR Engine - AI-Powered GitHub PR Automation and Issue Management
Setup configuration for Python packaging and distribution
"""

import os
import re
from pathlib import Path
from typing import List

from setuptools import find_packages, setup


# Get version from __init__.py
def get_version() -> str:
    init_file = Path(__file__).parent / "autopr" / "__init__.py"
    if init_file.exists():
        with open(init_file, "r", encoding="utf-8") as f:
            content = f.read()
            match = re.search(r'__version__ = ["\']([^"\']+)["\']', content)
            if match:
                return match.group(1)
    return "1.0.0"


# Read long description from README
def get_long_description() -> str:
    readme_file = Path(__file__).parent / "README.md"
    if readme_file.exists():
        with open(readme_file, "r", encoding="utf-8") as f:
            return f.read()
    return "AI-Powered GitHub PR Automation and Issue Management"


# Read requirements from requirements.txt
def get_requirements() -> List[str]:
    requirements_file = Path(__file__).parent / "requirements.txt"
    if requirements_file.exists():
        with open(requirements_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


# Read development requirements
def get_dev_requirements() -> List[str]:
    dev_requirements_file = Path(__file__).parent / "requirements-dev.txt"
    if dev_requirements_file.exists():
        with open(dev_requirements_file, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip() and not line.startswith("#")]
    return []


setup(
    # Basic package information
    name="autopr-engine",
    version=get_version(),
    description="AI-Powered GitHub PR Automation and Issue Management",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    # Author and maintainer information
    author="neuralliquid Team",
    author_email="dev@neuralliquid.net",
    maintainer="neuralliquid Team",
    maintainer_email="dev@neuralliquid.net",
    # URLs and project information
    url="https://github.com/neuralliquid/autopr-engine",
    project_urls={
        "Homepage": "https://github.com/neuralliquid/autopr-engine",
        "Documentation": "https://autopr-engine.readthedocs.io",
        "Repository": "https://github.com/neuralliquid/autopr-engine",
        "Bug Tracker": "https://github.com/neuralliquid/autopr-engine/issues",
        "Changelog": "https://github.com/neuralliquid/autopr-engine/blob/main/CHANGELOG.md",
        "Discussions": "https://github.com/neuralliquid/autopr-engine/discussions",
    },
    # Package discovery and inclusion
    packages=find_packages(exclude=["tests*", "docs*", "examples*"]),
    package_data={
        "autopr": [
            "workflows/*.yaml",
            "workflows/*.yml",
            "config/*.yaml",
            "config/*.yml",
            "templates/*.j2",
            "templates/*.jinja",
            "static/*",
        ],
    },
    include_package_data=True,
    # Python version and classifiers
    python_requires=">=3.9",
    classifiers=[
        # Development Status
        "Development Status :: 4 - Beta",
        # Intended Audience
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        # License
        "License :: OSI Approved :: MIT License",
        # Programming Language
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: Implementation :: CPython",
        # Operating System
        "Operating System :: OS Independent",
        "Operating System :: POSIX",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS",
        # Topic Classification
        "Topic :: Software Development",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Software Development :: Quality Assurance",
        "Topic :: Software Development :: Version Control :: Git",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: System :: Software Distribution",
        "Topic :: Utilities",
        # Natural Language
        "Natural Language :: English",
        # Environment
        "Environment :: Console",
        "Environment :: Web Environment",
    ],
    # Keywords for PyPI search
    keywords=[
        "github",
        "pull-request",
        "automation",
        "ai",
        "code-review",
        "ci-cd",
        "workflow",
        "integration",
        "slack",
        "linear",
        "autogen",
        "llm",
        "openai",
        "anthropic",
        "issue-management",
        "quality-gates",
        "platform-detection",
        "multi-agent",
    ],
    # Dependencies
    install_requires=[
        # Core dependencies
        "pydantic>=2.0.0,<3.0.0",
        "aiohttp>=3.8.0,<4.0.0",
        "structlog>=22.0.0,<24.0.0",
        "click>=8.0.0,<9.0.0",
        "pyyaml>=6.0.0,<7.0.0",
        "jinja2>=3.1.0,<4.0.0",
        # GitHub integration
        "pygithub>=1.58.0,<2.0.0",
        "GitPython>=3.1.0,<4.0.0",
        # AI and LLM providers
        "openai>=1.0.0,<2.0.0",
        "anthropic>=0.25.0,<1.0.0",
        "mistralai>=1.0.0,<2.0.0",
        # HTTP and networking
        "httpx>=0.24.0,<1.0.0",
        "websockets>=11.0.0,<12.0.0",
        # Data processing
        "python-dateutil>=2.8.0,<3.0.0",
        "pytz>=2023.3",
        # Configuration and environment
        "python-dotenv>=1.0.0,<2.0.0",
        "toml>=0.10.0,<1.0.0",
    ],
    # Optional dependencies for different features
    extras_require={
        # Development dependencies
        "dev": [
            "pytest>=7.4.0,<8.0.0",
            "pytest-asyncio>=0.21.0,<1.0.0",
            "pytest-cov>=4.1.0,<5.0.0",
            "pytest-mock>=3.11.0,<4.0.0",
            "black>=23.7.0,<24.0.0",
            "isort>=5.12.0,<6.0.0",
            "flake8>=6.0.0,<7.0.0",
            "mypy>=1.5.0,<2.0.0",
            "pre-commit>=3.4.0,<4.0.0",
            "sphinx>=7.1.0,<8.0.0",
            "sphinx-rtd-theme>=1.3.0,<2.0.0",
        ],
        # Monitoring and observability
        "monitoring": [
            "prometheus_client>=0.17.0,<1.0.0",
            "sentry-sdk[fastapi]>=1.32.0,<2.0.0",
            "datadog>=0.47.0,<1.0.0",
        ],
        # Memory and learning systems
        "memory": [
            "mem0ai>=0.1.0,<1.0.0",
            "chromadb>=0.4.0,<1.0.0",
            "qdrant-client>=1.5.0,<2.0.0",
        ],
        # Advanced AI features
        "ai": [
            "pyautogen>=0.2.0,<1.0.0",
            "langchain>=0.0.300,<1.0.0",
            "langchain-openai>=0.0.5,<1.0.0",
            "langchain-anthropic>=0.1.0,<1.0.0",
        ],
        # Database and caching
        "database": [
            "asyncpg>=0.28.0,<1.0.0",
            "sqlalchemy[asyncio]>=2.0.0,<3.0.0",
            "alembic>=1.12.0,<2.0.0",
            "redis>=4.6.0,<5.0.0",
            "aioredis>=2.0.0,<3.0.0",
        ],
        # Web server and API
        "server": [
            "fastapi>=0.103.0,<1.0.0",
            "uvicorn[standard]>=0.23.0,<1.0.0",
            "gunicorn>=21.2.0,<22.0.0",
        ],
        # Resilience and reliability
        "resilience": [
            "pybreaker>=1.0.0,<2.0.0",
            "tenacity>=8.2.0,<9.0.0",
            "limits>=3.6.0,<4.0.0",
        ],
        # Full installation with all optional features
        "full": ["autopr-engine[dev,monitoring,memory,ai,database,server,resilience]"],
    },
    # Console scripts and entry points
    entry_points={
        "console_scripts": [
            "autopr=autopr.cli:main",
            "autopr-server=autopr.server:main",
            "autopr-worker=autopr.worker:main",
            "autopr-migration=autopr.migration:main",
        ],
        "autopr.actions": [
            "platform_detector=autopr.actions.platform_detector:PlatformDetector",
            "pr_review_analyzer=autopr.actions.pr_review_analyzer:PRReviewAnalyzer",
            "issue_creator=autopr.actions.issue_creator:IssueCreator",
            "ai_comment_analyzer=autopr.actions.ai_comment_analyzer:AICommentAnalyzer",
            "quality_gates=autopr.actions.quality_gates:QualityGates",
            "autogen_multi_agent=autopr.actions.autogen_multi_agent:AutoGenMultiAgent",
        ],
        "autopr.integrations": [
            "github=autopr.integrations.github:GitHubIntegration",
            "linear=autopr.integrations.linear:LinearIntegration",
            "slack=autopr.integrations.slack:SlackIntegration",
            "axolo=autopr.integrations.axolo:AxoloIntegration",
        ],
        "autopr.llm_providers": [
            "openai=autopr.ai.providers.openai:OpenAIProvider",
            "anthropic=autopr.ai.providers.anthropic:AnthropicProvider",
            "mistral=autopr.ai.providers.mistral:MistralProvider",
            "groq=autopr.ai.providers.groq:GroqProvider",
        ],
    },
    # Test suite configuration
    test_suite="tests",
    # Zip safety
    zip_safe=False,
    # Platform compatibility
    platforms=["any"],
)
