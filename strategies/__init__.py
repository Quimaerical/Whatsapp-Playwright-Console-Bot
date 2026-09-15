"""Módulo de estrategias de envío aplicando el Patrón Strategy."""

from .send_strategies import (
    BaseSendStrategy,
    DirectUrlStrategy,
    SearchContactStrategy,
    get_strategy,
)

__all__ = [
    "BaseSendStrategy",
    "DirectUrlStrategy",
    "SearchContactStrategy",
    "get_strategy",
]
