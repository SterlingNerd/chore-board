"""Service handlers for member-related services."""

from __future__ import annotations


async def async_add_participant(hass: object, service_call: object) -> None:
    """Handle adding a participant."""
    data = service_call.data if service_call else {}
    user_id = data.get("user_id")
    external_account = data.get("external_account")
    member_mgr = hass.services.data["member_manager"]
    member_mgr.add_member(user_id, external_account)


async def async_remove_participant(hass: object, service_call: object) -> None:
    """Handle removing a participant."""
    data = service_call.data if service_call else {}
    user_id = data.get("user_id")
    member_mgr = hass.services.data["member_manager"]
    member_mgr.remove_member(user_id)


async def async_link_external_account(
    hass: object, service_call: object
) -> None:
    """Handle linking an external account."""
    data = service_call.data if service_call else {}
    user_id = data.get("user_id")
    account = data.get("external_account")
    member_mgr = hass.services.data["member_manager"]
    member_mgr.link_external_account(user_id, account)
