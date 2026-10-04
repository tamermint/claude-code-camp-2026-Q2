# The Prompt Builder

Because LLM access, cost, and quality are constantly changing, we want to be able to switch between multiple LLMs that will drive the agent loop.

There are several SDKs that provide access to many LLMs, but in practice we focus on top-tier models:
- Anthropic family
- OpenAI family
- Gemini family
- Ollama local / Ollama cloud (e.g. kimi, minimax, qwen)

The Prompt Builder serializes `Context` for the exact format each API expects. 
`PromptBuilder` delegates to whichever backend you pass in.

`PromptBuilder` does not call the API; we are simply preparing the format for API calls.

Configuration is task-based here, carried forward from the registry step. The
`player` task owns its provider, model, and prompt override settings, and the
context records the task that the prompt is being built for.

## New Files

| File | Description |
|---|---|
| `boukensha/prompt_builder.py` | Delegates serialization to the active backend |
| `boukensha/tasks/base.py` | Abstract task helper for provider/model and prompt resolution |
| `boukensha/tasks/player.py` | The concrete player task used by the main loop |
| `prompts/system.md` | Default system prompt used when a task does not override it |
| `boukensha/backends/base.py` | Shared backend contract for model validation and model metadata |
| `boukensha/backends/anthropic.py` | Serializes context into the Anthropic API format |
| `boukensha/backends/ollama.py` | Serializes context into the Ollama API format |
| `boukensha/backends/ollama_cloud.py` | Serializes context into the Ollama Cloud API format |
| `boukensha/backends/openai.py` | Serializes context into the OpenAI Chat Completions format |
| `boukensha/backends/gemini.py` | Serializes context into the Gemini `generateContent` format |

## How It Works

```
Context (Python objects)
        ↓
PromptBuilder
        ↓
Backend (Anthropic, OpenAI, Gemini, or Ollama)
        ↓
API Payload (plain dicts and lists)
        ↓
POST to API
```

## Boukensha::PromptBuilder (Python: `PromptBuilder`)

| Method | Description |
|---|---|
| `to_messages()` | Delegates message serialization to the backend |
| `to_tools()` | Delegates tool serialization to the backend |
| `to_api_payload(max_output_tokens=1024)` | Assembles the complete payload ready to POST |
| `headers` | Returns the correct headers for the backend |
| `url` | Returns the correct endpoint URL for the backend |

## Backends

Each API has its own conventions for how data is expected. Anthropic and Gemini are the most alike (system prompt as a top-level field), while OpenAI and Ollama share the same `function`-wrapped tool schema.

Backends also own their supported model table. A backend refuses to initialize
with an unknown model, so `settings.yml` cannot silently select an unsupported
or misspelled model. Each model entry carries:

| Key | Meaning |
|---|---|
| `context_window` | The model's known token context window |
| `cost_per_million.input` | USD input token price per million tokens, when known |
| `cost_per_million.output` | USD output token price per million tokens, when known |
| `usage_unit` | `"tokens"`, `"local_compute"`, or `"ollama_cloud_usage"` |
| `usage_level` | Ollama Cloud usage tier, when applicable |

Backend instances expose `context_window`, `input_token_cost_per_million`,
`output_token_cost_per_million`, `usage_unit`, `usage_level`, and
`estimate_cost(input_tokens, output_tokens)`.

## Run Example

```sh
./bin/python/03_prompt_builder.sh
```
