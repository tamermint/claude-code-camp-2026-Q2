from __future__ import annotations

from typing import Any, ClassVar
from .base import Base


class Ollama(Base):
    """Local Ollama LLM backend serializer."""

    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "gemma4": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:e2b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:e4b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:12b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:26b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "gemma4:31b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen3:30b": {
            "context_window": 256_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen3:8b": {
            "context_window": 40_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "deepseek-r1:8b": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
    }

    def __init__(self, model: str, host: str = "http://localhost:11434") -> None:
        self.host = host.rstrip("/")
        super().__init__(model)

    def to_messages(self, system: str, messages: list[Any]) -> list[dict[str, Any]]:
        system_message = [{"role": "system", "content": system}]
        conversation = []
        for msg in messages:
            role_str = str(msg.role).lstrip(":")
            if role_str == "tool_result":
                conversation.append({
                    "role": "tool",
                    "tool_name": msg.tool_use_id,
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
            "stream": False,
            "messages": self.to_messages(context.system, context.messages),
            "tools": self.to_tools(tools_dict),
        }

    @property
    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    @property
    def url(self) -> str:
        return f"{self.host}/api/chat"
