from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

# Add package directory to path
pkg_dir = Path(__file__).resolve().parent.parent
if str(pkg_dir) not in sys.path:
    sys.path.insert(0, str(pkg_dir))

from boukensha import Agent, Client, Context, Message, PromptBuilder, Registry, tasks
from boukensha.backends import Gemini
from boukensha.errors import ApiError


class MockClient(Client):
    """Mocks API responses for agent loop testing without external network traffic."""

    def __init__(self, responses: list[dict[str, Any]]) -> None:
        super().__init__(max_retries=1, base_retry_delay=0.01)
        self.responses = list(responses)
        self.call_history: list[dict[str, Any]] = []

    def call(
        self,
        builder: PromptBuilder,
        max_output_tokens: int = 1024,
        tools: Any = None,
    ) -> dict[str, Any]:
        self.call_history.append({
            "max_output_tokens": max_output_tokens,
            "tools": tools,
            "turn_count": len(builder.context.messages),
        })
        if not self.responses:
            raise ApiError("No more mock responses")
        resp = self.responses.pop(0)
        if isinstance(resp, Exception):
            raise resp
        return resp


def test_agent_immediate_text() -> None:
    ctx = Context(task=tasks.Player, system="Test system")
    reg = Registry(ctx)
    backend = Gemini(api_key="fake-key", model="gemini-3.8-flash")
    builder = PromptBuilder(ctx, backend)

    mock_resp = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": "Hello, adventurer!"}],
                },
                "finishReason": "STOP",
            }
        ]
    }
    client = MockClient([mock_resp])
    agent = Agent(context=ctx, registry=reg, builder=builder, client=client)

    result = agent.run()
    assert result == "Hello, adventurer!"
    assert agent.iteration == 1
    assert len(client.call_history) == 1
    print("✓ test_agent_immediate_text passed")


def test_agent_tool_use_cycle() -> None:
    ctx = Context(task=tasks.Player, system="Test system")
    reg = Registry(ctx)
    backend = Gemini(api_key="fake-key", model="gemini-3.8-flash")
    builder = PromptBuilder(ctx, backend)

    @reg.tool("add", description="Add numbers", parameters={"a": {"type": "int"}, "b": {"type": "int"}})
    def add(a: int, b: int) -> int:
        return a + b

    resp_1 = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "functionCall": {"name": "add", "args": {"a": 2, "b": 3}},
                            "thoughtSignature": "sig123",
                        }
                    ],
                },
                "finishReason": "STOP",
            }
        ]
    }
    resp_2 = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": "The answer is 5."}],
                },
                "finishReason": "STOP",
            }
        ]
    }
    client = MockClient([resp_1, resp_2])
    agent = Agent(context=ctx, registry=reg, builder=builder, client=client)

    result = agent.run()
    assert result == "The answer is 5."
    assert agent.iteration == 2
    # Verify messages in context
    assert len(ctx.messages) == 2  # assistant tool_use, then tool_result
    assert ctx.messages[0].role == "assistant"
    assert ctx.messages[1].role == "tool_result"
    assert ctx.messages[1].content == "5"
    assert ctx.messages[1].tool_use_id == "add"
    print("✓ test_agent_tool_use_cycle passed")


def test_agent_multi_tool_use() -> None:
    ctx = Context(task=tasks.Player, system="Test system")
    reg = Registry(ctx)
    backend = Gemini(api_key="fake-key", model="gemini-3.8-flash")
    builder = PromptBuilder(ctx, backend)

    executed: list[str] = []

    @reg.tool("tool_a", description="Tool A")
    def tool_a() -> str:
        executed.append("a")
        return "result_a"

    @reg.tool("tool_b", description="Tool B")
    def tool_b() -> str:
        executed.append("b")
        return "result_b"

    resp_1 = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {"functionCall": {"name": "tool_a", "args": {}}},
                        {"functionCall": {"name": "tool_b", "args": {}}},
                    ],
                }
            }
        ]
    }
    resp_2 = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": "Both tools executed."}],
                }
            }
        ]
    }
    client = MockClient([resp_1, resp_2])
    agent = Agent(context=ctx, registry=reg, builder=builder, client=client)

    result = agent.run()
    assert result == "Both tools executed."
    assert executed == ["a", "b"]
    assert len(ctx.messages) == 3  # 1 assistant + 2 tool_results
    print("✓ test_agent_multi_tool_use passed")


