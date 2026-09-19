"""Household members."""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass
class Member:
    """A household member."""

    id: str
    name: str
    avatar: str | None = None


def members_from_config(members_config: list[dict[str, Any]]) -> dict[str, Member]:
    """Build member dict from HA config."""
    return {m["id"]: Member(id=m["id"], name=m["name"], avatar=m.get("avatar")) for m in members_config}
