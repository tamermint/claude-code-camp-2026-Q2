from __future__ import annotations

from typing import Any, ClassVar
from .base import Base


class OpenAI(Base):
    """OpenAI Chat Completions LLM backend serializer."""

    BASE_URL = "https://api.openai.com/v1/chat/completions"
    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "gpt-5.5": {
            "context_window": 1_000_000,
            "cost_per_million": {"input": 5.0, "output": 30.0},
            "usage_unit": "tokens",
        },
        "gpt-5.4": {
            "context_window": 1_000_000,
            "cost_per_million": {"input": 2.5, "output": 15.0},
            "usage_unit": "tokens",
        },
        "gpt-5.4-mini": {
            "context_window": 400_000,
            "cost_per_million": {"input": 0.75, "output": 4.5},
            "usage_unit": "tokens",
        },
    }

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        super().__init__(model)

    def to_messages(self, system: str, messages: list[Any]) -> list[dict[str, Any]]:
        system_message = [{"role": "system", "content": system}]
        conversation = []
        for msg in messages:
            role_str = str(msg.role).lstrip(":")
            if role_str == "tool_result":
                conversation.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_use_id,
                    "content": msg.content,
                })
            else:
                conversation.append({"role": role_str, "content": msg.content})
        return system_message + conversation

    def to_tools(self, tools: dict[str, Any]) -> list[dict[str, Any]]:
        declarations = []
        for tool in tools.values():
            params = getattr(tool, "parameters", {})
            required_keys = [str(k) for k in params.keys()]
            declarations.append({
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": params,
                        "required": required_keys,
                    },
                },
            })
        return declarations

    def to_payload(self, context: Any, max_output_tokens: int = 1024) -> dict[str, Any]:
        tools_dict = getattr(context, "tools", {})
        return {
            "model": self.model,
            "messages": self.to_messages(context.system, context.messages),
            "tools": self.to_tools(tools_dict),
            "max_completion_tokens": max_output_tokens,
        }

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @property
    def url(self) -> str:
        return self.BASE_URL
