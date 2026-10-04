from __future__ import annotations

from typing import Any, ClassVar
from .base import Base


class Anthropic(Base):
    """Anthropic Claude LLM backend serializer."""

    BASE_URL = "https://api.anthropic.com/v1/messages"
    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "claude-haiku-4-5": {
            "context_window": 200_000,
            "cost_per_million": {"input": 1.0, "output": 5.0},
            "usage_unit": "tokens",
        },
        "claude-haiku-4-5-20251001": {
            "context_window": 200_000,
            "cost_per_million": {"input": 1.0, "output": 5.0},
            "usage_unit": "tokens",
        },
        "claude-sonnet-4-6": {
            "context_window": 1_000_000,
            "cost_per_million": {"input": 3.0, "output": 15.0},
            "usage_unit": "tokens",
        },
        "claude-opus-4-8": {
            "context_window": 1_000_000,
            "cost_per_million": {"input": 5.0, "output": 25.0},
            "usage_unit": "tokens",
        },
    }

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        super().__init__(model)

    def to_messages(self, messages: list[Any]) -> list[dict[str, Any]]:
        result = []
        for msg in messages:
            role_str = str(msg.role).lstrip(":")
            if role_str == "tool_result":
                result.append({
                    "role": "user",
                    "content": [{
                        "type": "tool_result",
                        "tool_use_id": msg.tool_use_id,
                        "content": msg.content,
                    }],
                })
            else:
                result.append({"role": role_str, "content": msg.content})
        return result

    def to_tools(self, tools: dict[str, Any]) -> list[dict[str, Any]]:
        declarations = []
        for tool in tools.values():
            params = getattr(tool, "parameters", {})
            required_keys = [str(k) for k in params.keys()]
            declarations.append({
                "name": tool.name,
                "description": tool.description,
                "input_schema": {
                    "type": "object",
                    "properties": params,
                    "required": required_keys,
                },
            })
        return declarations

    def to_payload(self, context: Any, max_output_tokens: int = 1024) -> dict[str, Any]:
        tools_dict = getattr(context, "tools", {})
        return {
            "model": self.model,
            "system": context.system,
            "max_tokens": max_output_tokens,
            "tools": self.to_tools(tools_dict),
            "messages": self.to_messages(context.messages),
        }

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-api-key": self.api_key,
            "anthropic-version": "2023-06-01",
        }

    @property
    def url(self) -> str:
        return self.BASE_URL
