"""Factory for creating todo stores."""

from __future__ import annotations

from typing import Any

from homeassistant.core import HomeAssistant

from .base import TodoStore
from .ha_todos import HATodoStore


def create_store(hass: HomeAssistant, todo_entity_id: str) -> TodoStore:
    """Create the HA Todo List store."""
    return HATodoStore(hass, todo_entity_id)
