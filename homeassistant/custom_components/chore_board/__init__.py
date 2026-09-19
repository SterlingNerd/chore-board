"""Chore Board - Gamified household chore tracker."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers import storage

from .chore import Chore, ChoreManager
from .const import STORAGE_KEY, STORAGE_VERSION
from .coordinator import ChoreBoardCoordinator
from .member import members_from_config
from .services import async_setup_services, async_unload_services
from .todo_store.factory import create_store

_LOGGER = logging.getLogger(__name__)

PLATFORMS = ["sensor"]


async def async_setup(hass: HomeAssistant, config: dict) -> bool:
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Chore Board from a config entry."""
    data = entry.data

    # Initialize members
    members = members_from_config(data["members"])

    # Initialize chore manager
    chore_mgr = ChoreManager()

    # Load persisted state (chores, scores, history)
    store = storage.Storage(hass, STORAGE_VERSION, STORAGE_KEY)
    saved = await store.async_load()

    if saved and saved.get("chores"):
        # Restore from persisted state
        chore_mgr = ChoreManager.from_dict(saved["chores"])
        coordinator = ChoreBoardCoordinator.from_dict(hass, saved, members)
    else:
        coordinator = ChoreBoardCoordinator(hass, chore_mgr, members)

    # Initialize todo store
    todo_store = create_store(hass, data["store_type"], {"token": data.get("todoist_token", "")})
    await todo_store.initialize()

    # Sync chores to todo store
    await todo_store.sync_with_chores(chore_mgr.to_dict())

    # Store references
    hass.data["coordinator"] = coordinator
    hass.data["todo_store"] = todo_store

    # Register services
    await async_setup_services(hass, entry)

    # Set up platforms
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    entry.async_on_unload(entry.add_update_listener(async_reload_entry))

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        await async_unload_services(hass)
        # Persist state
        store = storage.Storage(hass, STORAGE_VERSION, STORAGE_KEY)
        coordinator: ChoreBoardCoordinator = hass.data.get("coordinator")
        if coordinator:
            await store.async_save(coordinator.to_dict())
        hass.data.pop("coordinator", None)
        hass.data.pop("todo_store", None)
    return unload_ok


async def async_reload_entry(hass: HomeAssistant, entry: ConfigEntry) -> None:
    """Reload config entry."""
    await async_unload_entry(hass, entry)
    await async_setup_entry(hass, entry)
