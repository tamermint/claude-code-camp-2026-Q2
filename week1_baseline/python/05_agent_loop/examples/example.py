from __future__ import annotations

import os
import sys
from pathlib import Path

# Add package directory to path if not installed
pkg_dir = Path(__file__).resolve().parent.parent
if str(pkg_dir) not in sys.path:
    sys.path.insert(0, str(pkg_dir))

# Resolve default BOUKENSHA_DIR
if "BOUKENSHA_DIR" not in os.environ:
    os.environ["BOUKENSHA_DIR"] = str(Path(__file__).resolve().parents[4] / ".boukensha")

from boukensha import Agent, Client, Config, Context, PromptBuilder, Registry, tasks
from boukensha.backends import Anthropic, Gemini, Ollama, OllamaCloud, OpenAI

config = Config()
player_settings = config.tasks("player")
system_prompt = tasks.Player.system_prompt(
    player_settings,
    user_prompts_dir=config.user_prompts_dir,
    default_prompts_dir=Config.PROMPTS_DIR,
)
base_dir = Path(__file__).resolve().parents[1]

ctx = Context(task=tasks.Player, system=system_prompt)
registry = Registry(ctx)

provider = tasks.Player.provider(player_settings)
model = tasks.Player.model(player_settings)

if provider == "anthropic":
    backend = Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"], model=model)
elif provider == "openai":
    backend = OpenAI(api_key=os.environ["OPENAI_API_KEY"], model=model)
elif provider == "gemini":
    backend = Gemini(api_key=os.environ["GEMINI_API_KEY"], model=model)
elif provider == "ollama":
    backend = Ollama(model=model)
elif provider == "ollama_cloud":
    backend = OllamaCloud(api_key=os.environ["OLLAMA_API_KEY"], model=model)
else:
    raise ValueError(f"Unsupported provider for player task: {provider}")

builder = PromptBuilder(ctx, backend)
client = Client()
agent = Agent(
    context=ctx,
    registry=registry,
    builder=builder,
    client=client,
    task_settings=player_settings,
)


@registry.tool(
    "read_file",
    description="Read the contents of a file from disk",
    parameters={"path": {"type": "string", "description": "The file path to read"}},
)
def read_file(path: str) -> str:
    target = (base_dir / path).resolve()
    return target.read_text(encoding="utf-8")


@registry.tool(
    "list_directory",
    description="List the files in a directory",
    parameters={"path": {"type": "string", "description": "The directory path to list"}},
)
def list_directory(path: str) -> str:
    target = (base_dir / path).resolve()
    return ", ".join(sorted([f.name for f in target.iterdir() if not f.name.startswith(".")]))


ctx.add_message("user", "Read the README.md file and summarise what this MUD player assistant framework can do.")

print("=== BOUKENSHA Step 5: Agent Loop ===\n")
print(f"Config: {config}")
print(f"Provider: {provider}")
print(f"Model: {model}")
print(f"Max iterations: {tasks.Player.max_iterations(player_settings)}")
print(f"Max output tokens: {tasks.Player.max_output_tokens(player_settings)}\n")

result = agent.run()

print("\n=== FINAL RESPONSE ===")
print(result)
