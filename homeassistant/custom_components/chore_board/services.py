"""Service definitions for Chore Board."""

from __future__ import annotations

import dataclasses
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .chore import Chore, ChoreManager
from .const import (
    DEFAULT_POINTS,
    SERVICE_AI_SCORE,
    SERVICE_ASSIGN_CHORE,
    SERVICE_COMPLETE,
    SERVICE_LOG_TASK,
)
from .coordinator import ChoreBoardCoordinator
from .todo_store.base import Task

# Service schemas
SCHEMA_ASSIGN = vol.Schema({
    vol.Required("chore_id"): cv.string,
    vol.Required("title"): cv.string,
    vol.Optional("points", default=DEFAULT_POINTS): cv.positive_int,
    vol.Optional("assigned_to"): cv.string,
})

SCHEMA_COMPLETE = vol.Schema({
    vol.Required("chore_id"): cv.string,
    vol.Required("member_id"): cv.string,
})

SCHEMA_LOG_TASK = vol.Schema({
    vol.Required("member_id"): cv.string,
    vol.Required("task_title"): cv.string,
    vol.Required("points"): cv.positive_int,
})

SCHEMA_AI_SCORE = vol.Schema({
    vol.Required("member_id"): cv.string,
    vol.Required("task_title"): cv.string,
    vol.Optional("model"): cv.string,
    vol.Optional("api_key"): cv.string,
})


async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register all services."""
    coordinator: ChoreBoardCoordinator = hass.data["coordinator"]
    todo_store = hass.data["todo_store"]
    chore_mgr: ChoreManager = coordinator.chore_manager

    async def handle_assign(call: ServiceCall) -> dict[str, Any]:
        data = call.data
        chore = Chore(
            id=data["chore_id"],
            title=data["title"],
            points=data["points"],
            assigned_to=data.get("assigned_to"),
        )
        chore_mgr.add(chore)
        await todo_store.create_task(
            title=data["title"],
            notes=f"points:{data['points']}",
        )
        await coordinator.async_request_refresh()
        return {"status": "assigned"}

    async def handle_complete(call: ServiceCall) -> dict[str, Any]:
        data = call.data
        try:
            points = await coordinator.async_complete(data["chore_id"], data["member_id"])
        except Exception as e:
            return {"status": "error", "message": str(e)}

        # Also mark complete in todo store
        try:
            await todo_store.complete_task(data["chore_id"])
        except Exception:
            pass  # Don't fail if store doesn't have it

        return {"status": "done", "points_awarded": points}

    async def handle_log_task(call: ServiceCall) -> dict[str, Any]:
        data = call.data
        await coordinator.async_log_task(data["member_id"], data["task_title"], data["points"])
        return {"status": "logged", "points": data["points"]}

    async def handle_ai_score(call: ServiceCall) -> dict[str, Any]:
        data = call.data
        model = data.get("model", "gpt-4o-mini")
        try:
            from .scoring import ai_score_task
            points = await ai_score_task(
                data["task_title"],
                model=model,
                api_key=data.get("api_key"),
            )
        except Exception as e:
            return {"status": "error", "message": str(e)}

        await coordinator.async_log_task(data["member_id"], data["task_title"], points)
        return {"status": "scored", "points": points}

    hass.services.async_register("chore_board", SERVICE_ASSIGN_CHORE, handle_assign, schema=SCHEMA_ASSIGN)
    hass.services.async_register("chore_board", SERVICE_COMPLETE, handle_complete, schema=SCHEMA_COMPLETE)
    hass.services.async_register("chore_board", SERVICE_LOG_TASK, handle_log_task, schema=SCHEMA_LOG_TASK)
    hass.services.async_register("chore_board", SERVICE_AI_SCORE, handle_ai_score, schema=SCHEMA_AI_SCORE)


async def async_unload_services(hass: HomeAssistant) -> None:
    """Remove all services."""
    hass.services.async_remove("chore_board", SERVICE_ASSIGN_CHORE)
    hass.services.async_remove("chore_board", SERVICE_COMPLETE)
    hass.services.async_remove("chore_board", SERVICE_LOG_TASK)
    hass.services.async_remove("chore_board", SERVICE_AI_SCORE)
