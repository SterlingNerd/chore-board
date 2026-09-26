"""Chore data model and ChoreManager (CRUD)."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Chore:
    id: str
    title: str
    points: int
    assigned_to: Optional[str] = None
    active: bool = True


class ChoreManager:
    """CRUD operations for chores."""

    def __init__(self, chores: Optional[list[Chore]] = None) -> None:
        self._chores: dict[str, Chore] = {}
        if chores:
            for c in chores:
                self._chores[c.id] = c

    def add_chore(self, chore: Chore) -> str:
        """Add a chore. Returns the chore id."""
        if not chore.title or not chore.title.strip():
            raise ValueError("Chore title cannot be empty")
        if not isinstance(chore.points, int) or isinstance(chore.points, bool):
            raise ValueError("Chore points must be an integer")
        if chore.points < 0:
            raise ValueError("Chore points cannot be negative")
        self._chores[chore.id] = chore
        return chore.id

    def update_chore(self, chore_id: str, **kwargs: object) -> None:
        """Update chore fields. kwargs: title, points, assigned_to, active."""
        chore = self._get_or_raise(chore_id)
        if "title" in kwargs:
            if not kwargs["title"] or not str(kwargs["title"]).strip():
                raise ValueError("Chore title cannot be empty")
            chore.title = str(kwargs["title"])
        if "points" in kwargs:
            pts = kwargs["points"]
            if not isinstance(pts, int) or isinstance(pts, bool):
                raise ValueError("Chore points must be an integer")
            if pts < 0:
                raise ValueError("Chore points cannot be negative")
            chore.points = pts
        if "assigned_to" in kwargs:
            chore.assigned_to = kwargs["assigned_to"]
        if "active" in kwargs:
            chore.active = bool(kwargs["active"])

    def toggle_active(self, chore_id: str) -> None:
        """Toggle a chore's active status."""
        chore = self._get_or_raise(chore_id)
        chore.active = not chore.active

    def delete_chore(self, chore_id: str) -> None:
        """Delete a chore."""
        self._get_or_raise(chore_id)
        del self._chores[chore_id]

    def get_chore(self, chore_id: str) -> Chore:
        """Get a chore by id."""
        return self._get_or_raise(chore_id)

    def list_chores(self, active_only: bool = False) -> list[Chore]:
        """List chores, optionally filtered by active status."""
        result = list(self._chores.values())
        if active_only:
            result = [c for c in result if c.active]
        return result

    def list_active_chores(self) -> list[Chore]:
        """Shorthand for list_chores(active_only=True)."""
        return self.list_chores(active_only=True)

    def list_chores_by_assignee(self, assignee_id: str) -> list[Chore]:
        """List chores assigned to a specific participant."""
        return [c for c in self._chores.values() if c.assigned_to == assignee_id]

    def _get_or_raise(self, chore_id: str) -> Chore:
        if chore_id not in self._chores:
            raise KeyError(f"Chore '{chore_id}' not found")
        return self._chores[chore_id]
