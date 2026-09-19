"""Abstract base class for todo stores."""

from __future__ import annotations

import asyncio
import dataclasses
from abc import ABC, abstractmethod
from typing import Any


@dataclasses.dataclass
class Task:
    """A task in the todo store."""

    id: str
    title: str
    completed: bool = False
    notes: str | None = None


class TodoStore(ABC):
    """Abstract interface for todo store backends."""

    @abstractmethod
    async def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize the store (auth, connections, etc.)."""

    @abstractmethod
    async def list_tasks(self) -> list[Task]:
        """List all tasks from the store."""

    @abstractmethod
    async def create_task(self, title: str, notes: str | None = None) -> Task:
        """Create a new task and return it."""

    @abstractmethod
    async def complete_task(self, task_id: str) -> Task:
        """Mark a task as completed."""

    @abstractmethod
    async def delete_task(self, task_id: str) -> bool:
        """Delete a task. Returns True if it existed."""

    @abstractmethod
    async def sync_with_chores(self, chores_data: dict[str, Any]) -> None:
        """Sync chore definitions to this store's task list.

        Ensures tasks exist for all active chores. Removes tasks for
        chores that are no longer active.
        """
