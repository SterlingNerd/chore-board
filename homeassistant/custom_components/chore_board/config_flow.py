"""Config flow for Chore Board."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .const import DEFAULT_LLM_MODEL, STORE_LOCAL, STORE_TODOIST, VALID_STORE_TYPES

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema({
    vol.Required("store_type", default=STORE_LOCAL): vol.In(VALID_STORE_TYPES),
})

STEP_TODOIST = vol.Schema({
    vol.Required("token"): str,
})

STEP_MEMBERS = vol.Schema({
    vol.Required("members"): str,  # JSON string of member list
})


class ChoreBoardConfigFlow(config_entries.ConfigFlow, domain="chore_board"):
    """Handle a config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._store_type = STORE_LOCAL
        self._members: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA)

        self._store_type = user_input["store_type"]

        if self._store_type == STORE_TODOIST:
            return await self.async_step_todoist()
        return await self.async_step_members()

    async def async_step_todoist(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(step_id="todoist", data_schema=STEP_TODOIST)

        self._todoist_token = user_input["token"]
        return await self.async_step_members()

    async def async_step_members(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="members",
                data_schema=vol.Schema({
                    vol.Required("members_json", default="[]"): str,
                }),
            )

        import json
        try:
            self._members = json.loads(user_input["members_json"])
        except json.JSONDecodeError:
            return self.async_show_form(step_id="members", errors={"base": "invalid_json"})

        return self.async_create_entry(
            title="Chore Board",
            data={
                "store_type": self._store_type,
                "members": self._members,
                "todoist_token": getattr(self, "_todoist_token", ""),
                "llm_model": DEFAULT_LLM_MODEL,
            },
        )
