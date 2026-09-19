"""Data coordinator for Chore Board."""

from __future__ import annotations

import dataclasses
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .chore import Chore, ChoreManager
from .member import Member
from .todo_store.base import Task

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class BoardState:
    """Full board state."""

    chores: list[Chore]
    members: dict[str, Member]
    scores: dict[str, int]  # member_id -> points
    task_history: list[dict[str, Any]]


class ChoreBoardCoordinator(DataUpdateCoordinator[BoardState]):
    """Tracks chores, members, scores, and history."""

    def __init__(self, hass: HomeAssistant, chore_mgr: ChoreManager, members: dict[str, Member]) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="chore_board",
            update_interval=timedelta(minutes=5),
        )
        self._chore_mgr = chore_mgr
        self._members = members
        self._scores: dict[str, int] = {mid: 0 for mid in members}
        self._history: list[dict[str, Any]] = []

    @property
    def chore_manager(self) -> ChoreManager:
        return self._chore_mgr

    @property
    def members(self) -> dict[str, Member]:
        return self._members

    async def async_complete(self, chore_id: str, member_id: str) -> int:
        """Complete a chore and award points. Returns points awarded."""
        chore = self._chore_mgr.get(chore_id)
        if not chore:
            raise UpdateFailed(f"Chore {chore_id} not found")
        if member_id not in self._members:
            raise UpdateFailed(f"Member {member_id} not found")
        if not chore.active:
            raise UpdateFailed(f"Chore {chore_id} is not active")

        points = chore.points
        self._scores[member_id] = self._scores.get(member_id, 0) + points

        self._history.append({
            "chore_id": chore_id,
            "chore_title": chore.title,
            "member_id": member_id,
            "points": points,
            "timestamp": str(self._async_now()),
        })

        await self.async_request_refresh()
        return points

    async def async_log_task(self, member_id: str, task_title: str, points: int) -> None:
        """Log an ad-hoc task and award points."""
        if member_id not in self._members:
            raise UpdateFailed(f"Member {member_id} not found")

        self._scores[member_id] = self._scores.get(member_id, 0) + points

        self._history.append({
            "task_title": task_title,
            "member_id": member_id,
            "points": points,
            "timestamp": str(self._async_now()),
        })

        await self.async_request_refresh()

    async def async_ai_score(self, member_id: str, task_title: str, model: str, api_key: str | None) -> int:
        """Use LLM to score a task, then log it."""
        from .scoring import ai_score

        points = await ai_score_task(task_title, model=model, api_key=api_key)
        await self.async_log_task(member_id, task_title, points)
        return points

    def _async_now(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()

    async def _async_update_data(self) -> BoardState:
        return BoardState(
            chores=self._chore_mgr.chores,
            members=self._members,
            scores=dict(self._scores),
            task_history=list(self._history),
        )

    def to_dict(self) -> dict[str, Any]:
        return {
            "chores": [c.to_dict() for c in self._chore_mgr.chores],
            "scores": dict(self._scores),
            "history": list(self._history),
        }

    @classmethod
    def from_dict(cls, hass: HomeAssistant, data: dict[str, Any], members: dict[str, Member]) -> "ChoreBoardCoordinator":
        """Reconstruct coordinator from stored data."""
        chore_mgr = ChoreManager.from_dict(data.get("chores", {}))
        coord = cls(hass, chore_mgr, members)
        coord._scores = data.get("scores", {mid: 0 for mid in members})
        coord._history = data.get("history", [])
        return coord
