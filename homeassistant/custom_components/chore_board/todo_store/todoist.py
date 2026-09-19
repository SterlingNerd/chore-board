"""Todoist API adapter with sync-token polling."""

from __future__ import annotations

import logging
from datetime import datetime, timezone
from typing import Any

from homeassistant.core import HomeAssistant

from .base import StoreChanges, Task, TodoStore

_LOGGER = logging.getLogger(__name__)

TODOIST_PROJECT_NAME = "Chore Board"


class TodoistTodoStore(TodoStore):
    """Todoist API as source-of-truth backend."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._token: str = ""
        self._project_id: str | None = None
        self._sync_token: str | None = None  # Todoist sync token
        self._seen_tasks: set[str] = set()   # task ids we've already reported

    async def initialize(self, config: dict[str, Any] | None = None) -> None:
        if config:
            self._token = config.get("token", "")
        if not self._token:
            raise ValueError("Todoist token is required")

    async def poll(self) -> StoreChanges:
        """Poll Todoist for changes using sync token.

        Returns StoreChanges with newly completed tasks and new tasks
        since the last poll.
        """
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(self._token)
        if not self._project_id:
            await self._find_or_create_project(api)

        kwargs: dict[str, Any] = {"sync_token": self._sync_token} if self._sync_token else {}
        response = api.get_sync(**kwargs)

        new_token = response.get("sync_token", "")
        self._sync_token = new_token

        changes = StoreChanges()
        new_tasks_set = set()

        # Process completed items
        for item_data in response.get("items", []):
            item_id = item_data.get("id", "")
            # Only report if this is a task we care about (in our project)
            if item_data.get("project_id") != self._project_id:
                continue
            if item_data.get("completed_at") and not self._seen_tasks.get(item_id):
                changes.completed_tasks.append(Task(
                    id=f"todoist-{item_id}",
                    title=item_data.get("content", ""),
                    completed=True,
                    completed_at=datetime.fromisoformat(item_data["completed_at"].replace("Z", "+00:00"))
                        if item_data["completed_at"].endswith("Z")
                        else datetime.fromisoformat(item_data["completed_at"]),
                ))
                self._seen_tasks[item_id] = True
            else:
                new_tasks_set.add(item_id)

        # Process items added to our project
        for item_data in response.get("items", []):
            item_id = item_data.get("id", "")
            if item_id in self._seen_tasks:
                continue
            if item_data.get("project_id") == self._project_id and not item_data.get("completed_at"):
                changes.new_tasks.append(Task(
                    id=f"todoist-{item_id}",
                    title=item_data.get("content", ""),
                    notes=item_data.get("description"),
                ))
                self._seen_tasks[item_id] = True

        # Process item removals
        for item_id in response.get("item_deletions", []):
            if item_id in self._seen_tasks:
                changes.deleted_tasks.append(f"todoist-{item_id}")
                del self._seen_tasks[item_id]

        return changes

    async def list_tasks(self) -> list[Task]:
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(self._token)
        if not self._project_id:
            await self._find_or_create_project(api)
        if not self._project_id:
            return []

        items = api.get_sync_items(project_id=self._project_id)
        tasks = []
        for item in getattr(items, "items", []):
            completed_at = None
            if item.is_completed and item.completed_at:
                try:
                    completed_at = datetime.fromisoformat(item.completed_at.replace("Z", "+00:00"))
                except (ValueError, AttributeError):
                    pass
            tasks.append(Task(
                id=f"todoist-{item.id}",
                title=item.content,
                completed=item.is_completed,
                notes=item.description,
                completed_at=completed_at,
            ))
        return tasks

    async def sync_with_chores(self, chores_data: dict[str, Any]) -> None:
        """Sync chores to Todoist project."""
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(self._token)
        await self._find_or_create_project(api)

        if not self._project_id:
            return

        items = api.get_sync_items(project_id=self._project_id)
        existing = {item.id: item for item in getattr(items, "items", [])}

        for chore_id, chore_info in chores_data.items():
            if not chore_info.get("active", True):
                continue
            title = chore_info["title"]
            notes = f"points:{chore_info.get('points', 10)}"

            matched = None
            for tid, item in existing.items():
                if item.content == title:
                    matched = (tid, item)
                    break

            if matched:
                tid, item = matched
                if not item.is_completed:
                    api.update_item(tid, content=title, description=notes)
            else:
                api.add_item(content=title, project_id=self._project_id, description=notes)

    async def _find_or_create_project(self, api: Any) -> None:
        projects = api.get_projects()
        for project in projects:
            if project.name == TODOIST_PROJECT_NAME:
                self._project_id = project.id
                return

        project = api.add_project(name=TODOIST_PROJECT_NAME)
        self._project_id = project.id
