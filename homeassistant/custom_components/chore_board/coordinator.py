"""Data coordinator for Chore Board."""

from __future__ import annotations

import dataclasses
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .chore import Chore, ChoreManager
from .member import Member
from .todo_store.base import StoreChanges, Task

_LOGGER = logging.getLogger(__name__)


@dataclasses.dataclass
class BoardState:
    """Full board state."""

    chores: list[Chore]
    members: dict[str, Member]
    scores: dict[str, int]  # member_id -> points
    task_history: list[dict[str, Any]]


class ChoreBoardCoordinator(DataUpdateCoordinator[BoardState]):
    """Polls the todo store, detects completions, awards points."""

    def __init__(
        self,
        hass: HomeAssistant,
        chore_mgr: ChoreManager,
        members: dict[str, Member],
        poll_interval: timedelta = timedelta(minutes=2),
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            name="chore_board",
            update_interval=poll_interval,
        )
        self._chore_mgr = chore_mgr
        self._members = members
        self._scores: dict[str, int] = {mid: 0 for mid in members}
        self._history: list[dict[str, Any]] = []
        self._pending_attribution: dict[str, Task] = {}  # task_id -> task awaiting member attribution
        self._store = None  # set by __init__

    @property
    def chore_manager(self) -> ChoreManager:
        return self._chore_mgr

    @property
    def members(self) -> dict[str, Member]:
        return self._members

    @property
    def pending(self) -> dict[str, Task]:
        return dict(self._pending_attribution)

    async def async_set_store(self, store: Any) -> None:
        """Set the todo store reference (called from __init__.py)."""
        self._store = store

    async def async_complete(self, task_id: str, member_id: str) -> int:
        """Manually complete a task and award points (for HA-initiated flow)."""
        if member_id not in self._members:
            raise UpdateFailed(f"Member {member_id} not found")

        chore = self._chore_mgr.get(task_id)
        points = chore.points if chore else 10

        self._scores[member_id] = self._scores.get(member_id, 0) + points
        self._history.append({
            "task_id": task_id,
            "member_id": member_id,
            "points": points,
            "timestamp": self._now(),
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
            "timestamp": self._now(),
        })
        await self.async_request_refresh()

    async def _async_update_data(self) -> BoardState:
        """Core polling loop: detect changes, ask who did it."""
        if not self._store:
            return self._build_state()

        try:
            changes: StoreChanges = await self._store.poll()
        except Exception as e:
            _LOGGER.warning("Poll failed: %s", e)
            return self._build_state()

        # Handle newly completed tasks — ask who completed each
        for task in changes.completed_tasks:
            # Skip if already attributed
            if task.id in self._pending_attribution:
                continue
            self._pending_attribution[task.id] = task
            _LOGGER.info("Task completed: %s — awaiting attribution", task.title)

        # Handle new tasks
        for task in changes.new_tasks:
            _LOGGER.info("New task detected: %s", task.title)

        # Handle deletions
        for task_id in changes.deleted_tasks:
            self._pending_attribution.pop(task_id, None)

        return self._build_state()

    def _build_state(self) -> BoardState:
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
        chore_mgr = ChoreManager.from_dict(data.get("chores", {}))
        coord = cls(hass, chore_mgr, members)
        coord._scores = data.get("scores", {mid: 0 for mid in members})
        coord._history = data.get("history", [])
        return coord

    def _now(self) -> str:
        from datetime import datetime, timezone
        return datetime.now(timezone.utc).isoformat()