def test_agent_iteration_limit_wrap_up() -> None:
    ctx = Context(task=tasks.Player, system="Test system")
    reg = Registry(ctx)
    backend = Gemini(api_key="fake-key", model="gemini-3.8-flash")
    builder = PromptBuilder(ctx, backend)

    @reg.tool("loop_tool", description="Infinite tool")
    def loop_tool() -> str:
        return "repeating"

    loop_resp = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"functionCall": {"name": "loop_tool", "args": {}}}],
                }
            }
        ]
    }
    wrap_up_resp = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"text": "Wrapped up after reaching limit."}],
                }
            }
        ]
    }

    # max_iterations = 2: iteration 1 (loop_resp), iteration 2 (loop_resp), then wrap_up (wrap_up_resp)
    client = MockClient([loop_resp, loop_resp, wrap_up_resp])
    agent = Agent(context=ctx, registry=reg, builder=builder, client=client, max_iterations=2)

    result = agent.run()
    assert result == "Wrapped up after reaching limit."
    assert agent.iteration == 2
    # Check that wrap-up call sent tools=[]
    last_call = client.call_history[-1]
    assert last_call["tools"] == []
    assert last_call["max_output_tokens"] == Agent.WRAP_UP_OUTPUT_TOKENS
    print("✓ test_agent_iteration_limit_wrap_up passed")


def test_agent_wrap_up_fallback_on_api_error() -> None:
    ctx = Context(task=tasks.Player, system="Test system")
    reg = Registry(ctx)
    backend = Gemini(api_key="fake-key", model="gemini-3.8-flash")
    builder = PromptBuilder(ctx, backend)

    @reg.tool("loop_tool", description="Infinite tool")
    def loop_tool() -> str:
        return "repeating"

    loop_resp = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [{"functionCall": {"name": "loop_tool", "args": {}}}],
                }
            }
        ]
    }

    # Wrap up call fails with ApiError
    client = MockClient([loop_resp, ApiError("Server down")])
    agent = Agent(context=ctx, registry=reg, builder=builder, client=client, max_iterations=1)

    result = agent.run()
    assert "I reached my 1-action limit for this turn before finishing" in result
    print("✓ test_agent_wrap_up_fallback_on_api_error passed")


def test_gemini_thought_signature_preservation() -> None:
    backend = Gemini(api_key="fake-key", model="gemini-3.8-flash")
    raw_response = {
        "candidates": [
            {
                "content": {
                    "role": "model",
                    "parts": [
                        {
                            "functionCall": {"name": "read_file", "args": {"path": "a.txt"}},
                            "thoughtSignature": "cryptographic_blob_xyz",
                        }
                    ],
                }
            }
        ]
    }

    parsed = backend.parse_response(raw_response)
    assert parsed["stop_reason"] == "tool_use"
    assert len(parsed["content"]) == 1
    block = parsed["content"][0]
    assert block["thought_signature"] == "cryptographic_blob_xyz"

    # Reconstruct messages
    msgs = [Message(role="assistant", content=parsed["content"])]
    wire_msgs = backend.to_messages(msgs)
    assert len(wire_msgs) == 1
    assert wire_msgs[0]["role"] == "model"
    part = wire_msgs[0]["parts"][0]
    assert part["functionCall"]["name"] == "read_file"
    assert part["thoughtSignature"] == "cryptographic_blob_xyz"
    print("✓ test_gemini_thought_signature_preservation passed")


if __name__ == "__main__":
    test_agent_immediate_text()
    test_agent_tool_use_cycle()
    test_agent_multi_tool_use()
    test_agent_iteration_limit_wrap_up()
    test_agent_wrap_up_fallback_on_api_error()
    test_gemini_thought_signature_preservation()
    print("\nAll 6 Agent tests passed successfully!")
