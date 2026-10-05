from __future__ import annotations

from typing import Any, Optional
from .message import Message
from .tool import Tool


class Context:
    """Holds conversation state for an agent run (task, system prompt, messages, tools)."""

    def __init__(self, task: Any, system: Optional[str] = None) -> None:
        self.task = task
        self.system = system
        self.messages: list[Message] = []
        self.tools: dict[str, Tool] = {}

    def register_tool(self, tool: Tool) -> None:
        self.tools[tool.name] = tool

    def add_message(self, role: str, content: Any, tool_use_id: Optional[str] = None) -> Message:
        msg = Message(role=role, content=content, tool_use_id=tool_use_id)
        self.messages.append(msg)
        return msg

    @property
    def tool_count(self) -> int:
        return len(self.tools)

    @property
    def turn_count(self) -> int:
        return len(self.messages)

    def __str__(self) -> str:
        task_name = (
            self.task.task_name()
            if hasattr(self.task, "task_name") and callable(self.task.task_name)
            else getattr(self.task, "task_name", None)
        )
        return f"#<Context task={task_name} turns={self.turn_count} tools={self.tool_count}>"

    def __repr__(self) -> str:
        return self.__str__()
