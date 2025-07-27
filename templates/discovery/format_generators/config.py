#!/usr/bin/env python3
"""
Documentation Configuration Module
=================================

Configuration classes for documentation generation.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class DocumentationConfig:
    """Configuration for documentation generation."""

    output_format: str = "markdown"  # markdown, html, json
    include_examples: bool = True
    include_code_snippets: bool = True
    include_troubleshooting: bool = True
    include_best_practices: bool = True
    generate_index: bool = True
    custom_css: Optional[str] = None
