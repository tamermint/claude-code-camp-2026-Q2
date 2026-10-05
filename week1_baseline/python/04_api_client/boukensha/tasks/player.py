from __future__ import annotations

from .base import Base


class Player(Base):
    """Concrete task representing the main player loop."""

    @classmethod
    def task_name(cls) -> str:
        return "player"
