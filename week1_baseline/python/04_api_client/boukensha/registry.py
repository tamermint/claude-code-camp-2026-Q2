from __future__ import annotations

from typing import Any, Callable, Optional
from .context import Context
from .errors import UnknownToolError
from .tool import Tool


class Registry:
    """Manages tool registration and dispatching for agent workflows."""

    def __init__(self, context: Optional[Context] = None) -> None:
        self.context = context
        self.tools: dict[str, Tool] = {}
        if context is not None:
            context.tools = self.tools

    def register_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool
        if self.context is not None and tool.name not in self.context.tools:
            self.context.register_tool(tool)

    def tool(
        self,
        name: str,
        description: str,
        parameters: Optional[dict[str, Any]] = None,
        block: Optional[Callable[..., Any]] = None,
    ) -> Any:
        params = parameters if parameters is not None else {}

        if block is not None:
            t = Tool(name=str(name), description=description, parameters=params, block=block)
            self.register_tool(t)
            return t

        def decorator(fn: Callable[..., Any]) -> Tool:
            t = Tool(name=str(name), description=description, parameters=params, block=fn)
            self.register_tool(t)
            return t

        return decorator

    def dispatch(self, name: str, args: Optional[dict[str, Any]] = None) -> Any:
        tool = self.tools.get(str(name))
        if tool is None:
            raise UnknownToolError(f"No tool registered as '{name}'")

        call_args = args if args is not None else {}
        clean_args = {str(k).lstrip(":"): v for k, v in call_args.items()}

        if tool.block is None:
            return None
        return tool.block(**clean_args)
