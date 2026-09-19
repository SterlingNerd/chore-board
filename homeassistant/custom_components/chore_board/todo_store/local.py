"""Local JSON storage using HA StorageHelper."""

from __future__ import annotations

import asyncio
import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import storage

from .base import StoreChanges, Task, TodoStore

_LOGGER = logging.getLogger(__name__)

_STORE_KEY = "chore_board_local"


class LocalTodoStore(TodoStore):
    """Local storage using HA's StorageHelper."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._store = storage.Storage(hass, 1, _STORE_KEY, write_version=1)
        self._tasks: dict[str, Task] = {}
        self._sync_token: int = 0  # monotonically increasing counter
        self._lock = asyncio.Lock()

    async def initialize(self, config: dict[str, Any] | None = None) -> None:
        data = await self._store.async_load()
        if data:
            self._tasks = {t["id"]: Task(**{k: v for k, v in t.items()}) for t in data.get("tasks", [])}
            self._sync_token = data.get("sync_token", 0)

    async def poll(self) -> StoreChanges:
        """Return changes since last poll."""
        async with self._lock:
            old_token = self._sync_token
            # Increment token (simulates a "write" cycle)
            self._sync_token += 1
            # We use the token to track if we've already processed these changes
            # In local mode, changes come from sync_with_chores or direct manipulation
            # For polling, we check if any tasks changed state since last read
            return StoreChanges()  # Local store: changes are applied synchronously

    async def list_tasks(self) -> list[Task]:
        return list(self._tasks.values())

    async def create_task(self, title: str, notes: str | None = None) -> Task:
        async with self._lock:
            task_id = f"local-{len(self._tasks) + 1}"
            task = Task(id=task_id, title=title, notes=notes)
            self._tasks[task_id] = task
            self._sync_token += 1
            await self._save()
        return task

    async def complete_task(self, task_id: str) -> Task:
        async with self._lock:
            if task_id not in self._tasks:
                raise ValueError(f"Task {task_id} not found")
            self._tasks[task_id] = Task(
                id=task_id,
                title=self._tasks[task_id].title,
                completed=True,
                notes=self._tasks[task_id].notes,
                completed_at=datetime.now(timezone.utc),
            )
            self._sync_token += 1
            await self._save()
            return self._tasks[task_id]

    async def delete_task(self, task_id: str) -> bool:
        async with self._lock:
            if task_id not in self._tasks:
                return False
            del self._tasks[task_id]
            self._sync_token += 1
            await self._save()
            return True

    async def sync_with_chores(self, chores_data: dict[str, Any]) -> None:
        """Sync local tasks to match active chores."""
        async with self._lock:
            to_remove = [tid for tid in self._tasks if tid.startswith("chore-") and tid not in chores_data]
            for tid in to_remove:
                del self._tasks[tid]
                self._sync_token += 1

            for chore_id, chore_info in chores_data.items():
                if chore_id not in self._tasks and chore_info.get("active", True):
                    self._tasks[chore_id] = Task(
                        id=chore_id,
                        title=chore_info["title"],
                        notes=f"points:{chore_info.get('points', 10)}",
                    )
                    self._sync_token += 1

            await self._save()

    async def _save(self) -> None:
        tasks_list = [{**t.__dict__} for t in self._tasks.values()]
        await self._store.async_save({
            "tasks": tasks_list,
            "sync_token": self._sync_token,
        })
