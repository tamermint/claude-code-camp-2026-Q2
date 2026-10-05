from __future__ import annotations

import json
from typing import Any, ClassVar, Optional
from ..context import Context
from ..message import Message
from ..tool import Tool
from .base import Base


class OpenAI(Base):
    """OpenAI Chat Completions backend serializer and response normalizer."""

    BASE_URL = "https://api.openai.com/v1/chat/completions"

    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "gpt-4o": {
            "context_window": 128_000,
            "cost_per_million": {"input": 2.50, "output": 10.0},
            "usage_unit": "tokens",
        },
        "gpt-4o-mini": {
            "context_window": 128_000,
            "cost_per_million": {"input": 0.15, "output": 0.60},
            "usage_unit": "tokens",
        },
        "o3-mini": {
            "context_window": 200_000,
            "cost_per_million": {"input": 1.10, "output": 4.40},
            "usage_unit": "tokens",
        },
    }

    def __init__(self, api_key: str, model: str) -> None:
        self.api_key = api_key
        super().__init__(model)

    def to_messages(self, system: str, messages: list[Message]) -> list[dict[str, Any]]:
        res: list[dict[str, Any]] = [{"role": "system", "content": system}]
        for msg in messages:
            if msg.role == "tool_result":
                res.append({
                    "role": "tool",
                    "tool_call_id": msg.tool_use_id,
                    "content": msg.content,
                })
            elif msg.role == "assistant":
                res.append(self._assistant_message(msg.content))
            else:
                res.append({"role": msg.role, "content": msg.content})
        return res

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
            "messages": self.to_messages(context.system or "", context.messages),
            "tools": tool_declarations,
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

    def parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        choices = response.get("choices") or []
        message = choices[0].get("message", {}) if choices else {}
        tool_calls = message.get("tool_calls") or []

        content: list[dict[str, Any]] = []
        if message.get("content"):
            content.append({"type": "text", "text": message["content"]})

        for tc in tool_calls:
            fn = tc.get("function", {})
            raw_args = fn.get("arguments", "{}")
            args = json.loads(raw_args) if isinstance(raw_args, str) else raw_args
            content.append({
                "type": "tool_use",
                "id": tc.get("id"),
                "name": fn.get("name"),
                "input": args,
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
                    "id": b.get("id"),
                    "type": "function",
                    "function": {
                        "name": b["name"],
                        "arguments": json.dumps(b.get("input", {})),
                    },
                }
                for b in tool_blocks
            ]
        return msg
