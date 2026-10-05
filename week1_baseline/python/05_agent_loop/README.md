# The Agent Loop

The Agent Loop is the heart of BOUKENSHA. Everything built before this — the structs, the registry, the prompt builder, the client — was setup. The loop is where the agent actually does work.

## New Files

| File | Description |
|---|---|
| `boukensha/agent.py` | The agent loop — sends requests, dispatches tools, and knows when to stop |
| `boukensha/backends/base.py` | Shared backend model validation and model metadata helpers |
| `boukensha/tasks/base.py` | Shared task configuration helpers for provider, model, turn limits, and prompts |
| `boukensha/tasks/player.py` | Player task definition |
| `boukensha/backends/gemini.py` | Google Gemini backend with thought signature preservation |
| `boukensha/backends/anthropic.py` | Anthropic Messages API backend |
| `boukensha/backends/openai.py` | OpenAI Chat Completions backend |
| `boukensha/backends/ollama.py` | Local Ollama backend |
| `boukensha/backends/ollama_cloud.py` | Hosted Ollama Cloud backend |
| `prompts/system.md` | Default system prompt used when the player task does not override it |

## Updated Files

| File | Change |
|---|---|
| `boukensha/errors.py` | Added `LoopError` for runaway agents |
| `boukensha/config.py` | Reads `tasks.player` instead of top-level provider/model settings |
| `boukensha/context.py` | Carries the active task object alongside messages and tools |
| `boukensha/prompt_builder.py` | Added `parse_response`, delegating to the backend |
| `boukensha/client.py` | Added optional `tools` parameter support for tool-disabled wind-down calls |
| `boukensha/backends/*.py` | Backends implement `parse_response` and assistant message reconstructors |

## How It Works

```
send messages to API
        ↓
stop_reason == "tool_use"?
    yes → extract tool calls
        → dispatch each tool via Registry
        → inject results as tool_result messages
        → go back to top
    no  → return final text response
```

## Boukensha::Agent / `boukensha.Agent`

| Method | Description |
|---|---|
| `run` | Starts the loop and returns the final text response when the agent is done |

## Every Backend Speaks the Same Normalized Shape

Five providers means five different response formats — Anthropic nests tool calls inside `content`, Ollama puts them in `message.tool_calls`, OpenAI nests them under `choices[0].message.tool_calls`, and Gemini calls them `functionCall` parts. Rather than teach the Agent loop about each of these, every backend implements `parse_response`, converting its raw response into one common shape:

```python
{
    "stop_reason": "tool_use" | "end_turn",
    "content": [
        {"type": "text", "text": "..."},
        {"type": "tool_use", "id": "...", "name": "...", "input": {...}},
    ],
}
```

`Boukensha::Agent` only ever sees this shape — it calls `builder.parse_response(response)`, which delegates to the backend, and never inspects a raw provider response.

The conversion also runs in reverse. When the conversation history is replayed on the next request, Ollama, Ollama Cloud, OpenAI, and Gemini each rebuild a provider-specific assistant message from the normalized `content` blocks via a private `_assistant_message` (or `_assistant_parts`) method — the inverse of `parse_response`. Anthropic's `content` array doubles as both the normalized shape and the wire format, so it needs no extra conversion.

**Tool call IDs aren't universal.** Anthropic and OpenAI assign every tool call a unique `id`, echoed back in the `tool_result`. Ollama, Ollama Cloud, and Gemini don't assign call ids at all — those backends reuse the tool's `name` as its `id` and match the `tool_result` back to the call by name.

**Gemini Thought Signatures.** Gemini 3 series models require thought signatures (`thoughtSignature`) on every `functionCall` part in the conversation history when replayed in multi-turn interactions. Gemini's backend preserves and replays this cryptographic token across iterations.

## Running the Example

```bash
bash week1_baseline/bin/python/05_agent_loop.sh
```
