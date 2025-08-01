# Quality Engine: Generic Tool Architecture

## 🧩 Generic Tool Class Hierarchy

```
┌─────────────────────────────────────────────┐
│ Tool[TConfig, TIssue]                       │ (Generic Abstract Base Class)
├─────────────────────────────────────────────┤
│ + name: str                                 │
│ + description: str                          │
│ + category: str                             │
│ + run(files: List[str],                     │
│       config: TConfig) → Awaitable[List[TIssue]] │
└─────────────────────────────────────────────┘
                    ▲
                    │
        ┌───────────────────────┐
        │                       │
┌───────────────┐      ┌─────────────────┐
│ ESLintTool    │      │ MyPyTool        │
├───────────────┤      ├─────────────────┤
│ Tool[ESLintConfig,   │ Tool[MyPyConfig,│
│      LintIssue]│      │      LintIssue] │
└───────────────┘      └─────────────────┘
```

## 💡 Design Goal

The quality engine architecture uses generics and TypedDict to create a flexible, type-safe system
for running different code analysis tools. This design:

1. Provides type safety across the entire toolchain
2. Enables polymorphic tool usage
3. Maintains consistent result structures
4. Allows for tool discovery and categorization

## 📦 Core Components

### 1. Tool Base Class

The `Tool` abstract base class provides a generic interface that all tools must implement:

```python
class Tool(ABC, Generic[TConfig, TIssue]):
    @property @abstractmethod
    def name(self) -> str: ...

    @property @abstractmethod
    def description(self) -> str: ...

    @property
    def category(self) -> str:
        return "general"

    @abstractmethod
    async def run(self, files: List[str], config: TConfig) -> List[TIssue]: ...
```

### 2. Type-Safe Configuration

Each tool defines its configuration using TypedDict:

```python
class MyPyConfig(TypedDict, total=False):
    args: List[str]
```

### 3. Standardized Results

Results are represented with TypedDict for consistent access patterns:

```python
class LintIssue(TypedDict):
    filename: str
    line_number: int
    column_number: int
    message: str
    code: str
    level: str
```

### 4. Tool Registry

The registry pattern provides runtime discovery of tools:

```python
# Register a tool
@register_tool
class MyPyTool(Tool[MyPyConfig, LintIssue]): ...

# Get tools by category
lint_tools = registry.get_tools_by_category("linting")
```

## 🔄 Workflow

1. **Tool Implementation**: Create concrete tool classes that implement the generic `Tool` interface
2. **Registration**: Automatically register tools using the `@register_tool` decorator
3. **Configuration**: Define typed configurations specific to each tool
4. **Result Standardization**: Return consistently structured results
5. **Discovery**: Query the registry to find tools by name, category, or issue type

## 🧠 Advanced Usage

You can extend this architecture with:

1. **Handlers**: Create dedicated handlers for processing specific issue types
2. **Pipelines**: Chain tools together for comprehensive analysis
3. **Filters**: Add filtering capabilities to focus on specific file types or issues
4. **Parallel Execution**: Run tools concurrently for performance
5. **Result Aggregation**: Combine results from multiple tools into unified reports

## 📚 Implementation Example

Here's how our MyPyTool is implemented:

```python
@register_tool
class MyPyTool(Tool[MyPyConfig, LintIssue]):
    """A tool for running MyPy, a static type checker for Python."""

    @property
    def name(self) -> str:
        return "mypy"

    @property
    def description(self) -> str:
        return "A static type checker for Python."

    @property
    def category(self) -> str:
        return "linting"

    async def run(self, files: List[str], config: MyPyConfig) -> List[LintIssue]:
        # Implementation details...
```

This architecture provides a robust foundation for a quality engine that can integrate with various
static analysis tools while maintaining type safety and modularity.
