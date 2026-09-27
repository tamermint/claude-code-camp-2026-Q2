from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Optional


@dataclass
class Tool:
    """Represents an executable tool that the agent can invoke."""

    name: str
    description: str
    parameters: dict[str, Any] = field(default_factory=dict)
    block: Optional[Callable[..., Any]] = None

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        if self.block is not None:
            return self.block(*args, **kwargs)
        raise RuntimeError(f"Tool '{self.name}' has no callable block defined")

    def __str__(self) -> str:
        param_keys = [f":{k}" if not str(k).startswith(":") else str(k) for k in self.parameters.keys()]
        params_str = f"[{', '.join(param_keys)}]"
        return f"#<Tool name={self.name} description={str(self.description)[:41]} params={params_str}>"

    def __repr__(self) -> str:
        return self.__str__()
