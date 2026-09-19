"""Chore model and management."""

from __future__ import annotations

import dataclasses
from typing import Any


@dataclasses.dataclass
class Chore:
    """Represents a chore on the board."""

    id: str
    title: str
    points: int = 10
    assigned_to: str | None = None  # member id
    active: bool = True

    def to_dict(self) -> dict[str, Any]:
        return dataclasses.asdict(self)

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Chore:
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})


class ChoreManager:
    """Manages chores in memory + persistence."""

    def __init__(self) -> None:
        self._chores: dict[str, Chore] = {}

    @property
    def chores(self) -> list[Chore]:
        return list(self._chores.values())

    def add(self, chore: Chore) -> None:
        self._chores[chore.id] = chore

    def get(self, chore_id: str) -> Chore | None:
        return self._chores.get(chore_id)

    def remove(self, chore_id: str) -> bool:
        return self._chores.pop(chore_id, None) is not None

    def update(self, chore_id: str, **kwargs) -> bool:
        if chore_id not in self._chores:
            return False
        for key, value in kwargs.items():
            if hasattr(self._chores[chore_id], key):
                setattr(self._chores[chore_id], key, value)
        return True

    def to_dict(self) -> dict[str, Any]:
        return {cid: c.to_dict() for cid, c in self._chores.items()}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> ChoreManager:
        mgr = cls()
        for cid, cdata in data.items():
            mgr.add(Chore.from_dict(cdata))
        return mgr
