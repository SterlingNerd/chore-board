"""Service definitions for Chore Board."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.helpers import config_validation as cv

from .const import DEFAULT_POINTS, SERVICE_AI_SCORE, SERVICE_ASSIGN_CHORE, SERVICE_LOG_TASK
from .coordinator import ChoreBoardCoordinator
from .member import Member

_LOGGER = logging.getLogger(__name__)

SCHEMA_AWARD = vol.Schema({
    vol.Required("task_id"): cv.string,
    vol.Required("member_id"): cv.string,
})

SCHEMA_ASSIGN = vol.Schema({
    vol.Required("chore_id"): cv.string,
    vol.Required("title"): cv.string,
    vol.Optional("points", default=DEFAULT_POINTS): cv.positive_int,
})

SCHEMA_ADJUST_POINTS = vol.Schema({
    vol.Required("chore_id"): cv.string,
    vol.Required("points"): cv.positive_int,
})

SCHEMA_UPDATE_MEMBER = vol.Schema({
    vol.Required("member_id"): cv.string,
    vol.Optional("ha_user_id"): cv.string,
    vol.Optional("todoist_username"): cv.string,
})

SCHEMA_UPDATE_LLM = vol.Schema({
    vol.Optional("base_url"): cv.string,
    vol.Optional("api_key"): cv.string,
    vol.Optional("model"): cv.string,
})

SCHEMA_LOG_TASK = vol.Schema({
    vol.Required("member_id"): cv.string,
    vol.Required("task_title"): cv.string,
    vol.Required("points"): cv.positive_int,
})

SCHEMA_AI_SCORE = vol.Schema({
    vol.Required("member_id"): cv.string,
    vol.Required("task_title"): cv.string,
})

SCHEMA_ACKNOWLEDGE = vol.Schema({
    vol.Required("task_id"): cv.string,
})


async def async_setup_services(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Register all services."""
    coordinator: ChoreBoardCoordinator = hass.data["coordinator"]
    todo_store = hass.data["todo_store"]

    async def handle_award(call: ServiceCall) -> dict[str, Any]:
        """Attribute a completed task to a member and award points."""
        data = call.data
        try:
            points = await coordinator.async_complete(data["task_id"], data["member_id"])
            coordinator._pending_attribution.pop(data["task_id"], None)
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "awarded", "points": points}

    async def handle_assign(call: ServiceCall) -> dict[str, Any]:
        """Add a chore to the Todo List."""
        data = call.data
        chore_mgr = coordinator.chore_manager
        chore_mgr.add(
            Chore(id=data["chore_id"], title=data["title"], points=data["points"],
                  assigned_to=data.get("assigned_to"))
        )
        await todo_store.sync_with_chores(chore_mgr.to_dict())
        await coordinator.async_request_refresh()
        return {"status": "assigned"}

    async def handle_adjust_points(call: ServiceCall) -> dict[str, Any]:
        """Adjust points for a chore."""
        data = call.data
        success = await coordinator.async_adjust_chore_points(data["chore_id"], data["points"])
        if success:
            return {"status": "updated", "chore_id": data["chore_id"], "points": data["points"]}
        return {"status": "error", "message": f"Chore {data['chore_id']} not found"}

    async def handle_update_member(call: ServiceCall) -> dict[str, Any]:
        """Update member links (HA user, Todoist)."""
        data = call.data
        member_id = data["member_id"]
        member = coordinator.members.get(member_id)
        if not member:
            return {"status": "error", "message": f"Member {member_id} not found"}

        updates = {}
        if "ha_user_id" in data:
            updates["ha_user_id"] = data["ha_user_id"] or None
        if "todoist_username" in data:
            updates["todoist_username"] = data["todoist_username"] or None

        for key, value in updates.items():
            setattr(member, key, value)

        # Save config entry with updated members
        entry.async_set_updated_data({
            **entry.data,
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
        })

        return {"status": "updated", "member_id": member_id}

    async def handle_update_llm(call: ServiceCall) -> dict[str, Any]:
        """Update LLM configuration."""
        data = call.data
        from .scoring import LLMConfig
        new_config = LLMConfig(
            base_url=data.get("base_url", ""),
            api_key=data.get("api_key", ""),
            model=data.get("model", coordinator.llm_config.model),
        )
        coordinator.llm_config = new_config

        # Save config entry with updated LLM settings
        entry.async_set_updated_data({
            **entry.data,
            "llm_base_url": new_config.base_url,
            "llm_api_key": new_config.api_key,
            "llm_model": new_config.model,
        })

        return {"status": "updated"}

    async def handle_log_task(call: ServiceCall) -> dict[str, Any]:
        """Log an ad-hoc task and award points."""
        data = call.data
        await coordinator.async_log_task(data["member_id"], data["task_title"], data["points"])
        return {"status": "logged", "points": data["points"]}

    async def handle_ai_score(call: ServiceCall) -> dict[str, Any]:
        """Use LLM to score an ad-hoc task, then log it."""
        data = call.data
        try:
            points = await coordinator.async_ai_score(data["member_id"], data["task_title"])
        except Exception as e:
            return {"status": "error", "message": str(e)}
        return {"status": "scored", "points": points}

    async def handle_acknowledge(call: ServiceCall) -> dict[str, Any]:
        """Dismiss a pending attribution request."""
        task_id = call.data["task_id"]
        coordinator._pending_attribution.pop(task_id, None)
        return {"status": "dismissed"}

    hass.services.async_register("chore_board", "award_points", handle_award, schema=SCHEMA_AWARD)
    hass.services.async_register("chore_board", SERVICE_ASSIGN_CHORE, handle_assign, schema=SCHEMA_ASSIGN)
    hass.services.async_register("chore_board", "adjust_chore_points", handle_adjust_points, schema=SCHEMA_ADJUST_POINTS)
    hass.services.async_register("chore_board", "update_member", handle_update_member, schema=SCHEMA_UPDATE_MEMBER)
    hass.services.async_register("chore_board", "update_llm_config", handle_update_llm, schema=SCHEMA_UPDATE_LLM)
    hass.services.async_register("chore_board", SERVICE_LOG_TASK, handle_log_task, schema=SCHEMA_LOG_TASK)
    hass.services.async_register("chore_board", SERVICE_AI_SCORE, handle_ai_score, schema=SCHEMA_AI_SCORE)
    hass.services.async_register("chore_board", "acknowledge", handle_acknowledge, schema=SCHEMA_ACKNOWLEDGE)


async def async_unload_services(hass: HomeAssistant) -> None:
    hass.services.async_remove("chore_board", "award_points")
    hass.services.async_remove("chore_board", SERVICE_ASSIGN_CHORE)
    hass.services.async_remove("chore_board", "adjust_chore_points")
    hass.services.async_remove("chore_board", "update_member")
    hass.services.async_remove("chore_board", "update_llm_config")
    hass.services.async_remove("chore_board", SERVICE_LOG_TASK)
    hass.services.async_remove("chore_board", SERVICE_AI_SCORE)
    hass.services.async_remove("chore_board", "acknowledge")


from .chore import Chore
