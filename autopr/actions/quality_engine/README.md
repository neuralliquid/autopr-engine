# AutoPR Quality Engine

A comprehensive, cross-platform code quality analysis engine with AI-enhanced capabilities and
Windows compatibility.

## Features

- **Cross-Platform Support**: Works on Windows, Linux, and macOS with automatic platform detection
- **Comprehensive Tool Integration**: Integrates multiple quality analysis tools
- **AI-Enhanced Analysis**: Optional AI-powered code review and suggestions
- **Windows Adaptations**: Automatic tool substitutions and alternatives for Windows compatibility
- **Extensible Architecture**: Easy to add new tools and analysis capabilities

## Directory Structure

```
quality_engine/
├── __init__.py                 # Main package initialization
├── engine.py                   # Core quality engine implementation
├── cli.py                      # Command-line interface
├── models.py                   # Data models and enums
├── config.py                   # Configuration management
├── platform_detector.py        # Platform detection and adaptations
├── tool_runner.py              # Tool execution and result processing
├── summary.py                  # Result summarization
├── di.py                       # Dependency injection container
├── handler_registry.py         # Result handler management
├── handler_base.py             # Base handler classes
├── result_wrapper.py           # Result wrapping utilities
├── example_usage.py            # Usage examples
├── README.md                   # This file
│
├── tools/                      # Quality analysis tools
│   ├── __init__.py            # Tool discovery and registration
│   ├── tool_base.py           # Base tool interface
│   ├── registry.py            # Tool registry
│   ├── ruff_tool.py           # Python linting and formatting
│   ├── mypy_tool.py           # Python type checking
│   ├── bandit_tool.py         # Python security scanning
│   ├── semgrep_tool.py        # Cross-platform static analysis (NEW)
│   ├── interrogate_tool.py    # Python docstring coverage
│   ├── pytest_tool.py         # Python testing
│   ├── radon_tool.py          # Python complexity analysis
│   ├── codeql_tool.py         # GitHub CodeQL (Linux/macOS)
│   ├── windows_security_tool.py # Windows security scanner
│   ├── eslint_tool.py         # JavaScript/TypeScript linting
│   ├── sonarqube_tool.py      # SonarQube integration
│   ├── dependency_scanner_tool.py # Dependency analysis
│   └── performance_analyzer_tool.py # Performance analysis
│
├── handlers/                   # Result handlers
│   ├── __init__.py            # Handler discovery
│   ├── base.py                # Base handler classes
│   └── ...                    # Specific handlers
│
├── ai/                        # AI-enhanced analysis
│   ├── ai_modes.py            # AI analysis modes
│   ├── ai_analyzer.py         # AI code analyzer
│   └── ai_handler.py          # AI result handling
│
└── __tests__/                 # Test files
    └── test_*.py              # Unit tests
```

## Available Tools

### Cross-Platform Tools (Recommended)

- **Semgrep**: Comprehensive static analysis for security and code quality
- **Ruff**: Fast Python linting and formatting
- **Bandit**: Python security vulnerability scanning
- **Safety**: Dependency vulnerability scanning
- **MyPy**: Python type checking
- **Pytest**: Python testing framework

### Platform-Specific Tools

- **CodeQL**: Advanced security analysis (Linux/macOS only)
- **Windows Security Tool**: Comprehensive Windows security scanner
- **ESLint**: JavaScript/TypeScript linting
- **SonarQube**: Enterprise code quality analysis

### Analysis Tools

- **Interrogate**: Python docstring coverage
- **Radon**: Python code complexity analysis
- **Dependency Scanner**: Package dependency analysis
- **Performance Analyzer**: Code performance analysis

## Windows Compatibility

The Quality Engine automatically detects Windows and provides:

1. **Tool Substitutions**: CodeQL → Semgrep (recommended cross-platform alternative)
2. **Windows Security Tool**: Comprehensive security scanning for Windows
3. **Platform Warnings**: Clear information about limitations and alternatives
4. **User Confirmation**: Optional confirmation before running on Windows

## Usage

### Command Line Interface

```bash
# Basic usage
python -m autopr.actions.quality_engine.cli --files <files> --mode fast

# Windows mode (with confirmation)
python -m autopr.actions.quality_engine.cli --files <files> --mode comprehensive

# Skip Windows check
python -m autopr.actions.quality_engine.cli --files <files> --skip-windows-check

# AI-enhanced analysis
python -m autopr.actions.quality_engine.cli --files <files> --mode ai_enhanced --enable-ai
```

### Available Modes

- **fast**: Quick analysis with essential tools (Ruff, Bandit)
- **smart**: Intelligent tool selection based on file types
- **comprehensive**: Full analysis with all available tools
- **ai_enhanced**: AI-powered analysis with code suggestions

### Programmatic Usage

```python
from autopr.actions.quality_engine.engine import QualityEngine
from autopr.actions.quality_engine.models import QualityInputs, QualityMode

# Create engine
engine = QualityEngine()

# Run analysis
inputs = QualityInputs(
    mode=QualityMode.COMPREHENSIVE,
    files=["src/"],
    enable_ai_agents=True
)

result = await engine.run(inputs)
print(f"Found {result.total_issues_found} issues")
```

## Configuration

The engine can be configured via `pyproject.toml`:

```toml
[tool.autopr.quality_engine]
default_mode = "smart"
enable_ai = false

[tool.autopr.quality_engine.tools]
ruff = { enabled = true, config = {} }
semgrep = { enabled = true, rules = "auto", severity = "INFO,WARNING,ERROR" }
bandit = { enabled = true, config = {} }
```

## Adding New Tools

To add a new quality analysis tool:

1. Create a new tool class in `tools/` directory
2. Inherit from `Tool` base class
3. Implement required methods (`name`, `description`, `run`)
4. Register the tool in `tools/__init__.py`

Example:

```python
from .tool_base import Tool

class MyCustomTool(Tool):
    @property
    def name(self) -> str:
        return "my_custom_tool"

    @property
    def description(self) -> str:
        return "My custom quality analysis tool"

    async def run(self, files: List[str], config: Dict[str, Any]) -> List[Dict[str, Any]]:
        # Implement tool logic here
        return []
```

## Contributing

1. Follow the existing code structure and patterns
2. Add appropriate tests for new tools
3. Update documentation for new features
4. Ensure cross-platform compatibility
5. Add Windows adaptations if needed

## License

Part of the AutoPR project. See main project license.
