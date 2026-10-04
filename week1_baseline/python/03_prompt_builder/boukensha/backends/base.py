from __future__ import annotations

from typing import Any, ClassVar, Optional
from ..errors import UnsupportedModelError


class Base:
    """Abstract base class for LLM backends."""

    MODELS: ClassVar[dict[str, dict[str, Any]]]

    def __init__(self, model: str) -> None:
        self.model: str
        self._model_info: dict[str, Any]
        self._configure_model(model)

    @classmethod
    def models(cls) -> dict[str, dict[str, Any]]:
        if not hasattr(cls, "MODELS"):
            raise NotImplementedError(f"{cls.__name__} must define MODELS")
        return cls.MODELS

    @classmethod
    def model_info_for(cls, model: str) -> Optional[dict[str, Any]]:
        return cls.models().get(str(model))

    @classmethod
    def validate_model(cls, model: str) -> str:
        m = str(model)
        if cls.model_info_for(m) is not None:
            return m
        supported = ", ".join(sorted(cls.models().keys()))
        raise UnsupportedModelError(
            f"{cls.__name__} does not support model {repr(m)}. Supported models: {supported}"
        )

    @property
    def model_info(self) -> dict[str, Any]:
        return self._model_info

    @property
    def context_window(self) -> int:
        return self.model_info["context_window"]

    @property
    def input_token_cost_per_million(self) -> Optional[float]:
        cost = self.model_info.get("cost_per_million")
        return cost.get("input") if cost else None

    @property
    def output_token_cost_per_million(self) -> Optional[float]:
        cost = self.model_info.get("cost_per_million")
        return cost.get("output") if cost else None

    @property
    def usage_unit(self) -> str:
        return self.model_info["usage_unit"]

    @property
    def usage_level(self) -> Optional[str]:
        return self.model_info.get("usage_level")

    def estimate_cost(self, input_tokens: int, output_tokens: int) -> Optional[float]:
        in_cost = self.input_token_cost_per_million
        out_cost = self.output_token_cost_per_million
        if in_cost is None or out_cost is None:
            return None
        return ((input_tokens * in_cost) + (output_tokens * out_cost)) / 1_000_000.0

    def _configure_model(self, model: str) -> None:
        self.model = self.validate_model(model)
        info = self.model_info_for(self.model)
        assert info is not None
        self._model_info = info
