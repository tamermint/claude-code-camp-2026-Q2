import os
import sys
from pathlib import Path

# Add python/00_config to sys.path so 'boukensha' can be imported without installation
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from boukensha import Config, tasks

# Override the config directory so the example works from the repo root.
# In real usage a user's ~/.boukensha is picked up automatically.
if "BOUKENSHA_DIR" not in os.environ:
    repo_boukensha = Path(__file__).resolve().parents[4] / ".boukensha"
    os.environ["BOUKENSHA_DIR"] = str(repo_boukensha)

config = Config()
player_settings = config.tasks("player")

print("=== Boukensha Step 0: Configuration ===")
print()
print(f"Config dir:     {config.dir}")
print(f"Tasks:          {', '.join(config.tasks().keys())}")
print()
print("-- player task --")
print(f"Provider:       {tasks.Player.provider(player_settings)}")
print(f"Model:          {tasks.Player.model(player_settings)}")
override_flag = "true" if tasks.Player.prompt_override(player_settings, "system") else "false"
print(f"Prompt override?{override_flag}")
prompt_text = tasks.Player.system_prompt(
    player_settings,
    user_prompts_dir=config.user_prompts_dir,
    default_prompts_dir=Config.PROMPTS_DIR,
)
prompt_snippet = (prompt_text[:60] if prompt_text else "") + "..."
print(f"System prompt:  {prompt_snippet}")
print()
print(f"MUD host:       {config.mud_host}:{config.mud_port}")
print(f"MUD user:       {config.mud_username}")
print()
api_key_set = "true" if os.environ.get("GEMINI_API_KEY") else "false"
print(f"API key set?    {api_key_set}")
print()
print(config)
