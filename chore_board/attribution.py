"""Pending attribution lifecycle."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Optional
from enum import Enum
import uuid


class AttributionState(Enum):
    PENDING = "pending"
    ATTRIBUTED = "attributed"
    DISMISSED = "dismissed"


@dataclass
class PendingAttribution:
    id: str
    task_uid: str
    task_title: str
    state: AttributionState = AttributionState.PENDING
    attributed_to: Optional[str] = None


class AttributionManager:
    """Manage pending attributions for completed tasks."""

    def __init__(self) -> None:
        self._attributions: dict[str, PendingAttribution] = {}

    def create_pending(self, task_uid: str, task_title: str) -> str:
        """Create a pending attribution entry. Returns the entry id."""
        aid = str(uuid.uuid4())
        entry = PendingAttribution(
            id=aid,
            task_uid=task_uid,
            task_title=task_title,
            state=AttributionState.PENDING,
        )
        self._attributions[aid] = entry
        return aid

    def resolve(self, attribution_id: str, participant_id: str) -> None:
        """Resolve a pending attribution (points awarded)."""
        entry = self._get_or_raise(attribution_id)
        if entry.state != AttributionState.PENDING:
            raise ValueError(f"Attribution '{attribution_id}' is not pending")
        entry.state = AttributionState.ATTRIBUTED
        entry.attributed_to = participant_id

    def dismiss(self, attribution_id: str) -> None:
        """Dismiss a pending attribution (no points)."""
        entry = self._get_or_raise(attribution_id)
        if entry.state != AttributionState.PENDING:
            raise ValueError(f"Attribution '{attribution_id}' is not pending")
        entry.state = AttributionState.DISMISSED

    def get_pending(self) -> list[PendingAttribution]:
        """Get all pending attributions."""
        return [e for e in self._attributions.values() if e.state == AttributionState.PENDING]

    def get_attribution(self, attribution_id: str) -> PendingAttribution:
        """Get a specific attribution entry."""
        return self._get_or_raise(attribution_id)

    def has_pending(self, task_uid: str) -> bool:
        """Check if a task has a pending attribution."""
        return any(
            e.task_uid == task_uid and e.state == AttributionState.PENDING
            for e in self._attributions.values()
        )

    def cleanup(self, attribution_id: str) -> None:
        """Remove an attribution entry (attributed or dismissed)."""
        if attribution_id in self._attributions:
            del self._attributions[attribution_id]

    def _get_or_raise(self, attribution_id: str) -> PendingAttribution:
        if attribution_id not in self._attributions:
            raise KeyError(f"Attribution '{attribution_id}' not found")
        return self._attributions[attribution_id]
