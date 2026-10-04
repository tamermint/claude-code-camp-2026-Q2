from __future__ import annotations

from typing import Any, ClassVar
from .base import Base


class OllamaCloud(Base):
    """Ollama Cloud LLM backend serializer."""

    BASE_URL = "https://ollama.com"
    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "gemma4:31b-cloud": {
            "context_window": 256_000,
            "cost_per_million": {"input": None, "output": None},
            "usage_unit": "ollama_cloud_usage",
            "usage_level": "medium",
        },
        "minimax-m3:cloud": {
            "context_window": 512_000,
            "advertised_context_window": 1_000_000,
            "cost_per_million": {"input": None, "output": None},
            "usage_unit": "ollama_cloud_usage",
            "usage_level": "high",
        },
        "kimi-k2.5:cloud": {
            "context_window": 256_000,
            "cost_per_million": {"input": None, "output": None},
            "usage_unit": "ollama_cloud_usage",
            "usage_level": "high",
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
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

    @property
    def url(self) -> str:
        return f"{self.BASE_URL}/api/chat"
