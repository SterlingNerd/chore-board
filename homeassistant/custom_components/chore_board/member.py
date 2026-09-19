"""Household members with HA user and Todoist accounts."""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass
class Member:
    """A household member with linked accounts."""

    id: str
    name: str
    ha_user_id: str | None = None  # HA user ID (for kiosk attribution)
    todoist_username: str | None = None  # Todoist username (for task sync)
    avatar: str | None = None


def members_from_config(members_config: list[dict[str, Any]]) -> dict[str, Member]:
    """Build member dict from HA config."""
    result = {}
    for m in members_config:
        result[m["id"]] = Member(
            id=m["id"],
            name=m["name"],
            ha_user_id=m.get("ha_user_id"),
            todoist_username=m.get("todoist_username"),
            avatar=m.get("avatar"),
        )
    return result


def find_member_by_ha_user(members: dict[str, Member], ha_user_id: str) -> Member | None:
    """Find a member by their HA user ID."""
    for member in members.values():
        if member.ha_user_id == ha_user_id:
            return member
    return None
