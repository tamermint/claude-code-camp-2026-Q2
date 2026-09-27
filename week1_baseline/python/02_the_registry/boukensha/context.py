from __future__ import annotations

from typing import Any, Optional
from .message import Message


class Context:
    """Holds conversation state for an agent run (task, system prompt, messages)."""

    def __init__(self, task: Any, system: Optional[str] = None) -> None:
        self.task = task
        self.system = system
        self.messages: list[Message] = []

    def add_message(self, role: str, content: str, tool_use_id: Optional[str] = None) -> None:
        self.messages.append(Message(role=role, content=content, tool_use_id=tool_use_id))

    @property
    def turn_count(self) -> int:
        return len(self.messages)

    def __str__(self) -> str:
        task_name = (
            self.task.task_name()
            if hasattr(self.task, "task_name") and callable(self.task.task_name)
            else getattr(self.task, "task_name", None)
        )
        return f"#<Context task={task_name} turns={self.turn_count}>"

    def __repr__(self) -> str:
        return self.__str__()
