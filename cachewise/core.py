"""Estimador de tokens (heuristica chars/4)."""


def estimate_tokens(text: str) -> int:
    """Cuenta tokens aproximados de un texto (heuristica caracteres/4)."""
    if not text:
        return 0
    return max(1, len(text) // 4)
