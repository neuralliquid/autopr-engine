#!/usr/bin/env python3
"""
Format Generators Package
=========================

Modular format generators for documentation generation.
Provides specialized generators for different output formats (Markdown, HTML, JSON).
"""

# Core components
from .config import DocumentationConfig
from .base import BaseFormatGenerator

# Format generators
from .markdown import MarkdownGenerator
from .html import HTMLGenerator
from .json_generator import JSONGenerator

# Factory and utilities
from .factory import (
    FormatGeneratorFactory,
    generate_platform_guide,
    generate_documentation_index
)

# Main exports
__all__ = [
    # Configuration
    'DocumentationConfig',
    
    # Base class
    'BaseFormatGenerator',
    
    # Format generators
    'MarkdownGenerator',
    'HTMLGenerator', 
    'JSONGenerator',
    
    # Factory and utilities
    'FormatGeneratorFactory',
    'generate_platform_guide',
    'generate_documentation_index',
]

# Version and metadata
__version__ = '1.0.0'
__author__ = 'AutoPR Engine'
__description__ = 'Modular format generators for documentation generation'
