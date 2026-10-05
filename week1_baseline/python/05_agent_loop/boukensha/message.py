from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class Message:
    """Represents a single conversation turn between user, assistant, or tool."""

    role: str
    content: Any
    tool_use_id: Optional[str] = None

    def __str__(self) -> str:
        id_tag = f" [{self.tool_use_id}]" if self.tool_use_id else ""
        return f"#<Message role={self.role}{id_tag} content={str(self.content)[:61]}...>"

    def __repr__(self) -> str:
        return self.__str__()
