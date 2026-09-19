"""Home Assistant Todo List store adapter.

Uses HA's native todo_list integration as source of truth.
We observe changes via triggers and read via todo.get_items.
"""

from __future__ import annotations

import logging
from datetime import datetime
from typing import Any

from homeassistant.core import HomeAssistant

from .base import StoreChanges, Task, TodoStore

_LOGGER = logging.getLogger(__name__)


class HATodoStore(TodoStore):
    """Adapter for HA's built-in Todo List integration."""

    def __init__(self, hass: HomeAssistant, todo_entity_id: str) -> None:
        self._hass = hass
        self._todo_entity_id = todo_entity_id
        self._seen_uids: set[str] = set()  # track seen items for delta detection

    @property
    def todo_entity_id(self) -> str:
        return self._todo_entity_id

    async def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Load current items to establish baseline."""
        items = await self._get_items()
        for item in items:
            self._seen_uids.add(item.uid)

    async def poll(self) -> StoreChanges:
        """Check for changes since last poll.

        Returns StoreChanges with new and completed tasks.
        """
        current_items = await self._get_items()
        current_uids = {item.uid for item in current_items}

        changes = StoreChanges()

        # Find completed items (were seen before, now completed or gone)
        for item in current_items:
            if item.uid not in self._seen_uids:
                # New item
                changes.new_tasks.append(Task(
                    id=f"{self._todo_entity_id}-{item.uid}",
                    title=item.summary,
                    completed=(item.status == "completed"),
                    notes=item.description,
                ))
            elif item.status == "completed":
                # Just completed
                changes.completed_tasks.append(Task(
                    id=f"{self._todo_entity_id}-{item.uid}",
                    title=item.summary,
                    completed=True,
                    completed_at=datetime.now(),
                ))

        # Find removed items
        removed = self._seen_uids - current_uids
        for uid in removed:
            changes.deleted_tasks.append(f"{self._todo_entity_id}-{uid}")

        # Update seen set
        self._seen_uids = current_uids
        return changes

    async def list_tasks(self) -> list[Task]:
        """Get all current tasks."""
        return await self._get_items()

    async def sync_with_chores(self, chores_data: dict[str, Any]) -> None:
        """Create tasks in HA Todo List for active chores."""
        from homeassistant.components.todo import TodoListEntity, TodoItem, TodoItemStatus

        for chore_id, chore_info in chores_data.items():
            if not chore_info.get("active", True):
                continue
            # Check if task already exists
            existing = await self._get_items()
            title = chore_info["title"]
            if any(item.summary == title and item.status == "needs_action" for item in existing):
                continue

            # Create description with points info
            points = chore_info.get("points", 10)
            notes = f"points:{points}"

            await self._hass.services.async_call(
                "todo",
                "add_item",
                {
                    "entity_id": self._todo_entity_id,
                    "item": title,
                    "description": notes,
                },
                blocking=True,
            )

    async def _get_items(self) -> list[Task]:
        """Fetch items from HA Todo List via service call."""
        result = await self._hass.services.async_call(
            "todo",
            "get_items",
            {"entity_id": self._todo_entity_id},
            blocking=True,
            return_response=True,
        )
        items = []
        todo_items = result.get(self._todo_entity_id, {}).get("items", [])
        for item_data in todo_items:
            items.append(Task(
                id=f"{self._todo_entity_id}-{item_data['uid']}",
                title=item_data["summary"],
                completed=(item_data["status"] == "completed"),
                notes=item_data.get("description"),
            ))
        return items
