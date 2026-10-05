# Walkthrough: Porting week1_baseline from Ruby to Python

## Overview
This walkthrough documents the Python ports of `week1_baseline` components from Ruby to Python, ensuring strict environment isolation via project-local `.venv`s and complete behavioral parity with the Ruby baselines.

---

## Step 0: `00_config`

- **Port Plan**: [docs/plans/python_port/00_config](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/docs/plans/python_port/00_config)
- **Source**: [week1_baseline/ruby/00_config](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/ruby/00_config)
- **Python Port**: [week1_baseline/python/00_config](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/00_config)
- **Runner Script**: [week1_baseline/bin/python/00_config.sh](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/bin/python/00_config.sh)

### Key Implementations
- [`boukensha.Config`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/00_config/boukensha/config.py#L11): Resolves `BOUKENSHA_DIR` / `~/.boukensha`, loads credentials from `.env`, loads settings from `settings.yml`, exposes `mud_*` properties and `dig()`.
- [`boukensha.tasks.Base`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/00_config/boukensha/tasks/base.py#L7) & [`boukensha.tasks.Player`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/00_config/boukensha/tasks/player.py#L6): Stateless task classes managing task name, provider, model, and prompt resolution.

---

## Step 1: `01_struct_skeleton`

- **Port Plan**: [docs/plans/python_port/01_struct_skeleton](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/docs/plans/python_port/01_struct_skeleton)
- **Source**: [week1_baseline/ruby/01_struct_skeleton](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/ruby/01_struct_skeleton)
- **Python Port**: [week1_baseline/python/01_struct_skeleton](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/01_struct_skeleton)
- **Runner Script**: [week1_baseline/bin/python/01_struct_skeleton.sh](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/bin/python/01_struct_skeleton.sh)

### Architecture & Reuse
Step 1 directly inherits the validated foundation from `python/00_config` (`config.py`, `tasks/`, `requirements.txt`, `prompts/system.md`), and adds the core in-memory agent turn data structures:

| Python Component | Ruby Equivalent | Details |
| :--- | :--- | :--- |
| [`boukensha.Tool`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/01_struct_skeleton/boukensha/tool.py#L8) | `Boukensha::Tool` | `@dataclass` holding `name`, `description`, `parameters`, and `block` callable, formatted with `params=[:direction]`. |
| [`boukensha.Message`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/01_struct_skeleton/boukensha/message.py#L8) | `Boukensha::Message` | `@dataclass` holding `role`, `content`, and optional `tool_use_id`, formatted with `role=... [tool_use_id] content=...`. |
| [`boukensha.Context`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/01_struct_skeleton/boukensha/context.py#L9) | `Boukensha::Context` | Session container managing `@task`, `@system`, `@messages`, `@tools`, `register_tool()`, `add_message()`, and counter properties. |
| [`boukensha/__init__.py`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/01_struct_skeleton/boukensha/__init__.py) | `boukensha.rb` | Re-exports `Config`, `tasks`, `Base`, `Player`, `Tool`, `Message`, and `Context`. |
| [`examples/example.py`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/01_struct_skeleton/examples/example.py) | `examples/example.rb` | Runnable verification script instantiating Context, registering a `move` tool with a lambda, and adding messages. |

---

## Step 2: `02_the_registry`

- **Port Plan**: [docs/plans/python_port/02_the_registry](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/docs/plans/python_port/02_the_registry)
- **Source**: [week1_baseline/ruby/02_the_registry](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/ruby/02_the_registry)
- **Python Port**: [week1_baseline/python/02_the_registry](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/02_the_registry)
- **Runner Script**: [week1_baseline/bin/python/02_the_registry.sh](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/bin/python/02_the_registry.sh)

### Architectural Changes & Refinements
Step 2 decouples tool registration and tool dispatching from `Context` into a dedicated `Registry` component:
- **`Context`**: Streamlined to strictly manage conversation turns (`task`, `system`, `messages`, `turn_count`). Its string representation renders `#<Context task=player turns=0>` without referencing tools.
- **`Registry`**: Solely responsible for tool registration and tool dispatch:
  - `self.tools: dict[str, Tool]`
  - `tool(name, description, parameters, block)` supporting both direct block passing and idiomatic Python decorator `@registry.tool(...)`.
  - `dispatch(name, args)`: looks up the tool by name, raises `UnknownToolError` if missing, unmarshals arguments, and invokes the underlying function/block.
- **`UnknownToolError`**: Explicit error class inheriting from `BoukenshaError`, preventing silent dispatch failures.

| Python Component | Ruby Equivalent | Details |
| :--- | :--- | :--- |
| [`boukensha.Registry`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/02_the_registry/boukensha/registry.py#L9) | `Boukensha::Registry` | Manages tool registration via `register_tool`/`tool` and dispatching via `dispatch`. |
| [`boukensha.errors.UnknownToolError`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/02_the_registry/boukensha/errors.py#L9) | `Boukensha::UnknownToolError` | Raised when invoking a non-registered tool. |
| [`boukensha.Context`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/02_the_registry/boukensha/context.py#L8) | `Boukensha::Context` | Decoupled session container tracking turns only. |
| [`boukensha.Tool`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/02_the_registry/boukensha/tool.py#L9) | `Boukensha::Tool` | Dataclass representing an executable tool, callable directly or via dispatch. |
| [`examples/example.py`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/02_the_registry/examples/example.py) | `examples/example.rb` | Registers `move` and `shout`, displays config/context/tools, dispatches calls, and tests `UnknownToolError`. |

---

## Step 3: `03_prompt_builder`

- **Port Plan**: [docs/plans/python_port/03_prompt_builder](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/docs/plans/python_port/03_prompt_builder)
- **Source**: [week1_baseline/ruby/03_prompt_builder](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/ruby/03_prompt_builder)
- **Python Port**: [week1_baseline/python/03_prompt_builder](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/03_prompt_builder)
- **Runner Script**: [week1_baseline/bin/python/03_prompt_builder.sh](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/bin/python/03_prompt_builder.sh)

### Multi-Backend Serialization Architecture
Step 3 introduces the `PromptBuilder` abstraction and 5 concrete LLM backend serializers that convert conversation turns and tool schemas into provider-specific API payloads:

| Python Component | Provider / Purpose | Distinct Payload Formatting |
| :--- | :--- | :--- |
| [`boukensha.PromptBuilder`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/03_prompt_builder/boukensha/prompt_builder.py#L11) | Serializer Orchestrator | Delegates `to_messages`, `to_tools`, and `to_api_payload` to the active backend. |
| [`boukensha.backends.Gemini`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/03_prompt_builder/boukensha/backends/gemini.py#L7) | Google Gemini | `systemInstruction`, `contents` with `model` and `functionResponse`, `functionDeclarations`. |
| [`boukensha.backends.Anthropic`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/03_prompt_builder/boukensha/backends/anthropic.py#L7) | Anthropic Claude | Top-level `system`, `tool_result` content blocks in user turns, `input_schema` tools. |
| [`boukensha.backends.OpenAI`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/03_prompt_builder/boukensha/backends/openai.py#L7) | OpenAI Chat Completions | Initial `role: "system"` message, `role: "tool"` with `tool_call_id`, `type: "function"` tools. |
| [`boukensha.backends.Ollama`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/03_prompt_builder/boukensha/backends/ollama.py#L7) | Local Ollama | Initial `role: "system"` message, `role: "tool"` with `tool_name`, `stream: False`. |
| [`boukensha.backends.OllamaCloud`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/03_prompt_builder/boukensha/backends/ollama_cloud.py#L7) | Ollama Cloud | Same message schema as Ollama, cloud model table and `Authorization: Bearer <key>` header. |
| [`boukensha.errors.UnsupportedModelError`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/03_prompt_builder/boukensha/errors.py#L14) | Model Validation | Raised if an unrecognized model name is passed to any backend constructor. |

---

## Step 4: `04_api_client`

- **Port Plan**: [docs/plans/python_port/04_api_client](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/docs/plans/python_port/04_api_client)
- **Source**: [week1_baseline/ruby/04_api_client](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/ruby/04_api_client)
- **Python Port**: [week1_baseline/python/04_api_client](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/04_api_client)
- **Runner Script**: [week1_baseline/bin/python/04_api_client.sh](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/bin/python/04_api_client.sh)

### Stateless HTTP Transport Architecture
Step 4 introduces `Client`, the HTTP transport layer that sends requests to provider endpoints and unmarshals JSON responses:
- **Stateless Client**: Unlike the course author's initial draft that bound `Client` to a single `PromptBuilder` at initialization, `Client` is strictly stateless. It stores only retry policies (`max_retries`, `base_retry_delay`), and accepts `builder` on each `call(builder, max_output_tokens=1024)`. This allows a single `Client` instance to live across turns throughout the agent loop.
- **Built-in Retries with Exponential Backoff**: Automatically handles transient socket errors (`TimeoutError`, `ConnectionResetError`, `ssl.SSLError`, `urllib.error.URLError`) and retryable status codes (`408, 409, 429, 500, 502, 503, 504`) with exponential delay.
- **Zero Heavy External Dependencies**: Built with Python standard library `urllib.request`, `ssl`, and `json`.
- **`ApiError`**: Explicit error boundary raised on terminal request failure with status code and body.

| Python Component | Ruby Equivalent | Details |
| :--- | :--- | :--- |
| [`boukensha.Client`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/04_api_client/boukensha/client.py#L21) | `Boukensha::Client` | Stateless HTTP transport client with retry policies. |
| [`boukensha.errors.ApiError`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/04_api_client/boukensha/errors.py#L19) | `Boukensha::ApiError` | Raised on non-2xx responses or exhausted retries. |
| [`examples/example.py`](file:///Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/week1_baseline/python/04_api_client/examples/example.py) | `examples/example.rb` | Registers tools, creates PromptBuilder and stateless Client, dispatches live API call, and prints candidate response. |

---

## Environment Isolation & Shared Virtual Environment

All Python implementations are strictly isolated from the global system:
- All ported subsystems share the root virtual environment (`.venv/`) located at the repository root.
- Duplicate `.venv` directories inside individual step folders have been cleaned up to prevent repository bloat.
- Runner scripts dynamically resolve `$ROOT_DIR/.venv` and ensure requirements from `requirements.txt` are satisfied via `"$VENV_DIR/bin/pip"`.
- Scripts execute via `"$VENV_DIR/bin/python"`.
- `.gitignore` ignores `.venv/`, `__pycache__/`, and `*.pyc`.

---

## Verification & Parity Results

### Step 3 Parity Check
Ran Ruby baseline:
```bash
bash week1_baseline/bin/ruby/03_prompt_builder.sh
```

Ran Python port:
```bash
bash week1_baseline/bin/python/03_prompt_builder.sh
```

**Output Comparison**:

```
=== BOUKENSHA Step 3: Prompt Builder ===

Config: #<Boukensha::Config dir=/Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/.boukensha tasks=player>
Provider: gemini
Model: gemini-3.8-flash
{
  "systemInstruction": {
    "parts": [
      {
        "text": "You are a MUD Journey player Agent. \n\nYou are playing the MUD on behalf of the player and the player will issue you goals to complete.\n\nUse the tools available to you to help the player explore, fight, and interact with the world."
      }
    ]
  },
  "contents": [
    {
      "role": "user",
      "parts": [
        {
          "text": "I just arrived in the dungeon. What's around me, and can you move north?"
        }
      ]
    },
    {
      "role": "model",
      "parts": [
        {
          "text": "Let me take a look around first."
        }
      ]
    },
    {
      "role": "user",
      "parts": [
        {
          "functionResponse": {
            "name": "toolu_01X",
            "response": {
              "content": "A damp stone corridor stretches north. Torches flicker on the walls."
            }
          }
        }
      ]
    }
  ],
  "tools": [
    {
      "functionDeclarations": [
        {
          "name": "look",
          "description": "Look around the current room for details",
          "parameters": {
            "type": "object",
            "properties": {},
            "required": []
          }
        },
        {
          "name": "move",
          "description": "Move the player in a direction (north, south, east, west, up, down)",
          "parameters": {
            "type": "object",
            "properties": {
              "direction": {
                "type": "string",
                "description": "The direction to move"
              }
            },
            "required": [
              "direction"
            ]
          }
        }
      ]
    }
  ],
  "generationConfig": {
    "maxOutputTokens": 1024
  }
}
```

The outputs are 100% identical.

### Unit & Multi-Backend Validation
Executed test suite covering all 5 backends:
```bash
.venv/bin/python week1_baseline/python/03_prompt_builder/tests/test_prompt_builder.py
```
**Results**:
- `✓ Gemini backend tests passed`
- `✓ Anthropic backend tests passed`
- `✓ OpenAI backend tests passed`
- `✓ Ollama backend tests passed`
- `✓ OllamaCloud backend tests passed`
- `✓ UnsupportedModelError validation passed`
- `All 6 test suites passed successfully!`

### Step 4 Parity Check
Ran Ruby baseline:
```bash
bash week1_baseline/bin/ruby/04_api_client.sh
```

Ran Python port:
```bash
bash week1_baseline/bin/python/04_api_client.sh
```

**Output Comparison**:
Both runners transmit the request to `https://generativelanguage.googleapis.com/...` and receive the exact same live candidate function call response:
```json
{
  "candidates": [
    {
      "content": {
        "parts": [
          {
            "functionCall": {
              "name": "list_directory",
              "args": {
                "path": "."
              }
            }
          }
        ],
        "role": "model"
      },
      "finishReason": "STOP",
      "index": 0,
      "finishMessage": "Model generated function call(s)."
    }
  ]
}
```

### Step 4 Unit Tests
Executed automated client test suite:
```bash
.venv/bin/python week1_baseline/python/04_api_client/tests/test_client.py
```
**Results**:
- `✓ test_client_success passed`
- `✓ test_client_retryable_status passed`
- `✓ test_client_fatal_http_error passed`
- `✓ test_client_exhausted_retries passed`
- `✓ test_client_transient_network_error passed`
- `All 5 Client tests passed successfully!`

