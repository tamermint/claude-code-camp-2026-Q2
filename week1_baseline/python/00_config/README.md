# 00 · Configuration (Python Port)

We want to be able to manage all configurations from an external file, e.g. `~/.boukensha/settings.yml`.
We have a dedicated class to handle configuration: `boukensha.Config`.
As we add configuration in each iteration, we will update the configuration schema and class.
We can hardcode defaults, but we should not hardcode configurable values.

Configuration is organised by **task** — a role in the agentic loop bound to its own LLM. `week1_baseline` drives a single `player` task (the main loop), but a more advanced loop will assign different LLMs to different tasks.

---

## Design Considerations

We aim to keep external dependencies minimal:
- `pyyaml` for parsing YAML configuration (`settings.yml`).
- `python-dotenv` for loading environment variables from `.env`.

Dependencies are managed via `requirements.txt`.

---

## Code Structure

| File | Purpose |
| :--- | :--- |
| `boukensha/config.py` | `boukensha.Config` configuration loader class |
| `boukensha/tasks/base.py` | Abstract `boukensha.tasks.Base` task class (provider/model and prompt resolution) |
| `boukensha/tasks/player.py` | Concrete `boukensha.tasks.Player` task class (the player loop) |
| `boukensha/__init__.py` | Top-level package exports |
| `prompts/system.md` | Default system prompt shipped with the library |
| `examples/example.py` | Runnable smoke-test and verification script |
| `requirements.txt` | Minimal pip dependencies (`pyyaml`, `python-dotenv`) |

---

## Config Directory Resolution

The `Config` class resolves the `.boukensha/` directory in this order:

1. **`BOUKENSHA_DIR` environment variable** — set this to point to any directory.
2. **`~/.boukensha`** — the default location for local installation.

### Config Directory Structure

```
.boukensha/
  .env                 # Credentials, e.g. GEMINI_API_KEY (never committed)
  settings.yml         # Non-secret task and environment settings
  prompts/
    <task>/
      system.md        # Per-task override for default system prompt (optional)
```

---

## Tasks

`boukensha.tasks.Base` is an abstract stateless class whose behavior is expressed via class methods taking a `settings` dictionary. Concrete subclasses define `task_name()`.

`Config.tasks()` returns the dictionary of tasks from `settings.yml`. Pass a task name to retrieve a specific task's settings:

```python
from boukensha import Config, tasks

config = Config()
player_settings = config.tasks("player")

provider = tasks.Player.provider(player_settings)
system_prompt = tasks.Player.system_prompt(
    player_settings,
    user_prompts_dir=config.user_prompts_dir,
    default_prompts_dir=Config.PROMPTS_DIR,
)
```

---

## System Prompt Resolution

Per task, `tasks.Player.system_prompt(...)` resolves prompts in this order:

1. **`.boukensha/prompts/<task>/system.md`** — used when `prompt_override.system` is `true` in `settings.yml` and the file exists.
2. **`prompts/system.md`** — the default system prompt shipped with the library.

---

## Configuration Schema

```yaml
tasks:
  player:
    provider: gemini        # provider name (string)
    model: gemini-3.5-flash
    prompt_override:
      system: true
mud:
  host: localhost
  port: 4000
  username: dummy
  password: helloworld
```

---

## Run Example

```bash
./week1_baseline/bin/00_config_py.sh
```

Expected output:

```
=== Boukensha Step 0: Configuration ===

Config dir:     /Users/.../claude-code-camp-2026-Q2/.boukensha
Tasks:          player

-- player task --
Provider:       gemini
Model:          gemini-3.5-flash
Prompt override?true
System prompt:  You are a MUD Journey player Agent. 

You are playing the MU...

MUD host:       localhost:4000
MUD user:       dummy

API key set?    true

#<Boukensha::Config dir=/Users/.../claude-code-camp-2026-Q2/.boukensha tasks=player>
```
