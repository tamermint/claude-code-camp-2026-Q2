from __future__ import annotations

from typing import Any, ClassVar, Optional
from ..context import Context
from ..message import Message
from ..tool import Tool
from .base import Base


class Ollama(Base):
    """Local Ollama backend serializer and response normalizer."""

    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "mistral-small:24b": {
            "context_window": 32_768,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "phi4:14b": {
            "context_window": 16_384,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen2.5:7b": {
            "context_window": 32_768,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen2.5:14b": {
            "context_window": 32_768,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "qwen2.5:32b": {
            "context_window": 32_768,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "llama3.3:70b": {
            "context_window": 131_072,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "deepseek-r1:14b": {
            "context_window": 131_072,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "deepseek-r1:32b": {
            "context_window": 131_072,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
        "deepseek-r1:70b": {
            "context_window": 131_072,
            "cost_per_million": {"input": 0.0, "output": 0.0},
            "usage_unit": "local_compute",
        },
    }

    def __init__(self, model: str, host: str = "http://localhost:11434") -> None:
        self.host = host
        super().__init__(model)

    def to_messages(self, system: str, messages: list[Message]) -> list[dict[str, Any]]:
        system_message: list[dict[str, Any]] = [{"role": "system", "content": system}]
        conversation = []
        for msg in messages:
            if msg.role == "tool_result":
                conversation.append({
                    "role": "tool",
                    "tool_name": msg.tool_use_id,
                    "content": msg.content,
                })
            elif msg.role == "assistant":
                conversation.append(self._assistant_message(msg.content))
            else:
                conversation.append({"role": msg.role, "content": msg.content})
        return system_message + conversation

    def to_tools(self, tools: dict[str, Tool]) -> list[dict[str, Any]]:
        return [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": {
                        "type": "object",
                        "properties": tool.parameters,
                        "required": list(tool.parameters.keys()),
                    },
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
            "stream": False,
            "messages": self.to_messages(context.system or "", context.messages),
            "tools": tool_declarations,
        }

    @property
    def headers(self) -> dict[str, str]:
        return {"Content-Type": "application/json"}

    @property
    def url(self) -> str:
        return f"{self.host}/api/chat"

    def parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        message = response.get("message") or {}
        tool_calls = message.get("tool_calls") or []

        content: list[dict[str, Any]] = []
        if message.get("content"):
            content.append({"type": "text", "text": message["content"]})

        for tc in tool_calls:
            fn = tc.get("function") or {}
            content.append({
                "type": "tool_use",
                "id": fn.get("name"),
                "name": fn.get("name"),
                "input": fn.get("arguments") or {},
            })

        return {
            "stop_reason": "tool_use" if tool_calls else "end_turn",
            "content": content,
        }

    def _assistant_message(self, content: Any) -> dict[str, Any]:
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content

        text_blocks = [b for b in blocks if b.get("type") == "text"]
        tool_blocks = [b for b in blocks if b.get("type") == "tool_use"]

        msg: dict[str, Any] = {
            "role": "assistant",
            "content": "".join(b.get("text", "") for b in text_blocks),
        }
        if tool_blocks:
            msg["tool_calls"] = [
                {
                    "function": {
                        "name": b["name"],
                        "arguments": b.get("input", {}),
                    }
                }
                for b in tool_blocks
            ]
        return msg
