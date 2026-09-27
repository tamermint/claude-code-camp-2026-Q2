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

## Environment Isolation

All Python implementations are strictly isolated from the global system:
- Each subsystem provisions a local `.venv` inside its own folder (`week1_baseline/python/<step>/.venv`).
- Dependencies from `requirements.txt` are installed exclusively inside `"$VENV_DIR/bin/pip"`.
- Scripts execute via `"$VENV_DIR/bin/python"`.
- `.gitignore` ignores `.venv/`, `__pycache__/`, and `*.pyc`.

---

## Verification & Parity Results

### Step 2 Parity Check
Ran Ruby baseline:
```bash
bash week1_baseline/bin/ruby/02_the_registry.sh
```

Ran Python port:
```bash
bash week1_baseline/bin/python/02_the_registry.sh
```

**Output Comparison**:

```
=== BOUKENSHA Step 2: Tool Registry ===

Config:  #<Boukensha::Config dir=/Users/vivekmitra/Desktop/Learn2Code/Anthropic/claude-code-camp-2026-Q2/.boukensha tasks=player>
Context: #<Context task=player turns=0>
Tools:
  #<Tool name=move description=Move the player in a direction (north, so params=[:direction]>
  #<Tool name=shout description=Shout a message so everyone in the zone c params=[:message]>

Dispatching 'shout' with message='dragon spotted'...
Result: DRAGON SPOTTED

Dispatching 'move' with direction='north'...
Result: You move north into a torch-lit corridor.

UnknownToolError caught: No tool registered as 'flee'
```

The outputs are 100% identical.
