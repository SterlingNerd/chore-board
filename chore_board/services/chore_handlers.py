"""Service handlers for chore-related services."""

from __future__ import annotations


async def async_assign_chore(hass: object, service_call: object) -> None:
    """Handle chore_board.assign_chore service."""
    from chore_board.chore import Chore, ChoreManager
    data = service_call.data if service_call else {}
    chore_id = data.get("chore_id")
    title = data.get("title")
    points = data.get("points", 10)
    assigned_to = data.get("assigned_to")

    if not title:
        raise ValueError("title is required")
    if not chore_id:
        raise ValueError("chore_id is required")

    manager = hass.services.data["chore_manager"]
    chore = Chore(id=chore_id, title=title, points=points, assigned_to=assigned_to)
    manager.add_chore(chore)


async def async_adjust_chore_points(hass: object, service_call: object) -> None:
    """Handle chore_board.adjust_chore_points service."""
    data = service_call.data if service_call else {}
    chore_id = data.get("chore_id")
    new_points = data.get("points")

    if not chore_id:
        raise ValueError("chore_id is required")
    if new_points is None:
        raise ValueError("points is required")

    manager = hass.services.data["chore_manager"]
    manager.update_chore(chore_id, points=new_points)
