from __future__ import annotations

from typing import Any, ClassVar, Optional
from ..context import Context
from ..message import Message
from ..tool import Tool
from .base import Base


class Anthropic(Base):
    """Anthropic Claude Messages API backend serializer and response normalizer."""

    BASE_URL = "https://api.anthropic.com/v1/messages"

    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "claude-3-7-sonnet": {
            "context_window": 200_000,
            "cost_per_million": {"input": 3.0, "output": 15.0},
            "usage_unit": "tokens",
        },
        "claude-3-5-haiku": {
            "context_window": 200_000,
            "cost_per_million": {"input": 0.80, "output": 4.0},
            "usage_unit": "tokens",
        },
        "claude-3-5-sonnet": {
            "context_window": 200_000,
            "cost_per_million": {"input": 3.0, "output": 15.0},
            "usage_unit": "tokens",
        },
        "claude-haiku-4-5": {
            "context_window": 200_000,
            "cost_per_million": {"input": 1.0, "output": 5.0},
            "usage_unit": "tokens",
        },
        "claude-sonnet-4-5": {
            "context_window": 200_000,
            "cost_per_million": {"input": 3.0, "output": 15.0},
            "usage_unit": "tokens",
        },
        "claude-opus-4-5": {
            "context_window": 200_000,
            "cost_per_million": {"input": 5.0, "output": 25.0},
            "usage_unit": "tokens",
        },
    }

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        super().__init__(model)

    def to_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        result = []
        for msg in messages:
            if msg.role == "tool_result":
                result.append({
                    "role": "user",
                    "content": [
                        {
                            "type": "tool_result",
                            "tool_use_id": msg.tool_use_id,
                            "content": msg.content,
                        }
                    ],
                })
            else:
                result.append({"role": msg.role, "content": msg.content})
        return result

    def to_tools(self, tools: dict[str, Tool]) -> list[dict[str, Any]]:
        return [
            {
                "name": tool.name,
                "description": tool.description,
                "input_schema": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": list(tool.parameters.keys()),
                },
            }
            for tool in tools.values()
        ]

    def to_payload(
        self,
        context: Context,
        max_output_tokens: int = 1024,
        tools: Optional[Any] = None,
    ) -> dict[str, Any]:
        tool_declarations = self.to_tools(context.tools) if tools is None else tools
        return {
            "model": self.model,
            "system": context.system or "",
            "max_tokens": max_output_tokens,
            "tools": tool_declarations,
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

    def parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        stop_reason = "tool_use" if response.get("stop_reason") == "tool_use" else "end_turn"
        return {
            "stop_reason": stop_reason,
            "content": response.get("content") or [],
        }
