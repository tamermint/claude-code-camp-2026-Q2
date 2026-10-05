from __future__ import annotations


class BoukenshaError(Exception):
    """Base exception for all Boukensha errors."""
    pass


class UnknownToolError(BoukenshaError):
    """Raised when dispatching a tool that has not been registered."""
    pass


class UnsupportedModelError(BoukenshaError):
    """Raised when an unrecognized model is specified for a backend."""
    pass


class ApiError(BoukenshaError):
    """Raised when an HTTP request to an LLM provider fails."""
    pass
