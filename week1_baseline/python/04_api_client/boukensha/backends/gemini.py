from __future__ import annotations

from typing import Any, ClassVar
from .base import Base


class Gemini(Base):
    """Gemini LLM backend serializer."""

    BASE_URL = "https://generativelanguage.googleapis.com/v1beta/models"
    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "gemini-3.8-flash": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 0.75, "output": 3.75},
            "usage_unit": "tokens",
        },
        "gemini-3.5-flash": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 1.5, "output": 9.0},
            "usage_unit": "tokens",
        },
        "gemini-3.1-flash-lite": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 0.25, "output": 1.5},
            "usage_unit": "tokens",
        },
        "gemini-2.5-pro": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 1.25, "output": 10.0},
            "usage_unit": "tokens",
        },
        "gemini-2.5-flash": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 0.30, "output": 2.50},
            "usage_unit": "tokens",
        },
        "gemini-2.5-flash-lite": {
            "context_window": 1_048_576,
            "cost_per_million": {"input": 0.10, "output": 0.40},
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
            if role_str == "assistant":
                result.append({"role": "model", "parts": [{"text": msg.content}]})
            elif role_str == "tool_result":
                result.append({
                    "role": "user",
                    "parts": [{
                        "functionResponse": {
                            "name": msg.tool_use_id,
                            "response": {"content": msg.content},
                        }
                    }],
                })
            else:
                result.append({"role": role_str, "parts": [{"text": msg.content}]})
        return result

    def to_tools(self, tools: dict[str, Any]) -> list[dict[str, Any]]:
        if not tools:
            return []

        declarations = []
        for tool in tools.values():
            params = getattr(tool, "parameters", {})
            required_keys = [str(k) for k in params.keys()]
            declarations.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": params,
                    "required": required_keys,
                },
            })
        return [{"functionDeclarations": declarations}]

    def to_payload(self, context: Any, max_output_tokens: int = 1024) -> dict[str, Any]:
        tools_dict = getattr(context, "tools", {})
        return {
            "systemInstruction": {"parts": [{"text": context.system}]},
            "contents": self.to_messages(context.messages),
            "tools": self.to_tools(tools_dict),
            "generationConfig": {"maxOutputTokens": max_output_tokens},
        }

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": self.api_key,
        }

    @property
    def url(self) -> str:
        return f"{self.BASE_URL}/{self.model}:generateContent"
