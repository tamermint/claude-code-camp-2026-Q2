from __future__ import annotations

from pathlib import Path
from typing import Any, Optional


class Base:
    """Abstract base class for Boukensha tasks.

    All behavior is expressed via class methods operating on a task's settings dictionary.
    """

    @classmethod
    def task_name(cls) -> str:
        raise NotImplementedError(f"{cls.__name__} must define task_name")

    @classmethod
    def provider(cls, settings: dict[str, Any]) -> str:
        val = cls._fetch(settings, "provider")
        if not val:
            raise ValueError(f"tasks.{cls.task_name()}.provider is required in settings.yml")
        return str(val)

    @classmethod
    def model(cls, settings: dict[str, Any]) -> str:
        val = cls._fetch(settings, "model")
        if not val:
            raise ValueError(f"tasks.{cls.task_name()}.model is required in settings.yml")
        return str(val)

    @classmethod
    def prompt_override(cls, settings: dict[str, Any], prompt: str = "system") -> bool:
        node = cls._fetch(settings, "prompt_override")
        if not isinstance(node, dict):
            return False
        return node.get(str(prompt)) is True

    @classmethod
    def prompt(
        cls,
        settings: dict[str, Any],
        name: str = "system",
        user_prompts_dir: Optional[str | Path] = None,
        default_prompts_dir: Optional[str | Path] = None,
    ) -> Optional[str]:
        if cls.prompt_override(settings, name):
            text = cls.read_user_prompt(name, user_prompts_dir=user_prompts_dir)
            if text is not None:
                return text

        return cls.read_default_prompt(name, default_prompts_dir=default_prompts_dir)

    @classmethod
    def system_prompt(
        cls,
        settings: dict[str, Any],
        user_prompts_dir: Optional[str | Path] = None,
        default_prompts_dir: Optional[str | Path] = None,
    ) -> Optional[str]:
        return cls.prompt(
            settings,
            name="system",
            user_prompts_dir=user_prompts_dir,
            default_prompts_dir=default_prompts_dir,
        )

    @classmethod
    def read_user_prompt(
        cls,
        prompt_name: str,
        user_prompts_dir: Optional[str | Path] = None,
    ) -> Optional[str]:
        if not user_prompts_dir:
            return None
        path = Path(user_prompts_dir) / cls.task_name() / f"{prompt_name}.md"
        return cls._read_file(path)

    @classmethod
    def read_default_prompt(
        cls,
        prompt_name: str,
        default_prompts_dir: Optional[str | Path] = None,
    ) -> Optional[str]:
        if not default_prompts_dir:
            return None
        path = Path(default_prompts_dir) / f"{prompt_name}.md"
        return cls._read_file(path)

    @classmethod
    def _fetch(cls, settings: Optional[dict[str, Any]], key: str) -> Any:
        if not isinstance(settings, dict):
            return None
        return settings.get(key)

    @staticmethod
    def _read_file(path: Path | str) -> Optional[str]:
        p = Path(path)
        if p.is_file():
            return p.read_text(encoding="utf-8").strip()
        return None
