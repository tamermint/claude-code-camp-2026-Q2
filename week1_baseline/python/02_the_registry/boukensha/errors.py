from __future__ import annotations


class BoukenshaError(Exception):
    """Base exception for Boukensha errors."""
    pass


class UnknownToolError(BoukenshaError):
    """Raised when dispatching a tool that has not been registered."""
    pass
