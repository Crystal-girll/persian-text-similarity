"""Small, local-first utilities for Persian text similarity."""

from .core import Match, TfidfIndex, normalize, tokens

__version__ = "0.1.0"
__all__ = ["Match", "TfidfIndex", "normalize", "tokens"]
