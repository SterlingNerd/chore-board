"""HA Todo List adapter."""

from __future__ import annotations

from .base import TodoStore


class HATodoStore(TodoStore):
    """Todo store backed by HA's todo.get_items service."""

    def __init__(self, hass: object) -> None:
        self._hass = hass
        self._seen_uids: set[str] = set()

    async def async_initialize(self) -> None:
        """Initialize — in real impl, would fetch current items from HA."""
        pass

    async def async_poll(self) -> list[dict]:
        """Poll for changes. Returns list of change dicts."""
        # In real impl, would call todo.get_items and diff against _seen_uids
        return []

    async def async_list(self) -> list[dict]:
        """List all current items."""
        # In real impl, would call todo.get_items
        return []
