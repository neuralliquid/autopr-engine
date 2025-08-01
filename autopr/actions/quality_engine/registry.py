from typing import Any, Callable, Dict, List, Type, TypeVar

T = TypeVar("T")


class HandlerRegistry:
    def __init__(self):
        self._handlers: Dict[Type[Any], Callable[[List[Any]], None]] = {}

    def register(self, result_type: Type[T]):
        """
        Register a handler function for a specific result type.

        Args:
            result_type: The type of result this handler handles.

        Returns:
            A decorator function that registers the handler.
        """

        def decorator(func: Callable[[List[T]], None]):
            self._handlers[result_type] = func
            return func

        return decorator

    def dispatch(self, results: List[Any], result_type: Type[T]) -> None:
        """
        Dispatch results to the appropriate handler.

        Args:
            results: The results to process.
            result_type: The type of the results.

        Raises:
            ValueError: If no handler is registered for the result type.
        """
        handler = self._handlers.get(result_type)
        if not handler:
            raise ValueError(f"No handler registered for {result_type.__name__}.")
        handler(results)
