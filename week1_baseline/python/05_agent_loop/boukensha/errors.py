from __future__ import annotations


class BoukenshaError(Exception):
    """Base exception for all Boukensha domain errors."""


class UnknownToolError(BoukenshaError):
    """Raised when attempting to invoke a tool that has not been registered."""


class UnsupportedModelError(BoukenshaError):
    """Raised when a model is not recognized by a backend."""


class ApiError(BoukenshaError):
    """Raised when an HTTP call to an LLM provider fails."""


class LoopError(BoukenshaError):
    """Raised when an agent loop encounters an unrecoverable iteration/turn issue."""
