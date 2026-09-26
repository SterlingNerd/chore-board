"""Abstract base class for todo store backends."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class TodoStore(ABC):
    """ABC for todo store backends."""

    @abstractmethod
    async def async_initialize(self) -> None:
        """Initialize the store."""
        ...

    @abstractmethod
    async def async_poll(self) -> list[dict]:
        """Poll for changes. Returns list of change dicts."""
        ...

    @abstractmethod
    async def async_list(self) -> list[dict]:
        """List all current items."""
        ...
