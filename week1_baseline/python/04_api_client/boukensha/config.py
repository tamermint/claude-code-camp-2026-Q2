from __future__ import annotations

import os
from pathlib import Path
from typing import Any, Optional
import yaml
from dotenv import load_dotenv


class Config:
    """Configuration manager for Boukensha.

    Resolves configuration directory (~/.boukensha or BOUKENSHA_DIR),
    loads credentials from .env, and loads settings from settings.yml.
    """

    DEFAULT_DIR = Path.home() / ".boukensha"
    PROMPTS_DIR = Path(__file__).resolve().parent.parent / "prompts"

    def __init__(self, dir: Optional[str | Path] = None) -> None:
        self.dir: Path = self._resolve_dir(dir)
        self._load_env()
        self.settings: dict[str, Any] = self._load_settings()

    def tasks(self, name: Optional[str] = None) -> Any:
        """Return all task configurations, or settings for a specific task."""
        all_tasks = self.dig("tasks") or {}
        if name is not None:
            return all_tasks.get(str(name))
        return all_tasks

    @property
    def user_prompts_dir(self) -> Path:
        """Directory for user prompt overrides."""
        return self.dir / "prompts"

    @property
    def mud_host(self) -> str:
        return self.dig("mud", "host") or "localhost"

    @property
    def mud_port(self) -> int:
        return self.dig("mud", "port") or 4000

    @property
    def mud_username(self) -> Optional[str]:
        return self.dig("mud", "username")

    @property
    def mud_password(self) -> Optional[str]:
        return self.dig("mud", "password")

    def dig(self, *keys: str) -> Any:
        """Fetch a nested key path from settings, e.g. dig('mud', 'host')."""
        node: Any = self.settings
        for key in keys:
            if isinstance(node, dict):
                node = node.get(str(key))
            else:
                return None
        return node

    def __str__(self) -> str:
        task_names = ",".join(self.tasks().keys())
        return f"#<Boukensha::Config dir={self.dir} tasks={task_names}>"

    def __repr__(self) -> str:
        return self.__str__()

    def _resolve_dir(self, custom_dir: Optional[str | Path] = None) -> Path:
        if custom_dir is not None:
            raw = custom_dir
        else:
            raw = os.environ.get("BOUKENSHA_DIR") or self.DEFAULT_DIR
        return Path(raw).expanduser().resolve()

    def _load_env(self) -> None:
        env_file = self.dir / ".env"
        if env_file.is_file():
            load_dotenv(env_file)

    def _load_settings(self) -> dict[str, Any]:
        settings_file = self.dir / "settings.yml"
        if settings_file.is_file():
            with open(settings_file, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        return {}
