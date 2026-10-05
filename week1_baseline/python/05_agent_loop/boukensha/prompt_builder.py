from __future__ import annotations

import inspect
from typing import Any, Optional
from .backends.base import Base
from .context import Context
from .registry import Registry
from .tool import Tool


class PromptBuilder:
    """Serializes Context into API payloads for the configured LLM backend and normalizes responses."""

    def __init__(
        self,
        context: Context,
        backend: Base,
        registry: Optional[Registry] = None,
    ) -> None:
        self.context = context
        self.backend = backend
        self.registry = registry

    @property
    def tools(self) -> dict[str, Tool]:
        if self.registry is not None:
            return self.registry.tools
        if hasattr(self.context, "tools"):
            return self.context.tools
        return {}

    def to_messages(self) -> list[dict[str, Any]]:
        sig = inspect.signature(self.backend.to_messages)
        if len(sig.parameters) >= 2:
            return self.backend.to_messages(self.context.system or "", self.context.messages)
        return self.backend.to_messages(self.context.messages)

    def to_tools(self) -> Any:
        return self.backend.to_tools(self.tools)

    def to_api_payload(
        self,
        max_output_tokens: int = 1024,
        tools: Optional[Any] = None,
    ) -> dict[str, Any]:
        return self.backend.to_payload(
            self.context,
            max_output_tokens=max_output_tokens,
            tools=tools,
        )

    def parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        return self.backend.parse_response(response)

    @property
    def headers(self) -> dict[str, str]:
        return self.backend.headers

    @property
    def url(self) -> str:
        return self.backend.url
