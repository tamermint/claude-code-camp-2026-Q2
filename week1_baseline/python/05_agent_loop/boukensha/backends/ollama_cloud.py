from __future__ import annotations

from typing import Any, ClassVar
from .ollama import Ollama


class OllamaCloud(Ollama):
    """Ollama Cloud backend serializer and response normalizer."""

    BASE_URL = "https://ollama.com"

    MODELS: ClassVar[dict[str, dict[str, Any]]] = {
        "mistral-small:24b": {
            "context_window": 32_768,
            "cost_per_million": {"input": 0.50, "output": 1.50},
            "usage_unit": "tokens",
        },
        "phi4:14b": {
            "context_window": 16_384,
            "cost_per_million": {"input": 0.20, "output": 0.80},
            "usage_unit": "tokens",
        },
        "qwen2.5:7b": {
            "context_window": 32_768,
            "cost_per_million": {"input": 0.15, "output": 0.60},
            "usage_unit": "tokens",
        },
        "qwen2.5:14b": {
            "context_window": 32_768,
            "cost_per_million": {"input": 0.30, "output": 1.20},
            "usage_unit": "tokens",
        },
        "qwen2.5:32b": {
            "context_window": 32_768,
            "cost_per_million": {"input": 0.70, "output": 2.80},
            "usage_unit": "tokens",
        },
        "llama3.3:70b": {
            "context_window": 131_072,
            "cost_per_million": {"input": 0.90, "output": 3.60},
            "usage_unit": "tokens",
        },
        "deepseek-r1:14b": {
            "context_window": 131_072,
            "cost_per_million": {"input": 0.40, "output": 1.60},
            "usage_unit": "tokens",
        },
        "deepseek-r1:32b": {
            "context_window": 131_072,
            "cost_per_million": {"input": 0.80, "output": 3.20},
            "usage_unit": "tokens",
        },
        "deepseek-r1:70b": {
            "context_window": 131_072,
            "cost_per_million": {"input": 1.20, "output": 4.80},
            "usage_unit": "tokens",
        },
    }

    def __init__(self, api_key: str, model: str, host: str = BASE_URL) -> None:
        self.api_key = api_key
        super().__init__(model=model, host=host)

    @property
    def headers(self) -> dict[str, str]:
        return {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
