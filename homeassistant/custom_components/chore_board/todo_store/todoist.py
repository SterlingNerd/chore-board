"""Todoist API adapter."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant

from .base import Task, TodoStore

_LOGGER = logging.getLogger(__name__)

# Map chore_board items to a specific Todoist project
TODOIST_PROJECT_NAME = "Chore Board"


class TodoistTodoStore(TodoStore):
    """Todoist API as a todo store backend."""

    def __init__(self, hass: HomeAssistant) -> None:
        self._hass = hass
        self._token: str = ""
        self._project_id: str | None = None

    async def initialize(self, config: dict[str, Any] | None = None) -> None:
        """Initialize with Todoist token from config."""
        if config:
            self._token = config.get("token", "")
        if not self._token:
            raise ValueError("Todoist token is required")

    async def list_tasks(self) -> list[Task]:
        """Fetch tasks from Todoist project."""
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(self._token)
        if not self._project_id:
            await self._find_or_create_project(api)

        if not self._project_id:
            return []

        items = api.get_sync_items(project_id=self._project_id)
        tasks = []
        for item in getattr(items, "items", []):
            tasks.append(
                Task(
                    id=f"todoist-{item.id}",
                    title=item.content,
                    completed=item.is_completed,
                    notes=item.notes,
                )
            )
        return tasks

    async def create_task(self, title: str, notes: str | None = None) -> Task:
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(self._token)
        if not self._project_id:
            await self._find_or_create_project(api)

        kwargs: dict[str, Any] = {"content": title, "project_id": self._project_id}
        if notes:
            kwargs["description"] = notes

        item = api.add_item(**kwargs)
        return Task(
            id=f"todoist-{item.id}",
            title=item.content,
            completed=False,
            notes=notes,
        )

    async def complete_task(self, task_id: str) -> Task:
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(self._token)
        todoist_id = task_id.removeprefix("todoist-")
        api.close_item(todoist_id)
        return Task(id=task_id, title="", completed=True)

    async def delete_task(self, task_id: str) -> bool:
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(self._token)
        todoist_id = task_id.removeprefix("todoist-")
        try:
            api.delete_item(todoist_id)
            return True
        except Exception as e:
            _LOGGER.warning("Failed to delete task %s: %s", task_id, e)
            return False

    async def sync_with_chores(self, chores_data: dict[str, Any]) -> None:
        """Sync chores to Todoist project.

        Creates a project called 'Chore Board' and ensures each active
        chore has a corresponding task.
        """
        from todoist_api_python.api import TodoistAPI

        api = TodoistAPI(self._token)
        await self._find_or_create_project(api)

        if not self._project_id:
            return

        # Get existing tasks in the project
        items = api.get_sync_items(project_id=self._project_id)
        existing = {item.id: item for item in getattr(items, "items", [])}

        # Ensure a task exists for each active chore
        for chore_id, chore_info in chores_data.items():
            if not chore_info.get("active", True):
                continue
            title = chore_info["title"]
            notes = f"points:{chore_info.get('points', 10)}"

            # Check if a matching task already exists
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
        """Find or create the Chore Board project."""
        projects = api.get_projects()
        for project in projects:
            if project.name == TODOIST_PROJECT_NAME:
                self._project_id = project.id
                return

        project = api.add_project(name=TODOIST_PROJECT_NAME)
        self._project_id = project.id
