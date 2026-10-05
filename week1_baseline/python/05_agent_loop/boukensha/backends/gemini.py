from __future__ import annotations

from typing import Any, ClassVar, Optional
from ..context import Context
from ..message import Message
from ..tool import Tool
from .base import Base


class Gemini(Base):
    """Google Gemini backend serializer and response normalizer."""

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

    def to_messages(self, messages: list[Message]) -> list[dict[str, Any]]:
        result = []
        for msg in messages:
            if msg.role == "assistant":
                result.append({"role": "model", "parts": self._assistant_parts(msg.content)})
            elif msg.role == "tool_result":
                result.append({
                    "role": "user",
                    "parts": [
                        {
                            "functionResponse": {
                                "name": msg.tool_use_id,
                                "response": {"content": msg.content},
                            }
                        }
                    ],
                })
            else:
                result.append({"role": msg.role, "parts": [{"text": str(msg.content)}]})
        return result

    def to_tools(self, tools: dict[str, Tool]) -> list[dict[str, Any]]:
        if not tools:
            return []

        declarations = []
        for tool in tools.values():
            declarations.append({
                "name": tool.name,
                "description": tool.description,
                "parameters": {
                    "type": "object",
                    "properties": tool.parameters,
                    "required": list(tool.parameters.keys()),
                },
            })

        return [{"functionDeclarations": declarations}]

    def to_payload(
        self,
        context: Context,
        max_output_tokens: int = 1024,
        tools: Optional[Any] = None,
    ) -> dict[str, Any]:
        tool_declarations = self.to_tools(context.tools) if tools is None else tools
        return {
            "systemInstruction": {"parts": [{"text": context.system or ""}]},
            "contents": self.to_messages(context.messages),
            "tools": tool_declarations,
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

    def parse_response(self, response: dict[str, Any]) -> dict[str, Any]:
        candidates = response.get("candidates") or []
        parts = candidates[0].get("content", {}).get("parts", []) if candidates else []

        content: list[dict[str, Any]] = []
        tool_used = False

        for part in parts:
            if "functionCall" in part:
                fc = part["functionCall"]
                block: dict[str, Any] = {
                    "type": "tool_use",
                    "id": fc.get("name"),
                    "name": fc.get("name"),
                    "input": fc.get("args") or {},
                }
                sig = part.get("thoughtSignature") or part.get("thought_signature")
                if sig:
                    block["thought_signature"] = sig
                content.append(block)
                tool_used = True
            elif "text" in part:
                content.append({"type": "text", "text": part["text"]})

        return {
            "stop_reason": "tool_use" if tool_used else "end_turn",
            "content": content,
        }

    def _assistant_parts(self, content: Any) -> list[dict[str, Any]]:
        blocks = [{"type": "text", "text": content}] if isinstance(content, str) else content

        parts = []
        for b in blocks:
            if b.get("type") == "tool_use":
                part: dict[str, Any] = {
                    "functionCall": {
                        "name": b["name"],
                        "args": b.get("input", {}),
                    }
                }
                sig = b.get("thought_signature") or b.get("thoughtSignature")
                if sig:
                    part["thoughtSignature"] = sig
                parts.append(part)
            else:
                parts.append({"text": b.get("text", "")})
        return parts
