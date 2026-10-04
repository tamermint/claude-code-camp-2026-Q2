from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure boukensha is in sys.path
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from boukensha.context import Context
from boukensha.errors import UnsupportedModelError
from boukensha.prompt_builder import PromptBuilder
from boukensha.registry import Registry
from boukensha.backends.anthropic import Anthropic
from boukensha.backends.gemini import Gemini
from boukensha.backends.ollama import Ollama
from boukensha.backends.ollama_cloud import OllamaCloud
from boukensha.backends.openai import OpenAI


class DummyTask:
    @classmethod
    def task_name(cls):
        return "player"


def setup_context_and_registry():
    ctx = Context(task=DummyTask, system="You are an adventurer assistant.")
    registry = Registry(ctx)

    @registry.tool(
        "look",
        description="Look around the current room",
        parameters={},
    )
    def look():
        return "You see a dark cave."

    @registry.tool(
        "move",
        description="Move player in a direction",
        parameters={"direction": {"type": "string"}},
    )
    def move(direction: str):
        return f"Moving {direction}."

    ctx.add_message("user", "Hello dungeon!")
    ctx.add_message("assistant", "I will inspect the room.")
    ctx.add_message("tool_result", "You see a dark cave.", tool_use_id="toolu_123")
    return ctx, registry


def test_gemini():
    ctx, reg = setup_context_and_registry()
    backend = Gemini(api_key="test-key", model="gemini-3.8-flash")
    builder = PromptBuilder(ctx, backend)
    payload = builder.to_api_payload()

    assert "systemInstruction" in payload
    assert payload["systemInstruction"]["parts"][0]["text"] == "You are an adventurer assistant."
    assert payload["contents"][0]["role"] == "user"
    assert payload["contents"][1]["role"] == "model"
    assert payload["contents"][2]["parts"][0]["functionResponse"]["name"] == "toolu_123"
    assert payload["tools"][0]["functionDeclarations"][0]["name"] == "look"
    assert payload["tools"][0]["functionDeclarations"][1]["name"] == "move"
    assert builder.headers["x-goog-api-key"] == "test-key"
    assert builder.url.endswith("gemini-3.8-flash:generateContent")
    assert backend.context_window == 1_048_576
    assert backend.estimate_cost(100_000, 100_000) is not None
    print("✓ Gemini backend tests passed")


def test_anthropic():
    ctx, reg = setup_context_and_registry()
    backend = Anthropic(api_key="sk-ant-test", model="claude-sonnet-4-6")
    builder = PromptBuilder(ctx, backend)
    payload = builder.to_api_payload()

    assert payload["system"] == "You are an adventurer assistant."
    assert payload["model"] == "claude-sonnet-4-6"
    assert payload["messages"][1]["role"] == "assistant"
    assert payload["messages"][2]["content"][0]["type"] == "tool_result"
    assert payload["messages"][2]["content"][0]["tool_use_id"] == "toolu_123"
    assert "input_schema" in payload["tools"][0]
    assert builder.headers["x-api-key"] == "sk-ant-test"
    assert builder.url == "https://api.anthropic.com/v1/messages"
    print("✓ Anthropic backend tests passed")


def test_openai():
    ctx, reg = setup_context_and_registry()
    backend = OpenAI(api_key="sk-openai-test", model="gpt-5.4")
    builder = PromptBuilder(ctx, backend)
    payload = builder.to_api_payload()

    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][1]["role"] == "user"
    assert payload["messages"][2]["role"] == "assistant"
    assert payload["messages"][3]["role"] == "tool"
    assert payload["messages"][3]["tool_call_id"] == "toolu_123"
    assert payload["tools"][0]["type"] == "function"
    assert payload["tools"][0]["function"]["name"] == "look"
    assert builder.headers["Authorization"] == "Bearer sk-openai-test"
    assert builder.url == "https://api.openai.com/v1/chat/completions"
    print("✓ OpenAI backend tests passed")


def test_ollama():
    ctx, reg = setup_context_and_registry()
    backend = Ollama(model="gemma4:12b", host="http://127.0.0.1:11434")
    builder = PromptBuilder(ctx, backend)
    payload = builder.to_api_payload()

    assert payload["stream"] is False
    assert payload["messages"][0]["role"] == "system"
    assert payload["messages"][3]["role"] == "tool"
    assert payload["messages"][3]["tool_name"] == "toolu_123"
    assert payload["tools"][0]["type"] == "function"
    assert builder.url == "http://127.0.0.1:11434/api/chat"
    assert backend.estimate_cost(1000, 1000) == 0.0
    print("✓ Ollama backend tests passed")


def test_ollama_cloud():
    ctx, reg = setup_context_and_registry()
    backend = OllamaCloud(api_key="ollama-key", model="kimi-k2.5:cloud")
    builder = PromptBuilder(ctx, backend)
    payload = builder.to_api_payload()

    assert payload["stream"] is False
    assert builder.headers["Authorization"] == "Bearer ollama-key"
    assert builder.url == "https://ollama.com/api/chat"
    assert backend.estimate_cost(1000, 1000) is None
    print("✓ OllamaCloud backend tests passed")


def test_unsupported_model():
    try:
        Gemini(api_key="test", model="gpt-4")
        assert False, "Should have raised UnsupportedModelError"
    except UnsupportedModelError as e:
        assert "Gemini does not support model 'gpt-4'" in str(e)
        assert "gemini-3.8-flash" in str(e)
    print("✓ UnsupportedModelError validation passed")


if __name__ == "__main__":
    test_gemini()
    test_anthropic()
    test_openai()
    test_ollama()
    test_ollama_cloud()
    test_unsupported_model()
    print("\nAll 6 test suites passed successfully!")
