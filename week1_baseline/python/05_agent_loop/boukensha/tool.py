from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Optional


@dataclass
class Tool:
    """Represents a callable tool exposed to LLM agents."""

    name: str
    description: str
    parameters: dict[str, Any]
    block: Optional[Callable[..., Any]] = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.block is not None:
            return self.block(*args, **kwargs)
        return None

    def __str__(self) -> str:
        param_keys = [f":{k}" for k in self.parameters.keys()]
        params_str = f"[{', '.join(param_keys)}]"
        return f"#<Tool {self.name} params={params_str}>"

    def __repr__(self) -> str:
        return self.__str__()
