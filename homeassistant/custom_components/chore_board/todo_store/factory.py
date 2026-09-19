"""Factory for creating todo stores."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .base import TodoStore
from .local import LocalTodoStore
from .todoist import TodoistTodoStore
from ..const import STORE_LOCAL, STORE_TODOIST


def create_store(hass: HomeAssistant, store_type: str, config: dict[str, Any] | None = None) -> TodoStore:
    """Create a todo store instance based on type."""
    if store_type == STORE_TODOIST:
        return TodoistTodoStore(hass)
    return LocalTodoStore(hass)
