"""Abstract base class for todo stores."""

from __future__ import annotations

import dataclasses
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any


@dataclasses.dataclass
class Task:
    """A task in the todo store."""

    id: str
    title: str
    completed: bool = False
    notes: str | None = None
    completed_at: datetime | None = None


@dataclasses.dataclass
class StoreChanges:
    """Delta report from a poll."""

    new_tasks: list[Task] = dataclasses.field(default_factory=list)
    completed_tasks: list[Task] = dataclasses.field(default_factory=list)
    deleted_tasks: list[str] = dataclasses.field(default_factory=list)


class TodoStore(ABC):
    """Abstract interface for todo store backends.

    Source of truth for tasks. HA polls for changes and attributes
    completions to household members.
    """

    @abstractmethod
    async def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the store (auth, connections, etc.)."""

    @abstractmethod
    async def poll(self) -> StoreChanges:
        """Return changes since last poll.

        Must be idempotent — calling twice with no external changes
        returns empty deltas. Uses an internal sync token/pointer.
        """

    @abstractmethod
    async def list_tasks(self) -> list[Task]:
        """List all current tasks (for display)."""

    @abstractmethod
    async def sync_with_chores(self, chores_data: dict[str, Any]) -> None:
        """Ensure tasks exist for all active chores.

        Called once at startup to bootstrap. Does not affect polling.
        """
