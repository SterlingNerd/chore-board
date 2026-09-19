"""Config flow for Chore Board."""

from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import selector

from .const import DEFAULT_LLM_MODEL

_LOGGER = logging.getLogger(__name__)

STEP_TODO = vol.Schema({
    vol.Required("todo_entity"): str,
})

STEP_LLM = vol.Schema({
    vol.Optional("llm_base_url"): str,
    vol.Optional("llm_api_key"): str,
    vol.Optional("llm_model", default=DEFAULT_LLM_MODEL): str,
})

STEP_MEMBERS = vol.Schema({
    vol.Required("members_json", default="[]"): str,
})


class ChoreBoardConfigFlow(config_entries.ConfigFlow, domain="chore_board"):
    """Handle a config flow."""

    VERSION = 1

    def __init__(self) -> None:
        self._todo_entity: str = ""
        self._llm_config: dict[str, str] = {
            "llm_base_url": "",
            "llm_api_key": "",
            "llm_model": DEFAULT_LLM_MODEL,
        }
        self._members: list[dict[str, Any]] = []

    async def async_step_user(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return await self._show_todo_form()
        self._todo_entity = user_input["todo_entity"]
        return await self.async_step_llm()

    async def _show_todo_form(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        errors: dict[str, str] = {}
        if user_input:
            self._todo_entity = user_input["todo_entity"]
            return await self.async_step_llm()

        entity_registry = await self.hass.helpers.entity_registry.async_get_registry()
        todo_entities = [
            (e.entity_id, e.name or e.entity_id)
            for e in entity_registry.entities.values()
            if e.platform == "todo"
        ]

        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({
                vol.Required("todo_entity", default=todo_entities[0][0] if todo_entities else ""):
                    selector({"entity": {"domain": "todo", "multiple": False}}),
            }),
            errors=errors,
        )

    async def async_step_llm(self, user_input: dict[str, Any] | None = None) -> FlowResult:
        if user_input is None:
            return self.async_show_form(
                step_id="llm",
                data_schema=STEP_LLM,
            )

        self._llm_config = {
            "llm_base_url": user_input.get("llm_base_url", ""),
            "llm_api_key": user_input.get("llm_api_key", ""),
            "llm_model": user_input.get("llm_model", DEFAULT_LLM_MODEL),
        }
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
                "todo_entity": self._todo_entity,
                "members": self._members,
                "llm_base_url": self._llm_config["llm_base_url"],
                "llm_api_key": self._llm_config["llm_api_key"],
                "llm_model": self._llm_config["llm_model"],
            },
        )
