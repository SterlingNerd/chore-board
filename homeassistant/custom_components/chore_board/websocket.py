"""Websocket API for Chore Board admin panel."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.components.websocket_api import (
    async_register_command,
    WebSocketCommandHandler,
    ActiveConnection,
)

from .coordinator import ChoreBoardCoordinator
from .scoring import LLMConfig

_LOGGER = logging.getLogger(__name__)


async def async_register_websocket(hass: HomeAssistant) -> None:
    """Register websocket commands."""
    async_register_command(hass, websocket_get_state)
    async_register_command(hass, websocket_update_llm_config)


async def websocket_get_state(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle get_state websocket command."""
    coordinator: ChoreBoardCoordinator = hass.data["coordinator"]
    llm_config = coordinator.llm_config

    state = {
        "chores": [c.to_dict() for c in coordinator.chore_manager.chores],
        "members": [
            {
                "id": m.id,
                "name": m.name,
                "ha_user_id": m.ha_user_id,
                "todoist_username": m.todoist_username,
                "avatar": m.avatar,
            }
            for m in coordinator.members.values()
        ],
        "scores": dict(coordinator._scores),
        "history": list(coordinator._history),
        "llm_config": llm_config.to_dict(),
    }

    connection.send_result(msg["id"], state)


async def websocket_update_llm_config(
    hass: HomeAssistant,
    connection: ActiveConnection,
    msg: dict[str, Any],
) -> None:
    """Handle update_llm_config websocket command."""
    coordinator: ChoreBoardCoordinator = hass.data["coordinator"]
    new_config = LLMConfig(
        base_url=msg.get("base_url", ""),
        api_key=msg.get("api_key", ""),
        model=msg.get("model", coordinator.llm_config.model),
    )
    coordinator.llm_config = new_config
    connection.send_result(msg["id"], {"status": "updated"})
