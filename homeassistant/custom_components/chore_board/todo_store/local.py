"""Local JSON file storage using HA StorageHelper."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import storage

from .base import Task, TodoStore

_LOGGER = logging.getLogger(__name__)

_STORE_KEY = "chore_board_local"


class LocalTodoStore(TodoStore):
    """Local storage using HA's StorageHelper."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = storage.Storage(hass, storage.STORAGE_VERSION, _STORE_KEY, write_version=1)
        self._tasks: dict[str, Task] = {}
        self._lock = asyncio.Lock()

    async def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Load stored tasks."""
        data = await self._store.async_load()
        if data:
            self._tasks = {t["id"]: Task(**t) for t in data.get("tasks", [])}

    async def list_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    async def create_task(self, title: str, notes: str | None = None) -> Task:
        async with self._lock:
            task_id = f"local-{len(self._tasks) + 1}"
            task = Task(id=task_id, title=title, notes=notes)
            self._tasks[task_id] = task
            await self._save()
        return task

    async def complete_task(self, task_id: str) -> Task:
        async with self._lock:
            if task_id not in self._tasks:
                raise ValueError(f"Task {task_id} not found")
            self._tasks[task_id] = Task(**{**self._tasks[task_id].__dict__, "completed": True})
            await self._save()
            return self._tasks[task_id]

    async def delete_task(self, task_id: str) -> bool:
        async with self._lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            await self._save()
            return True

    async def sync_with_chores(self, chores_data: dict[str, Any]) -> None:
        """Sync local tasks to match active chores."""
        async with self._lock:
            # Remove tasks for chores that no longer exist
            active_chore_ids = set(chores_data.keys())
            to_remove = [tid for tid in self._tasks if tid not in active_chore_ids and tid.startswith("chore-")]
            for tid in to_remove:
                del self._tasks[tid]

            # Create tasks for new chores
            for chore_id, chore_info in chores_data.items():
                if chore_id not in self._tasks and chore_info.get("active", True):
                    self._tasks[chore_id] = Task(
                        id=chore_id,
                        title=chore_info["title"],
                        notes=f"points:{chore_info.get('points', 10)}",
                    )

            await self._save()

    async def _save(self) -> None:
        tasks_list = [t.__dict__ for t in self._tasks.values()]
        await self._store.async_save({"tasks": tasks_list})
