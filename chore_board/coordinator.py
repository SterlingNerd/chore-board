"""Coordinator — polling + state management."""

from __future__ import annotations

from typing import Optional


class ChoreBoardCoordinator:
    """Central coordinator that polls todo store and manages state."""

    def __init__(
        self,
        chore_manager: object,
        member_manager: object,
        scoring_engine: object,
        attribution_manager: object,
        todo_store: object,
    ) -> None:
        self._chore_manager = chore_manager
        self._member_manager = member_manager
        self._scoring_engine = scoring_engine
        self._attribution_manager = attribution_manager
        self._todo_store = todo_store
        self._poll_interval = 30  # seconds
        self._running = False

    async def async_poll(self) -> list[dict]:
        """Poll the todo store and return detected changes."""
        changes = await self._todo_store.async_poll()
        return changes

    async def async_shutdown(self) -> None:
        """Clean shutdown."""
        self._running = False
