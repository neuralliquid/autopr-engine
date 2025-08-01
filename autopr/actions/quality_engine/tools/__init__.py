import importlib
import pkgutil
from typing import List, Type

from .tool_base import Tool


def discover_tools() -> List[Type[Tool]]:
    """Dynamically discover and import all tools in this directory."""

    tools = []

    for _, name, _ in pkgutil.iter_modules(__path__):
        module = importlib.import_module(f".{name}", __package__)
        for item_name in dir(module):
            item = getattr(module, item_name)
            if isinstance(item, type) and issubclass(item, Tool) and item is not Tool:
                tools.append(item)

    return tools
